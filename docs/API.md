# 🔌 Local REST & WebSocket API Specification

All APIs bind strictly to `127.0.0.1`.

## Endpoints

- `GET /api/health`: System health and agent status.
- `GET /api/games/list`: List all registered games.
- `POST /api/games/register`: Register a new game identity.
- `POST /api/sessions/create`: Create a new session and issue 256-bit challenge nonce.
- `POST /api/attest/verify`: Verify HMAC measurement bundle.
- `POST /api/sessions/heartbeat`: Ingest heartbeat telemetry and return policy action.
- `GET /api/agent/status`: Retrieve active session and agent state.
- `POST /api/exploit/inject`: Inject controlled test anomaly (Developer Mode).
- `POST /api/recovery/trigger`: Trigger authoritative checkpoint rewind.
- `WS /ws/soc`: Real-time WebSocket streaming telemetry and check results.
