# 🛡️ SENTINEL-X: Zero-Trust Game Integrity Platform

> **"Don't Trust the Client. Verify the Session."**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Status: Operational](https://img.shields.io/badge/Status-Operational%20Prototype-00ff88.svg)]()
[![Platform: Cross-Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows%20%7C%20Linux%20%7C%20Web-00f0ff.svg)]()
[![Engine: 60Hz Authoritative](https://img.shields.io/badge/Engine-60Hz%20Authoritative%20WebSocket-a855f7.svg)]()

---

## 🌟 The Core Innovation: Autonomous Session Recovery

Traditional anti-cheat systems (BattlEye, Easy Anti-Cheat, Vanguard, Ricochet) operate under a **destructive detection paradigm**:
$$\text{Detect Injected Cheat} \longrightarrow \text{Permanent Ban / Match Disconnect}$$

When a cheat executes mid-match, the game state is contaminated, scores are corrupted, and the match is ruined for everyone.

### Sentinel-X introduces the Zero-Trust Continuous Verification Paradigm:
$$\text{Observe} \longrightarrow \text{Attest} \longrightarrow \text{Correlate Evidence} \longrightarrow \text{Calculate Dynamic Trust} \longrightarrow \text{Detect Compromise} \longrightarrow \text{Quarantine Session} \longrightarrow \text{Identify Last Verified Merkle Checkpoint} \longrightarrow \text{Authoritatively Rewind State} \longrightarrow \text{Cryptographic Re-Attestation} \longrightarrow \text{Restore Trusted Session}$$

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

## 🚀 Live Demo Walkthrough (For Hackathon Judges)

Open your browser to: **`http://127.0.0.1:8080/`**

1. **The Cyberpunk Arena (Top-Left):** Control your operator using `WASD` to move and `Mouse` to aim and fire lasers. Watch the 60 Hz authoritative server calculate bullet trajectories, obstacle bounces, and live enemy AI bots (`SENTINEL-ALPHA`, `SENTINEL-BRAVO`, `SENTINEL-GAMMA`).
2. **The Exploit Injection Suite (Top-Right):**
   - Toggle **`🚀 Speedhack 3.5×`**: Skews the local client clock delta.
   - Toggle **`🎯 Aimbot Micro-Snap`**: Locks angular aiming instantly to closest bot with 0 ms transition time (spikes angular jerk to $> 800^\circ/\text{s}^2$).
   - Toggle **`🧱 Memory Hash Tamper`**: Corrupts `.text` memory page hash signature.
   - Toggle **`👻 Wallhack (ESP)`**: Enables occluded raycast line-of-sight barrier penetration.
   - Toggle **`💉 VMT Trampoline Hook`**: Injects unverified memory hook pointer.
3. **The SOC Operations Dashboard (Bottom):**
   - Watch the **Session Trust Score** dial collapse in real time from **100% (TRUSTED)** down to **0% (COMPROMISED)**.
   - Observe the **`⚠️ SESSION COMPROMISED`** Quarantine banner freeze the player's malicious input stream.
   - Watch the **Autonomous Recovery Pipeline Stepper** advance through:
     `OBSERVE` $\longrightarrow$ `DEGRADED` $\longrightarrow$ `QUARANTINE` $\longrightarrow$ `REWIND` $\longrightarrow$ `RE-ATTEST` $\longrightarrow$ `RESTORED`
   - Click **`⚡ TRIGGER AUTONOMOUS RECOVERY`** to see the holographic ghost rollback animation rewind the player's authoritative position, execute the 256-bit challenge-response handshake, and restore the session to **100% TRUSTED** in $< 2$ milliseconds!

---

## 🔬 Mathematical & Architectural Model

### 1. Dynamic Trust Score Calculation
The continuous trust metric $T_s(t) \in [0.0, 1.0]$ is computed at 60 Hz:
$$T_s(t) = \max\left(0.0, \; T_s(t - \Delta t) \cdot e^{-\lambda \Delta t} + \alpha_{\text{good}} - \sum_{i} w_i \cdot \text{Penalty}_i(t)\right)$$

Where:
- $\lambda = 0.015$ (decay constant)
- $\alpha_{\text{good}} = 0.030$ (recovery bonus per verified clean frame)
- Penalty weights:
  - $w_{\text{memory\_hash}} = 0.60$
  - $w_{\text{vmt\_hook}} = 0.55$
  - $w_{\text{speedhack}} = 0.45$
  - $w_{\text{aimbot\_jerk}} = 0.35$
  - $w_{\text{wallhack\_esp}} = 0.35$

### 2. Merkle State Checkpoint Ring Buffer
Every 16.66 ms, the server constructs a SHA-256 Merkle tree of all entity states:
$$H_{\text{root}} = \text{MerkleRoot}\Big(\big\{ \text{Entity}_1, \text{Entity}_2, \dots, \text{Entity}_N, T_s \big\}\Big)$$
The buffer retains 600 verified snapshots (~10 seconds of gameplay) for instantaneous rollback.

### 3. Nonce Re-Attestation Handshake
Upon quarantine, the server generates an ephemeral 256-bit cryptographic challenge $N_{\text{challenge}}$:
$$R_{\text{proof}} = \text{HMAC-SHA256}\big(N_{\text{challenge}}, \; H_{\text{clean\_memory}}\big)$$
The session is restored only when $R_{\text{proof}} == R_{\text{expected}}$.

---

## 🛠️ Quick Start & Execution

```bash
# 1. Clone repository
git clone https://github.com/<your-username>/sentinel-x.git
cd sentinel-x

# 2. Launch with run script
chmod +x run.sh
./run.sh

# 3. Open browser at http://127.0.0.1:8080
```

---

## 📁 Repository Structure

```
SENTINEL-X/
├── docs/
│   ├── foundation-analysis.md   # Open-Source Anti-Cheat Reconnaissance Report
│   └── architecture.md          # Full System Design & Security Specification
├── server/
│   ├── server.py                # Integrated HTTP & WebSocket Server
│   ├── engine/
│   │   ├── game_server.py       # 60 Hz Authoritative Physics & AI Bot Simulation
│   │   ├── entity.py            # Player, Projectile, and Obstacle models
│   │   └── checkpoint.py        # Merkle Tree & 600-Frame Circular Ring Buffer
│   └── security/
│       ├── evidence.py          # Multi-Vector Evidence Correlation Engine
│       ├── trust.py             # Bayesian Dynamic Trust State Machine
│       └── recovery.py          # Autonomous Rollback & Nonce Re-Attestation
├── public/
│   ├── index.html               # Unified Cyberpunk Command Center UI
│   ├── css/
│   │   └── style.css            # Glassmorphic Dark-Mode Cyberpunk Design System
│   └── js/
│       ├── game_client.js       # 60 FPS HTML5 Canvas Arena Client
│       ├── security_agent.js    # Client Attestation & Memory Hash Monitor
│       ├── exploit_console.js   # Interactive Cheat Injection Suite
│       └── soc_dashboard.js     # Real-Time SOC Telemetry & Merkle Visualizer
├── run.sh                       # One-Click Launch Script
├── package.json
└── README.md
```

---

## 📜 License
MIT License. Created for the 2026 Global Hackathon by the Sentinel-X Core Team.
