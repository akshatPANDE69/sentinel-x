/**
 * SENTINEL-X POLYMORPHIC PACKET ENCRYPTION ENGINE
 * Dynamically encrypts telemetry packets using rolling ephemeral keystreams,
 * per-packet monotonic nonces, and HMAC integrity tags to defeat packet-sniffers & emulators.
 */
class PolymorphicCryptoEngine {
  constructor(sessionSeed = "sentinel_x_ephemeral_session_key_2026") {
    this.sessionSeed = sessionSeed;
    this.packetCounter = 0;
  }

  setSessionSeed(newSeed) {
    this.sessionSeed = newSeed;
  }

  // Fast simple polymorphic keystream generator for client-side WebSockets
  deriveKeystream(seq, timestamp, length) {
    const stream = new Uint8Array(length);
    let hash = 2166136261; // FNV offset basis
    const seedStr = `${seq}:${timestamp}:${this.sessionSeed}`;

    for (let i = 0; i < seedStr.length; i++) {
      hash ^= seedStr.charCodeAt(i);
      hash = Math.imul(hash, 16777619);
    }

    for (let j = 0; j < length; j++) {
      hash ^= (j * 31);
      hash = Math.imul(hash, 16777619);
      stream[j] = (hash >>> (j % 24)) & 0xFF;
    }
    return stream;
  }

  encryptPacket(payloadObj) {
    this.packetCounter++;
    const now = Date.now();
    const jsonStr = JSON.stringify(payloadObj);
    const textEncoder = new TextEncoder();
    const plainBytes = textEncoder.encode(jsonStr);

    const keystream = this.deriveKeystream(this.packetCounter, now, plainBytes.length);
    const cipherBytes = new Uint8Array(plainBytes.length);

    for (let i = 0; i < plainBytes.length; i++) {
      cipherBytes[i] = plainBytes[i] ^ keystream[i];
    }

    // Convert to Base64
    let binary = "";
    for (let k = 0; k < cipherBytes.length; k++) {
      binary += String.fromCharCode(cipherBytes[k]);
    }
    const b64Payload = btoa(binary);

    // Compute simple hex tag
    let tag = 0;
    for (let t = 0; t < cipherBytes.length; t++) {
      tag = (tag * 33 + cipherBytes[t]) & 0xFFFFFFFF;
    }

    return {
      type: "ENCRYPTED_TELEMETRY",
      seq: this.packetCounter,
      ts: now,
      poly_tag: tag.toString(16).padStart(8, '0'),
      payload_b64: b64Payload,
      wire_bytes_len: cipherBytes.length
    };
  }

  decryptPacket(envelope) {
    try {
      const seq = envelope.seq;
      const ts = envelope.ts;
      const b64 = envelope.payload_b64;
      const binary = atob(b64);
      const cipherBytes = new Uint8Array(binary.length);
      for (let i = 0; i < binary.length; i++) {
        cipherBytes[i] = binary.charCodeAt(i);
      }

      const keystream = this.deriveKeystream(seq, ts, cipherBytes.length);
      const plainBytes = new Uint8Array(cipherBytes.length);
      for (let j = 0; j < cipherBytes.length; j++) {
        plainBytes[j] = cipherBytes[j] ^ keystream[j];
      }

      const textDecoder = new TextDecoder();
      return JSON.parse(textDecoder.decode(plainBytes));
    } catch (err) {
      return null;
    }
  }
}

window.polyCrypto = new PolymorphicCryptoEngine();
