# Sentinel-X: System Architecture & Design Specification

**Project:** SENTINEL-X  
**Tagline:** *"Don't Trust the Client. Verify the Session."*  
**Date:** August 2026  
**Status:** Canonical Architectural Specification  

---

## 1. Architectural Philosophy & Zero-Trust Vision

Traditional anti-cheat architectures operate on a **Binary Trust / Ban Paradigm**:
```
[Client] ---> (Reports Inputs) ---> [Server]
    |
(Cheat Injected) ---> [Client Flagged] ---> [Account Banned / Match Terminated]
```
*Failure Modes:*
- Games are ruined for legitimate players when cheaters inject mid-match.
- False positives result in permanent account damage.
- Detection-to-ban latency (ban waves) leaves games compromised for hours or weeks.

**Sentinel-X introduces the Zero-Trust Continuous Verification & Autonomous Recovery Paradigm:**
```
+-----------------------------------------------------------------------------+
|                                SENTINEL-X                                   |
|                                                                             |
|   +--------------------+   +---------------------+   +------------------+   |
|   |  GAME CLIENT/SRV   |   |   SECURITY AGENT    |   | PLATFORM TELEM   |   |
|   |  (60Hz State Sync) |   |  (Memory/Hook Att)  |   | (Clock/OS Layer) |   |
|   +---------+----------+   +----------+----------+   +--------+---------+   |
|             |                         |                       |             |
|             +-------------------------+-----------------------+             |
|                                       |                                     |
|                                       v                                     |
|                             EVIDENCE ENGINE                                 |
|                                       |                                     |
|            +--------------------------+--------------------------+          |
|            |                          |                          |          |
|            v                          v                          v          |
|    INTEGRITY STREAM           BEHAVIORAL STREAM         SERVER VALIDATION   |
|    - Memory Page Hashes       - Aim Delta / Jerk        - Delta Sim Match   |
|    - Hook / DLL Checks        - Impossible Vectors      - Raycast Bounds    |
|    - Clock Drift Attestation  - Input Entropy / Burst   - Projectile Origin |
|            |                          |                          |          |
|            +--------------------------+--------------------------+          |
|                                       |                                     |
|                                       v                                     |
|                                 TRUST ENGINE                                |
|                                       |                                     |
|                     +-----------------+-----------------+                   |
|                     |                 |                 |                   |
|                     v                 v                 v                   |
|                  TRUSTED          DEGRADED         COMPROMISED              |
|               (1.00 - 0.85)     (0.84 - 0.50)       (< 0.50)                |
|                     |                 |                 |                   |
|                     |        [Shadow Validation]        |                   |
|                     |                                   v                   |
|                     |                            QUARANTINE ISOLATION       |
|                     |                                   |                   |
|                     |                                   v                   |
|                     |                        LAST TRUSTED CHECKPOINT        |
|                     |                        (Cryptographic Merkle Proof)   |
|                     |                                   |                   |
|                     |                                   v                   |
|                     |                           AUTHORITATIVE REWIND        |
|                     |                           (State Rollback Engine)     |
|                     |                                   |                   |
|                     |                                   v                   |
|                     |                         NONCE RE-ATTESTATION          |
|                     |                         (Dynamic Challenge Proof)     |
|                     |                                   |                   |
|                     +<----------------------------------+                   |
|                     |                                                       |
|                     v                                                       |
|               SESSION RESTORED                                              |
+-----------------------------------------------------------------------------+
```

---

## 2. Explicit Implementation Categorization

To guarantee scientific rigor, engineering clarity, and hackathon transparency:

### What We Are Reusing / Inspiring:
- **ECS (Entity-Component-System) Model:** Inspired by *Veloren* architecture (clean separation of Position, Velocity, Health, Weapon, and SecurityAttestation components).
- **Integrity Telemetry Model:** Inspired by *NoMercy* and *UltimateAntiCheat* (memory page checksumming, VMT hook verification, process integrity flags).
- **Challenge-Response Attestation:** Inspired by *Darken AntiCheat* (server-directed ephemeral nonces and response signatures).

