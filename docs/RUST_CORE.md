# 🦀 Rust Security Core (`agent/rust-core/`)

## Module Structure

- `src/lib.rs`: Public API definitions and re-exports.
- `src/crypto.rs`: SHA-256 digest calculation and HMAC-SHA256 challenge verification.
- `src/process.rs`: Native OS process table enumeration and executable hashing.
- `src/integrity.rs`: Physical executable image verification.
- `src/evidence.rs`: Structured multi-vector evidence records.
- `src/session.rs`: Session lifecycle state machine.
- `src/telemetry.rs`: Bounded atomic ring buffers with drop-oldest retention.
- `src/scheduler.rs`: Unified check scheduler.
- `src/health.rs`: System health telemetry (CPU%, RSS MB, checks/sec).
- `src/main.rs`: Standalone binary emitting JSON check results via `--json-check`.

## Verification Commands

```bash
cd agent/rust-core
cargo test
cargo build --release
./target/release/sentinel-core --json-check
```
