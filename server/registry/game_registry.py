import time
from typing import Dict, Optional, List

class GameRegistration:
    def __init__(self, game_id: str, name: str, version: str, platforms: List[str],
                 executable_hash: str, sdk_version: str = "1.0", developer_public_key: str = "dev_pubkey_default"):
        self.game_id = game_id
        self.name = name
        self.version = version
        self.platforms = platforms
        self.executable_hash = executable_hash.lower()
        self.sdk_version = sdk_version
        self.developer_public_key = developer_public_key
        self.registered_at = int(time.time() * 1000)

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
    Authoritative Game Registry.
    Games must register their binary identities, public keys, and supported platforms
    before Sentinel-X will establish protected sessions.
    """
    def __init__(self):
        self._games: Dict[str, GameRegistration] = {}
        self._seed_default_games()

    def _seed_default_games(self):
        # Register the default demonstration target game
        self.register_game(
            game_id="sx-arena",
            name="Sentinel-X Arena",
            version="1.0.0",
            platforms=["macos", "windows", "linux"],
            executable_hash="d41d8cd98f00b204e9800998ecf8427e",
            sdk_version="1.0",
            developer_public_key="pk_secp256k1_sentinel_arena_prod"
        )

    def register_game(self, game_id: str, name: str, version: str, platforms: List[str],
                      executable_hash: str, sdk_version: str = "1.0", developer_public_key: str = "") -> GameRegistration:
        reg = GameRegistration(game_id, name, version, platforms, executable_hash, sdk_version, developer_public_key)
        self._games[game_id] = reg
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
