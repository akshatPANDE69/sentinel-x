# 📜 Changelog

## 2026-08-23

### Added
- Compiled native **Rust Security Core (`agent/rust-core/`)** with 5 unit tests.
- Persistent JSON **Game Registry (`data/games/registry.json`)** and dynamic registration form.
- Unified **Security Check Scheduler** with bounded ring buffers (max 100 checks, max 200 activity records).
- **Dual Live Telemetry Streams** (Log A: Security Checks, Log B: Engine Activity).
- Top Bar **Live Current Operation** indicator.
- 21-Test Comprehensive Reality Verification Harness.

### Changed
- Refactored console into an Apple Liquid Glass aesthetic.
- Server strictly authoritative for physics velocity bounds ($\le 1.0$).

### Verified
- 21/21 automated reality tests passed with zero mocks.
- SPSC queue benchmark: 15.24 Million ops/sec.
- SIMD vector scanner: 7.41 GB/s throughput.
- Checkpoint recovery: 0.37 ms latency.
