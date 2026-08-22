import json
import os
import time
from typing import Dict, Optional, List

class GameRegistration:
    def __init__(self, game_id: str, name: str, version: str, platforms: List[str],
                 executable_hash: str, sdk_version: str = "1.0", developer_public_key: str = "dev_pubkey_default",
                 registered_at: Optional[int] = None):
        self.game_id = game_id
        self.name = name
        self.version = version
        self.platforms = platforms
        self.executable_hash = executable_hash.lower()
        self.sdk_version = sdk_version
        self.developer_public_key = developer_public_key
        self.registered_at = registered_at or int(time.time() * 1000)

    def to_dict(self) -> dict:
        return {
            "game_id": self.game_id,
            "name": self.name,
            "version": self.version,
            "platforms": self.platforms,
            "executable_hash": self.executable_hash,
            "sdk_version": self.sdk_version,
            "developer_public_key": self.developer_public_key,
            "registered_at": self.registered_at
        }

class GameRegistry:
    """
    Persistent Game Registry.
    Stores and retrieves registered game identities from data/games/registry.json.
    """
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "data", "games", "registry.json")
        )
        self._games: Dict[str, GameRegistration] = {}
        self.load_from_disk()

    def load_from_disk(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                    for item in data.get("games", []):
                        g = GameRegistration(**item)
                        self._games[g.game_id] = g
            except Exception:
                pass
        
        # Ensure default demo game
        if "sx-arena" not in self._games:
            self.register_game(
                game_id="sx-arena",
                name="Sentinel-X Arena",
                version="1.0.0",
                platforms=["macos", "windows", "linux"],
                executable_hash="d41d8cd98f00b204e9800998ecf8427e",
                sdk_version="1.0",
                developer_public_key="pk_secp256k1_sentinel_arena_prod"
            )

    def save_to_disk(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        try:
            with open(self.storage_path, "w") as f:
                json.dump({"games": [g.to_dict() for g in self._games.values()]}, f, indent=2)
        except Exception:
            pass

    def register_game(self, game_id: str, name: str, version: str, platforms: List[str],
                      executable_hash: str, sdk_version: str = "1.0", developer_public_key: str = "") -> GameRegistration:
        reg = GameRegistration(game_id, name, version, platforms, executable_hash, sdk_version, developer_public_key)
        self._games[game_id] = reg
        self.save_to_disk()
        return reg

    def get_game(self, game_id: str) -> Optional[GameRegistration]:
        return self._games.get(game_id)

    def list_games(self) -> List[dict]:
        return [g.to_dict() for g in self._games.values()]

    def verify_executable_hash(self, game_id: str, candidate_hash: str) -> bool:
        game = self.get_game(game_id)
        if not game:
            return False
        return game.executable_hash == candidate_hash.lower()
