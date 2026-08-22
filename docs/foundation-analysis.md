# Sentinel-X: Foundation Analysis & Reconnaissance Report

**Project:** SENTINEL-X  
**Tagline:** *"Don't Trust the Client. Verify the Session."*  
**Date:** August 2026  
**Author:** Sentinel-X Systems Architecture & Security Engineering Team  

---

## 1. Executive Summary

Sentinel-X is a zero-trust game integrity platform built around **Continuous Multi-Vector Attestation** and **Autonomous Session Recovery**. 

Before building, we surveyed industry open-source foundations across two major domains:
1. **Multiplayer Game & Network Foundations** (e.g., *Veloren*)
2. **Open-Source Anti-Cheat Systems** (e.g., *NoMercy Anti-Cheat*, *UltimateAntiCheat*, *Darken AntiCheat*)

This document presents our architectural, licensing, technical, and feasibility evaluation of each candidate against our 4–5 hour hackathon delivery window.

---

## 2. Candidate Evaluation Matrix

| Candidate | Primary Purpose | Language | License | Key Strengths | Critical Issues / Bottlenecks | Hackathon Feasibility | Subsystem Decision |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| **Veloren** | Open-source multiplayer voxel RPG | Rust | **GPL-3.0** | Authoritative ECS networking, client-side prediction, rich world state | Strict viral copyleft; massive compile time (15–30+ min from clean build); tens of thousands of lines; hard to hack custom rollback in 4 hours | 🔴 Low | **INSPIRE** (Adopt ECS/snapshot concepts; avoid code/license) |
| **NoMercy Anti-Cheat** | Kernel-level anti-cheat driver & monitor | C / C++ | **MIT** | Kernel SSDT hooks, memory scanner, thread hijacking & macro detection | Windows kernel driver requires test-signing mode / certificates; cannot run on macOS or standard browser/cross-platform demo setups; high crash risk | 🟡 Medium | **INSPIRE** (Model memory hash & integrity verification telemetry) |
| **UltimateAntiCheat (AlSch092)** | Usermode anti-cheat security reference | C++ | **Open Source (Educational)** | Page Guard protection, VMT hook detection, thread context validation | Pure Win32 usermode APIs (`VirtualProtect`, `Toolhelp32`); hard to embed in portable live demo without Windows VM | 🟡 Medium | **INSPIRE / REFERENCE** (Adopt memory page integrity & challenge tokens) |
| **Darken AntiCheat** | Server-orchestrated anti-cheat monitor | C++ | **Open Source** | Server-client challenge/response heartbeats | Monolithic driver reliance; rigid protocol | 🟡 Medium | **INSPIRE** (Adopt dynamic challenge-response attestation loop) |
| **Sentinel-X Custom Hybrid Stack** | Authoritative Multiplayer Engine + Cross-Layer Security SOC | Node.js / TypeScript / WebGL Canvas / WebSockets + Cryptographic Engine | **MIT** | Instant cross-platform execution (macOS, Windows, Linux, Web); 60 FPS real-time multiplayer arena; live glassmorphic SOC dashboard; 100% reliable interactive cheat injection & rollback demo | Zero external compilation blockers; full end-to-end control over game state, Merkle proof ledger, and recovery engine | 🟢 **MAXIMUM (Recommended)** | **BUILD PROPRIETARY SENTINEL-X CORE** |

---

## 3. Detailed Candidate Analysis

### Candidate 1: Veloren
- **Purpose:** Full-featured open-source multiplayer voxel game with client-server networking.
- **Language:** Rust
- **License:** GNU General Public License v3.0 (GPL-3.0).
- **Useful Components:** Entity-Component-System (ECS) architecture, state delta interpolation, client-side input prediction.
- **Problems:** 
  1. **License Incompatibility:** GPL-3.0 is a strong copyleft license that requires any derivative work to be GPL-3.0, restricting proprietary or flexible hackathon distribution.
  2. **Compile-Time Overhead:** Veloren has over 200+ crate dependencies and takes 20+ minutes to compile from scratch, consuming immense RAM and CPU.
  3. **Integration Friction:** Slicing out the networking and rendering loops to hook up a custom Merkle checkpoint and state recovery engine in 4 hours would risk catastrophic compile and runtime bugs during the live demo.
- **Decision:** **INSPIRE ONLY**. We borrow its state-snapshotting and client-prediction models, but avoid its massive Rust codebase and GPL-3.0 restrictions.

---

