# 🛡️ Security Model & Zero-Trust Verification

## Core Principle
> **"Don't Trust the Client. Verify the Session."**

## Threat Vectors & Defenses

1. **Binary Modification / In-Memory Patching:**
   - *Defense:* Initial SHA-256 disk measurement + continuous memory scanning. Mismatch triggers immediate quarantine.
2. **Speedhacks / Velocity Spoofing:**
   - *Defense:* Server-authoritative position validation ($\Delta x / \Delta t \le v_{\max}$). Illegal multipliers ($> 2.0$) are clamped to $1.0$ and flagged as `STATE_DIVERGENCE`.
3. **Aimbots / Angular Snapping:**
   - *Defense:* Behavioral trajectory jerk analysis ($\Delta^3 \theta / \Delta t^3 > 400^\circ/\text{s}^3$).
4. **Packet Sniffing / Custom Server Emulators:**
   - *Defense:* Polymorphic packet encryption with rotating per-packet nonces and HMAC tags.
5. **State Compromise Recovery:**
   - *Defense:* Autonomous rewind to last verified Merkle checkpoint ($T_s \ge 0.85$) + HMAC re-attestation handshake in $< 2$ ms.
