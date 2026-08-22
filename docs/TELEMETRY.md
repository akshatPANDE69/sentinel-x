# 📡 Dual Live Telemetry & Structured Logging

## Bounded Ring Buffers

To prevent memory leaks and infinite growth, logs use strict rolling ring buffers:
- **Log A (Security Checks):** Max 100 entries.
- **Log B (Engine Activity):** Max 200 entries.
- **Audit Evidence:** Max 500 entries.

## High-Frequency Aggregation

High-frequency events like heartbeats are aggregated into counters rather than flooding logs:
- Example: `heartbeat() executed: 1,482 times | 0 failures | 100% success`.
