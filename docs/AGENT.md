# 🤖 Sentinel-X Endpoint Security Agent

## Lifecycle State Machine

`STOPPED` $\longrightarrow$ `STARTED` $\longrightarrow$ `DISCOVERING` $\longrightarrow$ `GAME_FOUND` $\longrightarrow$ `SESSION_NEGOTIATING` $\longrightarrow$ `ATTESTING` $\longrightarrow$ `PROTECTED` $\longrightarrow$ `DEGRADED` $\longrightarrow$ `QUARANTINED` $\longrightarrow$ `RECOVERING` $\longrightarrow$ `RESTORED`

## Responsibilities

- Continuous native process table scanning (`psutil` / native APIs).
- Dynamic matching of running binaries against `data/games/registry.json`.
- Bounded event collection and execution of scheduled security checks.
- Zero-state truthfulness: Displays "Waiting for protected game..." until a registered game connects.
