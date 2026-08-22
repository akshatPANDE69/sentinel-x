# 🛡️ SENTINEL-X: Zero-Trust Game Security Agent & Local Console

> **"Don't Trust the Client. Verify the Session."**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Status: Production Prototype](https://img.shields.io/badge/Status-Production%20Prototype-34c759.svg)]()
[![Core: Rust 1.98](https://img.shields.io/badge/Core-Rust%201.98-orange.svg)]()
[![Platform: macOS & Windows](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows%20%7C%20Linux-0a84ff.svg)]()
[![Design: Apple Liquid Glass](https://img.shields.io/badge/Design-Apple%20Liquid%20Glass-bf5af2.svg)]()

---

## ⚡ Quick Start

### macOS / Linux:
```bash
# 1. Install dependencies & build Rust Security Core:
./install.sh

# 2. Start the Security Agent & Local Authoritative Server:
./run_agent.sh
```

### Windows:
```powershell
# In PowerShell:
.\install.ps1

# Start the agent:
.\run_agent.bat
```

### Open Local Security Console:
- **HTTP Console:** [http://127.0.0.1:8080/](http://127.0.0.1:8080/)
- **HTTPS Console:** [https://127.0.0.1:8443/](https://127.0.0.1:8443/)

---

## 🌟 Product Philosophy & Real Architecture

Sentinel-X is **NOT** a black-box client simulation. It is a **Zero-Trust Game Integrity & Endpoint Security Platform** where game developers explicitly integrate the **Sentinel-X SDK**:

```
GAME DEVELOPER (Registers Game Hash & Public Key in data/games/registry.json)
        ↓
GAME PROCESS LAUNCHES & INITIALIZES SDK
        ↓
AGENT DISCOVERS PROCESS VIA OS APIS & RUST CORE (PID, Path, SHA-256)
        ↓
CRYPTOGRAPHIC ATTESTATION (256-bit Nonce Challenge + HMAC-SHA256 Bundle)
        ↓
SESSION STATE TRANSITIONS TO: ● PROTECTED
        ↓
CONTINUOUS SECURITY CHECKS (Log A) & LIVE ENGINE ACTIVITY (Log B)
        ↓
DEFENSE-IN-DEPTH SERVER AUTHORITY (Server clamps illegal velocity divergence)
        ↓
IF ATTACK: QUARANTINE → AUTONOMOUS REWIND TO MERKLE CHECKPOINT → RESTORE
```

---

## 🔬 Reality & Verification Matrix (21/21 Tests Passed)

| Component | Implementation | Runtime Path | Verification Status |
| :--- | :---: | :--- | :---: |
| **Rust Security Core** | Rust 1.98 | `agent/rust-core/target/release/sentinel-core` | **`VERIFIED_RUNTIME`** |
| **Process Discovery** | Python / Rust | `agent/process_discovery.py` | **`VERIFIED_RUNTIME`** |
| **Persistent Game Registry** | Python / JSON | `data/games/registry.json` | **`VERIFIED_RUNTIME`** |
| **Sentinel-X Game SDK** | Python / JS | `sdk/python/`, `sdk/js/` | **`VERIFIED_RUNTIME`** |
| **Attestation Nonce Engine** | Python / Rust | `server/security/attestation.py` | **`VERIFIED_RUNTIME`** |
| **Server Authority Physics** | Python | `server/engine/game_server.py` | **`VERIFIED_RUNTIME`** |
| **Lockless SPSC Queue** | C++17 | `agent/native/spsc_benchmark` | **`BENCHMARK (15.2M ops/s)`** |
| **Vectorized SIMD Scanner** | C++17 / NEON | `agent/native/vector_scanner` | **`BENCHMARK (7.41 GB/s)`** |
| **Merkle Checkpoint Recovery**| Python | `server/engine/checkpoint.py` | **`VERIFIED_RUNTIME (0.37 ms)`** |
| **Windows Kernel Driver** | C (KMDF) | `agent/kernel/sentinel_driver.c` | **`SOURCE_ONLY (Windows)`** |

---

## 📚 Complete Documentation Index

- [🏛️ Architecture Specification](docs/ARCHITECTURE.md)
- [📦 Installation Guide](docs/INSTALLATION.md)
- [🎮 Game Registration & Enrollment](docs/GAME_REGISTRATION.md)
- [🛡️ Security Model & Zero-Trust Verification](docs/SECURITY_MODEL.md)
- [🤖 Endpoint Security Agent](docs/AGENT.md)
- [🦀 Rust Security Core](docs/RUST_CORE.md)
- [📡 Dual Live Telemetry & Bounded Streams](docs/TELEMETRY.md)
- [🔌 Local REST & WebSocket API](docs/API.md)
- [💻 Developer Setup Guide](docs/DEVELOPMENT.md)
- [🧪 Test Suite & Methodology](docs/TESTING.md)
- [🌍 Platform Support Matrix](docs/PLATFORM_SUPPORT.md)
- [🪟 Windows Driver Specification](docs/WINDOWS_DRIVER.md)
- [🔍 Honest Security Reality & Limits](docs/SECURITY_REALITY.md)
- [📋 Final Engineering Reality Audit](docs/FINAL_ENGINEERING_AUDIT.md)
- [🎬 Final Demo Runbook (90–120s)](docs/FINAL_DEMO_RUNBOOK.md)
- [📜 Changelog](docs/CHANGELOG.md)
- [📓 Engineering Journal](docs/ENGINEERING_LOG.md)

---

## 🎬 90-Second Demonstration Runbook

1. **Clean Start:** Open `http://127.0.0.1:8080/`. Notice zero-state (*"Waiting for protected game..."*).
2. **Launch Game:** Switch to `Game Viewport`. The client solves the 256-bit challenge nonce and the console animates to `● PROTECTED`.
3. **Live Logs:** Watch `Log A (Security Checks)` and `Log B (Engine Activity)` streaming real function calls in real time.
4. **Simulate Attack:** In Developer Mode, inject a memory tamper. Watch Bayesian trust drop and session isolate to `QUARANTINED`.
5. **Autonomous Recovery:** Observe state rewind to the last verified Merkle checkpoint and HMAC re-attestation back to `● PROTECTED`.
