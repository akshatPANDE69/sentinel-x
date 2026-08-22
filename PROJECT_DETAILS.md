# 🛡️ SENTINEL-X: Project Overview & Architecture Reference

**Project:** SENTINEL-X  
**Tagline:** *"Don't Trust the Client. Verify the Session."*  
**Repository:** `https://github.com/akshatPANDE69/sentinel-x` (or local `/Users/akshat/Documents/ChatGPT/SENTINEL-X`)  
**License:** MIT  
**Platform Compatibility:** macOS (Apple Silicon / Intel), Windows (10/11), Linux, Modern Browsers  

---

## 1. Executive Summary

Sentinel-X is a next-generation game integrity platform that shifts cybersecurity from **destructive disconnection** to **autonomous self-healing resilience**.

Traditional anti-cheats (Vanguard, BattlEye, Easy Anti-Cheat) suffer from a critical flaw: when a cheat injects mid-match, the only recourse is to disconnect/ban the player, destroying the match for everyone.

**Sentinel-X solves this through Autonomous Session Recovery:**
1. Continuous Multi-Vector Attestation (Ring 0 Kernel Callbacks + Ring 3 Memory Hashes + Behavioral Aim Jerk + Server Simulation).
2. Dynamic Bayesian Trust Scoring ($T_s \in [0.0, 1.0]$).
3. Instant Quarantine Isolation upon compromise.
4. Cryptographic Merkle Checkpoint Rollback to the last clean game frame.
5. 256-bit Ephemeral Nonce Challenge-Response Handshake.
6. Seamless Session Restoration in $< 2$ milliseconds.

---

## 2. Technical Stack

- **Game Engine:** 60 Hz Authoritative Physics & State Buffer (Python 3.12 / aiohttp / WebSockets).
- **Client Frontend:** 60 FPS HTML5 Canvas Cyberpunk Arena, Web Audio API Sound Synthesizer, Glassmorphic CSS3.
- **Kernel Layer:** Windows KMDF/WDM C Driver (`sentinel_driver.c`) implementing `ObRegisterCallbacks`, `PsSetCreateThreadNotifyRoutine`, and `KeRegisterNmiCallback`.
- **Native SIMD Engine:** C++17 ARM NEON / AVX2 Vectorized Memory Scanner (`vector_scanner.cpp`) operating at 5.79 GB/s.
- **Cryptographic Core:** SHA-256 Merkle Tree ring buffer (600 frames = 10s history) and HMAC-SHA256 challenge verification.

---

## 3. How to Launch & Test

### On macOS / Linux:
```bash
./run.sh
```

### On Windows:
```cmd
run.bat
```

Open your browser to: **`http://127.0.0.1:8080/`**