### What We Are Building from Scratch (Proprietary Sentinel-X Core):
1. **The Multi-Vector Evidence Correlation Engine** (Correlating orthogonal telemetry streams with Bayesian weighting).
2. **The Dynamic Trust Engine** (Continuous float trust score $T_s \in [0.0, 1.0]$, decay dynamics, penalty matrices).
3. **The Cryptographic State Checkpoint Buffer** (Ring buffer of 600 frames / 10s with SHA-256 Merkle root proofs).
4. **The Autonomous Session Recovery Pipeline** (The hero innovation: Quarantine $\to$ Checkpoint Search $\to$ State Rewind $\to$ Ephemeral Nonce Challenge $\to$ Client Resync $\to$ Session Restoration).
5. **The Interactive Cyberpunk Arena Game** (Real-time authoritative 60 Hz multiplayer game in HTML5 Canvas/WebGL).
6. **The Exploit Injection Suite** (Interactive real-time attack console with 5 distinct cheat injection modules).
7. **The Glassmorphic SOC Operations Center** (Real-time cybernetic monitoring console with live telemetry graphs, trust meters, Merkle tree ledger, and audit timeline).

### What Is Real vs. What Is Simulated:
- **REAL:** 
  - Real-time 60 Hz WebSocket authoritative server simulation and client synchronization.
  - Real SHA-256 cryptographic hashing of client memory blocks and state buffers.
  - Real Merkle tree generation and verification for game checkpoints.
  - Real aim trajectory jerk calculation ($\Delta \theta / \Delta t^2$) and velocity vector physics validation.
  - Real state rewind and position/health/inventory rollback logic.
  - Real dynamic challenge-response cryptographic handshake.
  - Real live interactive cheat injection triggers altering runtime variables in the browser client.
- **SIMULATED (High-Fidelity Model):**
  - OS-level Windows kernel driver SSDT hooks are represented via a standardized integrity agent telemetry stream (simulating memory page tampering, DLL injection flags, and hook hooks in the security envelope) to ensure 100% cross-platform compatibility on macOS, Windows, Linux, and standard browsers without OS driver crashes.

---

## 3. Subsystem Breakdown

### 3.1 Authoritative Game Engine (`server/engine/`)
- **Tick Rate:** 60 Hz (16.66 ms tick step).
- **Physics Simulation:** 2D continuous collision detection, bounding box raycasting, projectile ballistic simulation.
- **Circular State Buffer:** 600 snapshot history ring buffer (`StateSnapshot[600]`), storing full entity states, input queues, and Merkle root hashes for the last 10 seconds.
- **Lag Compensation:** Historical rewind raycasting for hit verification.

### 3.2 Sentinel-X Client Security Agent (`agent/`)
- **Memory Integrity Monitor:** Periodically computes SHA-256 hashes of critical client memory segments (code text, constants, player struct).
- **Clock Drift Detector:** Compares `performance.now()`, `Date.now()`, and server timestamp delta to detect Speedhack tick-rate multipliers.
- **Input Jerk & Angular Velocity Analyzer:** Calculates first and second derivatives of mouse aim vector to detect non-human instantaneous micro-snaps (Aimbot).
- **Attestation Envelope Generator:** Signs each client input packet with a monotonic sequence ID, timestamp, telemetry digest, and session HMAC.

### 3.3 Multi-Vector Evidence Engine (`server/security/evidence.js`)
Aggregates three orthogonal evidence vectors:
1. **$V_{\text{integrity}}$ (Integrity Vector):**
   - Memory page hash mismatch ($\Delta H \neq 0$).
   - Detected DLL injection / hook signatures.
   - Clock tick skew $> 5\%$.
2. **$V_{\text{behavior}}$ (Behavioral Vector):**
   - Angular jerk $> \kappa_{\text{threshold}}$ ($> 180^\circ$ in $< 16$ ms).
   - Speed vector $> v_{\text{max\_allowed}}$.
   - Wall-occlusion line-of-sight violations (aiming at players through opaque map barriers).
3. **$V_{\text{server}}$ (Server-State Vector):**
   - Authoritative physics prediction discrepancy ($|p_{\text{client}} - p_{\text{server}}| > \epsilon$).
   - Impossible fire rate / weapon cooldown violations.

### 3.4 Dynamic Trust Engine (`server/security/trust.js`)
Calculates continuous trust score $T_s(t)$:
$$T_s(t) = \max\left(0.0, \; T_s(t - \Delta t) \cdot e^{-\lambda \Delta t} + \alpha_{\text{good}} - \sum_{i} w_i \cdot \text{Penalty}_i(t)\right)$$
- **Trust Levels:**
  - **`TRUSTED` ($T_s \ge 0.85$):** Normal high-performance gameplay; client predictions accepted.
  - **`DEGRADED` ($0.50 \le T_s < 0.85$):** Server enables strict authoritative overrides; increased attestation heartbeat frequency (10 Hz $\to$ 30 Hz); silent shadow verification.
  - **`COMPROMISED` ($T_s < 0.50$):** Immediate Quarantine Triggered!