### Candidate 2: NoMercy Anti-Cheat
- **Purpose:** Open-source kernel-mode anti-cheat for online games.
- **Language:** C / C++
- **License:** MIT License.
- **Useful Components:** Memory page hashing algorithms, hook detection patterns, process handle access prevention.
- **Problems:**
  1. **Platform Lock:** Requires a Windows kernel driver (`.sys`) running in a Windows environment with driver signing disabled or test-signing certificates.
  2. **Demo Fragility:** Kernel drivers that detect injection by intercepting system calls risk Blue Screens of Death (BSOD) during live hackathon demos.
  3. **Zero Recovery:** Like all traditional anti-cheats, NoMercy only flags/bans; it has zero concept of state rollback or autonomous session recovery.
- **Decision:** **INSPIRE**. We adopt its telemetry definitions (hook detection, memory signature verification, process integrity) for Sentinel-X's Integrity Stream.

---

### Candidate 3: UltimateAntiCheat (AlSch092)
- **Purpose:** Educational usermode anti-cheat demonstrating detection of memory edits, DLL injection, and debugging.
- **Language:** C++
- **License:** Open source (educational).
- **Useful Components:** Periodic checksumming of `.text` and code sections, detection of modified virtual method tables (VMT hooks), heartbeat challenge tokens.
- **Problems:** Windows-only API calls (`EnumProcessModules`, `VirtualQueryEx`); does not provide a multiplayer network server or session recovery.
- **Decision:** **INSPIRE / REFERENCE**. We translate its memory page checksumming and heartbeat verification into Sentinel-X's continuous attestation agent.

---

### Candidate 4: Darken AntiCheat (noahware)
- **Purpose:** Open-source server-assisted anti-cheat system.
- **Language:** C++
- **License:** Open source.
- **Useful Components:** Server-directed challenge tokens and client telemetry report envelopes.
- **Problems:** Lack of game-state integration; strict binary ban trigger without self-healing or rollback capabilities.
- **Decision:** **INSPIRE**. We adopt the server-orchestrated challenge token protocol.

---

## 4. Subsystem Strategy Decision

| Subsystem | Strategy | Execution Details |
| :--- | :---: | :--- |
| **Authoritative Multiplayer Game Server** | **BUILD (Custom)** | High-tick (60 Hz) authoritative physics server with rewindable circular state buffer (600 frames = 10 sec buffer), lag compensation, and projectile simulation. |
| **Cyberpunk Arena Game Client** | **BUILD (Custom)** | 60 FPS Canvas/WebGL client with client-side prediction, smooth interpolation, cybernetic visual effects, and sound synthesizer. |
| **Sentinel-X Security Agent** | **BUILD (Custom)** | Client-side security agent continuously collecting memory page hashes, input jerk metrics, clock drift telemetry, and generating Merkle attestation tokens. |
| **Multi-Vector Evidence Engine** | **BUILD (Custom)** | Server-side correlation engine evaluating Integrity, Behavioral, and Authoritative State streams in real-time. |
| **Dynamic Trust Engine** | **BUILD (Custom)** | Real-time Bayesian/decay trust scoring ($T_s \in [0.0, 1.0]$) mapping into `TRUSTED`, `DEGRADED`, and `COMPROMISED` state machine. |
| **Autonomous Session Recovery Engine** | **BUILD (Custom)** | The hero innovation: Sandboxes compromised clients, identifies the last cryptographically verified checkpoint $C_{\text{trusted}}$, rewinds player state, issues an ephemeral nonce challenge, forces client memory realignment, and restores the session seamlessly. |
| **Interactive Cheat Injection Suite** | **BUILD (Custom)** | Live GUI allowing judges to inject 5 distinct attack vectors in real-time (Speedhack, Aimbot, Memory Edit/Health Freeze, Wallhack/ESP, DLL/Hook Injection). |
| **Sentinel-X SOC Security Dashboard** | **BUILD (Custom)** | Ultra-high-polish, cybernetic glassmorphism operations dashboard showing real-time telemetry graphs, Merkle tree visualizations, trust gauge, and recovery state machine animations. |

---

## 5. Architectural Verdict

We will construct **Sentinel-X as a cohesive, high-performance, full-stack platform** featuring:
1. An Authoritative Multiplayer Game Engine (WebSocket + Node.js + Canvas/WebGL).
2. The Sentinel-X Zero-Trust Security & Recovery Engine.
3. An Interactive Exploit Injection Suite.
4. A Command-Center SOC Dashboard.

This architecture ensures **zero compilation failures, instant cross-platform execution, maximum live demo impact, and absolute scientific coherence**.
