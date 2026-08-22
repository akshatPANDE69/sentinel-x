/**
 * SENTINEL-X SOC REAL-TIME TELEMETRY & MERKLE LEDGER DASHBOARD
 */
class SOCDashboard {
  constructor() {
    this.ws = null;
    this.connectWS();
  }

  connectWS() {
    const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
    this.ws = new WebSocket(`${proto}//${window.location.host}/ws/soc`);

    this.ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === "SOC_TELEMETRY") {
          this.updateTelemetry(msg);
        }
      } catch (err) {}
    };

    this.ws.onclose = () => {
      setTimeout(() => this.connectWS(), 1500);
    };
  }

  updateTelemetry(data) {
    const score = data.trust_score || 1.0;
    const state = data.trust_state || "TRUSTED";
    const isQuarantined = data.is_quarantined || false;

    // 1. Update Header Status Pill
    const pill = document.getElementById("headerStatusPill");
    const pillText = document.getElementById("headerStatusText");
    if (pill && pillText) {
      pill.className = `status-pill ${state.toLowerCase()}`;
      pillText.innerText = isQuarantined ? "QUARANTINED" : state;
    }

    // 2. Update Trust Gauge
    const dialBar = document.getElementById("trustDialBar");
    const dialVal = document.getElementById("trustDialValue");
    if (dialBar && dialVal) {
      const percentage = Math.round(score * 100);
      dialVal.innerText = `${percentage}%`;

      // 440 is the perimeter
      const offset = 440 - (440 * score);
      dialBar.style.strokeDashoffset = offset;

      if (score >= 0.85) {
        dialBar.style.stroke = "var(--neon-green)";
        dialVal.style.color = "var(--neon-green)";
      } else if (score >= 0.50) {
        dialBar.style.stroke = "var(--neon-amber)";
        dialVal.style.color = "var(--neon-amber)";
      } else {
        dialBar.style.stroke = "var(--neon-crimson)";
        dialVal.style.color = "var(--neon-crimson)";
      }
    }

    // 3. Update Subsystem Matrix
    const metrics = data.telemetry_metrics || {};
    document.getElementById("metricMemIntegrity").innerText = metrics.memory_intact ? "MATCH (SHA-256)" : "TAMPER DETECTED";
    document.getElementById("metricMemIntegrity").style.color = metrics.memory_intact ? "var(--neon-green)" : "var(--neon-crimson)";

    document.getElementById("metricAimJerk").innerText = `${metrics.aim_jerk || 0} deg/s²`;
    document.getElementById("metricAimJerk").style.color = (metrics.aim_jerk > 400) ? "var(--neon-crimson)" : "var(--text-main)";

    document.getElementById("metricClockDrift").innerText = `${metrics.clock_drift || 1.0}x Delta`;
    document.getElementById("metricClockDrift").style.color = (metrics.clock_drift > 1.3) ? "var(--neon-crimson)" : "var(--text-main)";

    document.getElementById("metricVMTHooks").innerText = metrics.has_vmt_hook ? "HOOK DETECTED" : "CLEAN (VMT)";
    document.getElementById("metricVMTHooks").style.color = metrics.has_vmt_hook ? "var(--neon-crimson)" : "var(--neon-green)";

    // 4. Update Stepper Nodes
    this.updateStepper(state, isQuarantined, data.recovery_active);

    // 5. Update Checkpoints List
    if (data.recent_checkpoints) {
      this.renderCheckpoints(data.recent_checkpoints);
    }
  }

  updateStepper(state, isQuarantined, recoveryActive) {
    const stepObserve = document.getElementById("step-observe");
    const stepDegraded = document.getElementById("step-degraded");
    const stepQuarantine = document.getElementById("step-quarantine");
    const stepRewind = document.getElementById("step-rewind");
    const stepReattest = document.getElementById("step-reattest");
    const stepRestored = document.getElementById("step-restored");

    [stepObserve, stepDegraded, stepQuarantine, stepRewind, stepReattest, stepRestored].forEach(s => {
      if (s) s.className = "step-node";
    });

    if (isQuarantined || state === "COMPROMISED") {
      stepObserve.className = "step-node completed";
      stepDegraded.className = "step-node completed";
      stepQuarantine.className = "step-node alert";
      stepRewind.className = "step-node active";
      stepReattest.className = "step-node";
      stepRestored.className = "step-node";
    } else if (state === "DEGRADED") {
      stepObserve.className = "step-node completed";
      stepDegraded.className = "step-node active";
    } else {
      stepObserve.className = "step-node active";
      stepRestored.className = "step-node completed";
    }
  }

  renderCheckpoints(checkpoints) {
    const list = document.getElementById("checkpointList");
    if (!list) return;

    list.innerHTML = "";
    checkpoints.slice(0, 6).forEach(cp => {
      const card = document.createElement("div");
      card.className = `checkpoint-card ${cp.is_verified ? "verified" : "compromised"}`;
      card.innerHTML = `
        <div>
          <span>FRAME #${cp.frame_id}</span>
          <span style="color: var(--text-muted); margin-left: 8px;">${cp.player_count} Entities</span>
        </div>
        <div class="merkle-hash">${cp.merkle_root.substring(0, 14)}...</div>
        <div><span class="log-tag ${cp.is_verified ? "clean" : "alert"}">${cp.is_verified ? "VERIFIED" : "TAMPERED"}</span></div>
      `;
      list.appendChild(card);
    });
  }

  logEvent(tag, tagType, message) {
    const logEl = document.getElementById("socAuditLog");
    if (!logEl) return;

    const timeStr = new Date().toLocaleTimeString().split(" ")[0];
    const entry = document.createElement("div");
    entry.className = "log-entry";
    entry.innerHTML = `
      <span class="log-time">${timeStr}</span>
      <span class="log-tag ${tagType}">${tag}</span>
      <span class="log-msg">${message}</span>
    `;

    logEl.insertBefore(entry, logEl.firstChild);
    if (logEl.children.length > 50) {
      logEl.removeChild(logEl.lastChild);
    }
  }
}

window.socDashboard = new SOCDashboard();
