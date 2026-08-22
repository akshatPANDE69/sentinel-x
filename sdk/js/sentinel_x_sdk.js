/**
 * Sentinel-X Game Protection SDK (JavaScript).
 * Client runtime bridge for web and hybrid game clients.
 */
class SentinelXGameSDK {
  constructor() {
    this.gameId = "sx-arena";
    this.sessionId = null;
    this.sessionKey = null;
    this.isAttested = false;
    this.heartbeatSeq = 0;
    this.heartbeatInterval = null;
  }

  async initialize(config = {}) {
    this.gameId = config.gameId || "sx-arena";
    this.serverUrl = window.location.origin;
    return true;
  }

  async registerSession(processId = 4420) {
    try {
      const res = await fetch(`${this.serverUrl}/api/sessions/create`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ game_id: this.gameId, process_id: processId })
      });
      const data = await res.json();
      if (!data.success) return { success: false, error: data.error };

      this.sessionId = data.session.session_id;
      this.sessionKey = data.session_key;
      const nonce = data.challenge.nonce;

      // Attest session
      return await this.attest(nonce);
    } catch (err) {
      return { success: false, error: err.message };
    }
  }

  async attest(nonce) {
    if (!this.sessionId || !this.sessionKey) {
      return { success: false, error: "NO_SESSION" };
    }

    const exeHash = "d41d8cd98f00b204e9800998ecf8427e";
    const platformStr = "WebBrowser_Wasm";
    const agentVer = "1.0.0";

    // Simple HMAC in JS
    const canonical = `${this.sessionId}:${this.gameId}:${nonce}:${exeHash}:${platformStr}:${agentVer}`;
    const sig = await this._hmacSha256(this.sessionKey, canonical);

    const res = await fetch(`${this.serverUrl}/api/attest/verify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: this.sessionId,
        measurement_bundle: {
          executable_hash: exeHash,
          platform: platformStr,
          agent_version: agentVer
        },
        signature: sig
      })
    });

    const data = await res.json();
    if (data.success) {
      this.isAttested = true;
      this.startHeartbeats();
      return { success: true, sessionId: this.sessionId };
    }
    return { success: false, error: data.error };
  }

  startHeartbeats() {
    if (this.heartbeatInterval) clearInterval(this.heartbeatInterval);
    this.heartbeatInterval = setInterval(() => this.sendHeartbeat(), 1500);
  }

  async sendHeartbeat() {
    if (!this.sessionId) return;
    this.heartbeatSeq++;
    try {
      await fetch(`${this.serverUrl}/api/sessions/heartbeat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: this.sessionId,
          seq_id: this.heartbeatSeq,
          integrity_digest: `hb_${this.heartbeatSeq}_ok`
        })
      });
    } catch (err) {}
  }

  async _hmacSha256(keyStr, msgStr) {
    const enc = new TextEncoder();
    const key = await crypto.subtle.importKey(
      "raw", enc.encode(keyStr),
      { name: "HMAC", hash: "SHA-256" },
      false, ["sign"]
    );
    const signature = await crypto.subtle.sign("HMAC", key, enc.encode(msgStr));
    return Array.from(new Uint8Array(signature)).map(b => b.toString(16).padStart(2, '0')).join('');
  }

  shutdown() {
    if (this.heartbeatInterval) clearInterval(this.heartbeatInterval);
    this.sessionId = null;
    this.sessionKey = null;
    this.isAttested = false;
  }
}

window.sentinelSDK = new SentinelXGameSDK();
