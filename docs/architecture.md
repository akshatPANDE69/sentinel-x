# 🏛️ Architecture Specification

## Overview

Sentinel-X is a local-first, zero-trust game security platform and endpoint daemon. It replaces traditional client-side black-box anti-cheat simulations with an authoritative defense-in-depth model:

```
[ Protected Game (SDK) ]
           │ (REST / WebSocket Handshake)
           ▼
[ Sentinel-X Endpoint Agent ] <────> [ Compiled Rust Security Core ]
           │ (127.0.0.1 IPC)
           ▼
[ Local Authoritative Security Server ]
   ├── Multi-Vector Evidence Engine
   ├── Dynamic Bayesian Trust Engine
   ├── Policy Engine (ALLOW / MONITOR / QUARANTINE / RECOVER)
   └── Merkle Checkpoint Buffer (600 frames)
           │ (WebSocket Delta Streams)
           ▼
[ Localhost Console (Apple Liquid Glass UI) ]
```

## Subsystem Breakdown

1. **Rust Security Core (`agent/rust-core/`):**
   - High-performance, memory-safe routines for process enumeration, executable measurement, bounded telemetry ring buffers, and cryptographic challenge verification.
2. **Game Registry (`server/registry/` & `data/games/registry.json`):**
   - Persistent store maintaining authorized game identities, developer public keys, and SHA-256 binary baselines.
3. **Attestation Service (`server/security/attestation.py`):**
   - Generates unpredictable 256-bit challenge nonces and verifies HMAC-SHA256 measurement tokens.
4. **Server Authority Engine (`server/engine/`):**
   - Strictly authoritative physics validation ($\Delta x / \Delta t \le v_{\max}$). Client state divergence is clamped to allowable limits.
5. **Merkle Checkpoint Recovery (`server/engine/checkpoint.py`):**
   - Circular buffer recording full state hashes. Rewinds compromised state and completes re-attestation in $< 2$ ms.
