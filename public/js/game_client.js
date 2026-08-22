/**
 * SENTINEL-X 60 FPS CYBERPUNK ARENA GAME CLIENT
 * Features smooth interpolation, client-side prediction, particle engines,
 * aimbot mechanics, and the Holographic Rollback Rewind visualizer.
 */
class CyberpunkGameClient {
  constructor() {
    this.canvas = document.getElementById("gameCanvas");
    this.ctx = this.canvas.getContext("2d");
    this.width = 1200;
    this.height = 760;

    this.ws = null;
    this.playerId = null;
    this.myPlayer = null;
    this.players = [];
    this.projectiles = [];
    this.obstacles = [];

    this.keys = {};
    this.mouse = { x: 0, y: 0, down: false };
    this.particles = [];
    this.rollbackGhostTrail = [];
    this.isQuarantined = false;

    this.initCanvas();
    this.initInputListeners();
    this.connectWS();
    this.startLoop();
  }

  initCanvas() {
    this.canvas.width = this.width;
    this.canvas.height = this.height;
  }

  connectWS() {
    const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
    this.ws = new WebSocket(`${proto}//${window.location.host}/ws/game`);

    this.ws.onopen = () => {
      if (window.socDashboard) {
        window.socDashboard.logEvent("HANDSHAKE", "clean", "Connected to Sentinel-X Authoritative Game Server");
      }
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "HANDSHAKE_ACK") {
          this.playerId = data.player_id;
          this.obstacles = data.arena.obstacles || [];
        } else if (data.type === "WORLD_STATE") {
          this.players = data.players || [];
          this.projectiles = data.projectiles || [];
          this.myPlayer = this.players.find(p => p.id === this.playerId);
          
          if (this.myPlayer) {
            this.isQuarantined = this.myPlayer.is_quarantined;
            const banner = document.getElementById("quarantineBanner");
            if (banner) {
              banner.style.display = this.isQuarantined ? "block" : "none";
            }
            // Update HUD
            const hpFill = document.getElementById("playerHealthBar");
            const hpText = document.getElementById("playerHealthText");
            const scText = document.getElementById("playerScoreText");
            if (hpFill) hpFill.style.width = `${this.myPlayer.health}%`;
            if (hpText) hpText.innerText = `${this.myPlayer.health} HP`;
            if (scText) scText.innerText = `SCORE: ${this.myPlayer.score}`;
          }
        } else if (data.type === "RECOVERY_RESULT") {
          if (data.payload && data.payload.success) {
            this.triggerRollbackAnimation();
            if (window.socDashboard) {
              window.socDashboard.logEvent("RECOVERY_ACK", "recovery", `Session restored to Checkpoint #${data.payload.checkpoint_frame} in ${data.payload.elapsed_ms}ms`);
            }
          }
        }
      } catch (err) {}
    };

    this.ws.onclose = () => {
      setTimeout(() => this.connectWS(), 1500);
    };
  }

  initInputListeners() {
    window.addEventListener("keydown", (e) => {
      this.keys[e.key.toLowerCase()] = true;
    });
    window.addEventListener("keyup", (e) => {
      this.keys[e.key.toLowerCase()] = false;
    });

    this.canvas.addEventListener("mousemove", (e) => {
      const rect = this.canvas.getBoundingClientRect();
      const scaleX = this.canvas.width / rect.width;
      const scaleY = this.canvas.height / rect.height;
      this.mouse.x = (e.clientX - rect.left) * scaleX;
      this.mouse.y = (e.clientY - rect.top) * scaleY;
    });

    this.canvas.addEventListener("mousedown", () => {
      this.mouse.down = true;
    });
    window.addEventListener("mouseup", () => {
      this.mouse.down = false;
    });
  }

  startLoop() {
    const loop = () => {
      this.update();
      this.render();
      requestAnimationFrame(loop);
    };
    requestAnimationFrame(loop);
  }

  update() {
    if (!this.myPlayer) return;

    let dx = 0;
    let dy = 0;
    if (this.keys["w"] || this.keys["arrowup"]) dy -= 1;
    if (this.keys["s"] || this.keys["arrowdown"]) dy += 1;
    if (this.keys["a"] || this.keys["arrowleft"]) dx -= 1;
    if (this.keys["d"] || this.keys["arrowright"]) dx += 1;

    // Normalize
    const len = Math.hypot(dx, dy);
    if (len > 0) {
      dx /= len;
      dy /= len;
    }

    // Aim Angle
    let aimAngle = Math.atan2(this.mouse.y - this.myPlayer.y, this.mouse.x - this.myPlayer.x);

    // Aimbot Exploit Logic: Instant snap to closest bot
    if (window.exploitConsole && window.exploitConsole.activeExploits.aimbot) {
      let closestBot = null;
      let closestDist = 99999;
      this.players.forEach(p => {
        if (p.id !== this.playerId && !p.is_quarantined) {
          const dist = Math.hypot(p.x - this.myPlayer.x, p.y - this.myPlayer.y);
          if (dist < closestDist) {
            closestDist = dist;
            closestBot = p;
          }
        }
      });
      if (closestBot) {
        aimAngle = Math.atan2(closestBot.y - this.myPlayer.y, closestBot.x - this.myPlayer.x);
        this.mouse.x = closestBot.x;
        this.mouse.y = closestBot.y;
      }
    }

    // Update Security Agent
    window.securityAgent.updateAimMetrics(aimAngle);

    // Send Input Packet
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const baseInput = {
        dx,
        dy,
        angle: aimAngle,
        shoot: this.mouse.down
      };
      const signedPacket = window.securityAgent.generateAttestationPayload(baseInput);

      this.ws.send(JSON.stringify({
        type: "PLAYER_INPUT",
        payload: signedPacket
      }));
    }

    // Update Particles
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.x += p.vx;
      p.y += p.vy;
      p.life -= p.decay;
      if (p.life <= 0) {
        this.particles.splice(i, 1);
      }
    }
  }

  triggerRollbackAnimation() {
    if (!this.myPlayer) return;
    // Create rewind holographic ghost pulses
    for (let i = 0; i < 8; i++) {
      this.rollbackGhostTrail.push({
        x: this.myPlayer.x + (Math.random() - 0.5) * 80,
        y: this.myPlayer.y + (Math.random() - 0.5) * 80,
        alpha: 0.9,
        radius: this.myPlayer.radius * (1.2 + i * 0.2)
      });
    }
    // Spawn blue recovery sparkles
    for (let j = 0; j < 35; j++) {
      const ang = Math.random() * Math.PI * 2;
      const spd = Math.random() * 6 + 2;
      this.particles.push({
        x: this.myPlayer.x,
        y: this.myPlayer.y,
        vx: Math.cos(ang) * spd,
        vy: Math.sin(ang) * spd,
        color: "#00f0ff",
        radius: Math.random() * 4 + 2,
        life: 1.0,
        decay: 0.02
      });
    }
  }

  render() {
    this.ctx.clearRect(0, 0, this.width, this.height);

    // 1. Grid lines
    this.ctx.strokeStyle = "rgba(0, 240, 255, 0.04)";
    this.ctx.lineWidth = 1;
    for (let x = 0; x < this.width; x += 40) {
      this.ctx.beginPath();
      this.ctx.moveTo(x, 0);
      this.ctx.lineTo(x, this.height);
      this.ctx.stroke();
    }
    for (let y = 0; y < this.height; y += 40) {
      this.ctx.beginPath();
      this.ctx.moveTo(0, y);
      this.ctx.lineTo(this.width, y);
      this.ctx.stroke();
    }

    // 2. Obstacles
    this.obstacles.forEach(obs => {
      this.ctx.fillStyle = obs.color || "#1e293b";
      this.ctx.strokeStyle = "rgba(0, 240, 255, 0.2)";
      this.ctx.lineWidth = 2;
      this.ctx.fillRect(obs.x, obs.y, obs.w, obs.h);
      this.ctx.strokeRect(obs.x, obs.y, obs.w, obs.h);
    });

    // 3. Wallhack ESP skeleton overlay if enabled
    if (window.exploitConsole && window.exploitConsole.activeExploits.wallhack && this.myPlayer) {
      this.players.forEach(p => {
        if (p.id !== this.playerId) {
          this.ctx.strokeStyle = "rgba(255, 0, 85, 0.8)";
          this.ctx.setLineDash([4, 4]);
          this.ctx.beginPath();
          this.ctx.moveTo(this.myPlayer.x, this.myPlayer.y);
          this.ctx.lineTo(p.x, p.y);
          this.ctx.stroke();
          this.ctx.setLineDash([]);

          // ESP Bounding box
          this.ctx.strokeStyle = "#ff0055";
          this.ctx.strokeRect(p.x - 22, p.y - 22, 44, 44);
          this.ctx.fillStyle = "#ff0055";
          this.ctx.font = "10px monospace";
          this.ctx.fillText(`${p.name} [${p.health}HP]`, p.x - 30, p.y - 26);
        }
      });
    }

    // 4. Projectiles
    this.projectiles.forEach(proj => {
      this.ctx.save();
      this.ctx.fillStyle = proj.color || "#00f0ff";
      this.ctx.shadowColor = proj.color || "#00f0ff";
      this.ctx.shadowBlur = 12;
      this.ctx.beginPath();
      this.ctx.arc(proj.x, proj.y, proj.radius, 0, Math.PI * 2);
      this.ctx.fill();
      this.ctx.restore();
    });

    // 5. Rollback Ghost Trail
    for (let k = this.rollbackGhostTrail.length - 1; k >= 0; k--) {
      const g = this.rollbackGhostTrail[k];
      this.ctx.strokeStyle = `rgba(0, 240, 255, ${g.alpha})`;
      this.ctx.lineWidth = 3;
      this.ctx.beginPath();
      this.ctx.arc(g.x, g.y, g.radius, 0, Math.PI * 2);
      this.ctx.stroke();
      g.alpha -= 0.03;
      if (g.alpha <= 0) {
        this.rollbackGhostTrail.splice(k, 1);
      }
    }

    // 6. Players
    this.players.forEach(p => {
      this.ctx.save();
      this.ctx.translate(p.x, p.y);

      // Player circle
      this.ctx.fillStyle = p.is_quarantined ? "#ff0055" : (p.color || "#00ffcc");
      this.ctx.shadowColor = p.is_quarantined ? "#ff0055" : (p.color || "#00ffcc");
      this.ctx.shadowBlur = 14;
      this.ctx.beginPath();
      this.ctx.arc(0, 0, p.radius, 0, Math.PI * 2);
      this.ctx.fill();

      // Gun direction pointer
      this.ctx.rotate(p.angle);
      this.ctx.fillStyle = "#fff";
      this.ctx.fillRect(p.radius - 2, -3, 10, 6);
      this.ctx.restore();

      // Name & Mini Health bar
      this.ctx.font = "10px monospace";
      this.ctx.fillStyle = "#94a3b8";
      this.ctx.textAlign = "center";
      this.ctx.fillText(p.name, p.x, p.y - p.radius - 8);

      // Mini Health Bar
      this.ctx.fillStyle = "rgba(0,0,0,0.6)";
      this.ctx.fillRect(p.x - 16, p.y - p.radius - 6, 32, 4);
      this.ctx.fillStyle = p.health > 40 ? "#00ff88" : "#ff0055";
      this.ctx.fillRect(p.x - 16, p.y - p.radius - 6, 32 * (p.health / 100), 4);
    });

    // 7. Particles
    this.particles.forEach(p => {
      this.ctx.fillStyle = p.color;
      this.ctx.globalAlpha = Math.max(0, p.life);
      this.ctx.beginPath();
      this.ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      this.ctx.fill();
      this.ctx.globalAlpha = 1.0;
    });
  }
}

window.gameClient = new CyberpunkGameClient();
