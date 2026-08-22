# 🎮 Game Registration & Enrollment

## Philosophy

Sentinel-X enforces **explicit developer enrollment**. An executable is not protected merely because it exists; it must be registered with its cryptographic identity in `data/games/registry.json`.

## Schema

```json
{
  "game_id": "sx-arena",
  "name": "Sentinel-X Arena",
  "version": "1.0.0",
  "platforms": ["macos", "windows", "linux"],
  "executable_hash": "d41d8cd98f00b204e9800998ecf8427e",
  "sdk_version": "1.0",
  "developer_public_key": "pk_secp256k1_sentinel_arena_prod",
  "registered_at": 1787420000000
}
```

## Dynamic Registration via API

```bash
curl -X POST http://127.0.0.1:8080/api/games/register \
  -H "Content-Type: application/json" \
  -d '{
    "game_id": "custom-game",
    "name": "Custom FPS",
    "version": "1.0.0",
    "platforms": ["macos", "windows"],
    "executable_hash": "d41d8cd98f00b204e9800998ecf8427e",
    "developer_public_key": "pk_custom_dev"
  }'
```
