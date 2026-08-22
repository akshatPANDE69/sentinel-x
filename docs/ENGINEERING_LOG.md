# 📓 Engineering Journal & Key Decisions

## Decision 1: Explicit Game Registration vs. Magical Discovery
- *Decision:* Require games to explicitly register expected executable SHA-256 hashes in `data/games/registry.json`.
- *Rationale:* Eliminates false claims of auto-protecting arbitrary non-participating software.

## Decision 2: Rust Security Core Integration
- *Decision:* Implement performance-critical routines (hashing, bounded ring buffers, process inspection) in compiled Rust 1.98.
- *Rationale:* Memory safety and raw native performance.

## Decision 3: Server-Authoritative Physics Clamping
- *Decision:* Maintain physics authority on the server. If client reports impossible velocity ($> 2.0$), clamp to $1.0$ and flag divergence.
- *Rationale:* Eliminates reliance on client claims alone.
