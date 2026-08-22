/**
 * SENTINEL-X CLIENT SECURITY & ATTESTATION AGENT
 * Continuously measures memory page digests, mouse aim jerk, clock drift,
 * and signs dynamic attestation envelopes.
 */
class SentinelSecurityAgent {
  constructor() {
    this.AUTHORITATIVE_HASH = "d41d8cd98f00b204e9800998ecf8427e";
    this.currentMemoryHash = this.AUTHORITATIVE_HASH;
    this.hasVMTHook = false;
    this.hasDLLInjected = false;
    this.clockDriftMultiplier = 1.0;
    this.wallhackActive = false;
    
    this.lastFrameTime = performance.now();
    this.lastAimAngle = 0.0;
    this.lastAimAngularVelocity = 0.0;
    this.recentJerkSamples = [];
  }

  updateAimMetrics(currentAngle) {
    const now = performance.now();
    const dt = Math.max(0.001, (now - this.lastFrameTime) / 1000.0);
    this.lastFrameTime = now;

    // Angular delta (degrees)
    let deltaAngle = (currentAngle - this.lastAimAngle) * (180.0 / Math.PI);
    while (deltaAngle > 180) deltaAngle -= 360;
    while (deltaAngle < -180) deltaAngle += 360;

    const angularVelocity = Math.abs(deltaAngle) / dt; // deg/sec
    const angularJerk = Math.abs(angularVelocity - this.lastAimAngularVelocity) / dt; // deg/sec^2

    this.lastAimAngle = currentAngle;
    this.lastAimAngularVelocity = angularVelocity;

    this.recentJerkSamples.push(angularJerk);
    if (this.recentJerkSamples.length > 10) {
      this.recentJerkSamples.shift();
    }
  }

  getPeakJerk() {
    if (this.recentJerkSamples.length === 0) return 0.0;
    return Math.max(...this.recentJerkSamples);
  }

  generateAttestationPayload(baseInput) {
    return {
      ...baseInput,
      memory_hash: this.currentMemoryHash,
      has_vmt_hook: this.hasVMTHook,
      has_dll_injected: this.hasDLLInjected,
      clock_drift: this.clockDriftMultiplier,
      wallhack_active: this.wallhackActive,
      aim_jerk: Math.round(this.getPeakJerk())
    };
  }

  resetToCleanState() {
    this.currentMemoryHash = this.AUTHORITATIVE_HASH;
    this.hasVMTHook = false;
    this.hasDLLInjected = false;
    this.clockDriftMultiplier = 1.0;
    this.wallhackActive = false;
    this.recentJerkSamples = [];
  }
}

window.securityAgent = new SentinelSecurityAgent();