### 3.5 Autonomous Session Recovery Engine (`server/security/recovery.js`)
When $T_s < 0.50$:
1. **Quarantine Isolation:** The client session is immediately tagged `QUARANTINED`. Client input packets are suppressed from impacting other players.
2. **Checkpoint Search:** The engine traverses the circular history buffer backwards to find the last verified checkpoint $C_{\text{trusted}}$ where $T_s \ge 0.85$ and Merkle hash verification succeeded.
3. **Authoritative State Rewind:** Server sets the player's canonical state back to $C_{\text{trusted}}$ (e.g. 1.8 seconds prior to exploit injection).
4. **Cryptographic Challenge-Response:** Server generates an ephemeral challenge nonce $N_{\text{challenge}}$ and requests re-attestation.
5. **Client State Reconstruction:** Client receives the rewind packet, clears any injected memory overrides, recomputes memory hash, and returns $R_{\text{proof}} = \text{HMAC}(N_{\text{challenge}}, H_{\text{clean}})$.
6. **Session Restoration:** Upon signature validation, the server resets $T_s = 1.0$, lifts the quarantine, and broadcasts session restoration to the arena.

### 3.6 Interactive Cheat Injection Suite (`src/exploit_console.js`)
Allows the demoer/judge to test 5 real-time exploit vectors:
1. **Speedhack (Clock Multiplier):** Accelerates local simulation delta by 3.5×.
2. **Aimbot (Instant Snap):** Locks cursor directly to closest enemy player angle with 0 ms transition time.
3. **Memory Tamper (Health/Ammo Freeze):** Overwrites local health byte to 9999 HP and locks ammo count.
4. **Wallhack (ESP / Occlusion Probe):** Renders enemy player skeletons through opaque map geometry.
5. **DLL / Hook Injection:** Simulates injecting an unverified module into the client process memory space.

### 3.7 Sentinel-X SOC Glassmorphic Dashboard (`public/soc/`)
- **Cyberpunk Dark-Mode UI:** Glowing neon accents (cyan, amber, crimson), glassmorphism frosted backdrop.
- **Live Telemetry Gauges:** Real-time Trust Score dial ($0–100\%$), Aim Jerk distribution, Memory Hash status.
- **Merkle Ledger Visualizer:** Interactive tree showing blocks, state hashes, and verification proofs.
- **Recovery State Machine Monitor:** Animated node graph highlighting `OBSERVE` $\to$ `DEGRADED` $\to$ `QUARANTINE` $\to$ `REWIND` $\to$ `RE-ATTEST` $\to$ `RESTORED`.
- **Live Event Audit Log:** Detailed chronological security event stream with timestamps and packet hex dumps.

---

## 4. Directory Structure & Technology Stack

```
SENTINEL-X/
├── docs/
│   ├── foundation-analysis.md
│   └── architecture.md
├── server/
│   ├── index.js               # Main HTTP & WebSocket Server
│   ├── engine/
│   │   ├── game_server.js     # 60 Hz Authoritative Physics & State Buffer
│   │   ├── entity.js          # Player, Projectile, and Obstacle models
│   │   └── checkpoint.js      # Merkle Proof & Ring Buffer Store
│   └── security/
│       ├── evidence.js        # Multi-Vector Evidence Correlation
│       ├── trust.js           # Dynamic Trust Score & State Machine
│       └── recovery.js        # Autonomous State Rewind & Re-Attestation
├── public/
│   ├── index.html             # Unified Split-View Portal (Game + Exploit + SOC)
│   ├── css/
│   │   ├── style.css          # Glassmorphic Cyberpunk Theme & Animations
│   │   └── soc.css            # Security Dashboard Components
│   └── js/
│       ├── game_client.js     # 60 FPS Canvas Game Client
│       ├── security_agent.js  # Client-side Attestation & Memory Hashing
│       ├── exploit_console.js # Interactive Cheat Injector
│       └── soc_dashboard.js   # Live Telemetry & Merkle Visualizer
├── package.json
└── README.md
```

---

## 5. Summary

Sentinel-X shifts the cybersecurity paradigm in gaming from **destructive disconnection** to **autonomous self-healing resilience**. By combining authoritative state snapshotting, continuous multi-vector attestation, and cryptographic rollback, Sentinel-X preserves match integrity without compromising player experience.
