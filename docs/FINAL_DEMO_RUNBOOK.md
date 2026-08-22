# 🎬 Final Demo Runbook (90–120 Seconds)

## Demonstration Steps

1. **Zero-State Verification (0–15s):**
   - Open `http://127.0.0.1:8080/`. Point out `● AGENT ACTIVE (WAITING)`, `0 Active Sessions`, and Trust `—`.
2. **Game Launch & Attestation (15–35s):**
   - Click `Game Viewport`. The client initializes SDK, solves the 256-bit challenge nonce, and transitions the console to `● PROTECTED`.
3. **Telemetry & Dual Logs (35–55s):**
   - Show `Log A (Security Checks)` passing at millisecond latencies and `Log B (Engine Activity)` streaming real function calls.
4. **Controlled Attack Injection (55–75s):**
   - Trigger memory tamper in Developer Mode. Show immediate detection, trust drop, and transition to `SESSION QUARANTINED`.
5. **Autonomous Checkpoint Recovery (75–100s):**
   - Observe automatic rollback to last trusted Merkle checkpoint and HMAC re-attestation back to `● PROTECTED`.
6. **Evidence & Settings (100–120s):**
   - View structured evidence audit logs and show dynamic game registration in Settings.
