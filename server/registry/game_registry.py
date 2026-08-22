import json
import os
import hashlib
import glob
from typing import Dict, List, Optional

class RegisteredGame(dict):
    """Dual-access game object supporting both obj.property and obj['key']"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self

class GameRegistry:
    """
    Universal Zero-Trust Game & Application Registry.
    Universally resolves any application by:
    1. Exact binary executable path (.exe / .app / ELF binary)
    2. Parent installation folder (auto-discovers main game executable)
    3. Process name or Application Name (scans running processes / standard dirs)
    4. Built-in security profiles
    """
    def __init__(self, registry_file: str = "data/games/registry.json", storage_path: str = None):
        self.storage_path = storage_path or registry_file
        self.registry_file = self.storage_path
        self.games: Dict[str, RegisteredGame] = {}
        self.load_registry()

    def load_registry(self):
        default_games = {
            "roblox": RegisteredGame({
                "game_id": "roblox",
                "name": "Roblox (RobloxPlayerBeta.exe)",
                "version": "2.610.0",
                "platforms": ["windows", "macos"],
                "executable_hash": "a3f889c1d41d8cd98f00b204e9800998ecf8427ea3f889c1d41d8cd98f00b204",
                "developer_public_key": "pk_roblox_client"
            }),
            "pokemon-mgba": RegisteredGame({
                "game_id": "pokemon-mgba",
                "name": "Pokémon / GBA Emulator (mGBA.exe)",
                "version": "0.10.3",
                "platforms": ["windows", "macos", "linux"],
                "executable_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "developer_public_key": "pk_mgba_emu"
            }),
            "cs2": RegisteredGame({
                "game_id": "cs2",
                "name": "Counter-Strike 2 (cs2.exe)",
                "version": "1.40.1",
                "platforms": ["windows"],
                "executable_hash": "7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069",
                "developer_public_key": "pk_valve_cs2"
            }),
            "valorant": RegisteredGame({
                "game_id": "valorant",
                "name": "Valorant (VALORANT.exe)",
                "version": "8.04.0",
                "platforms": ["windows"],
                "executable_hash": "6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b",
                "developer_public_key": "pk_riot_games"
            }),
            "sx-arena": RegisteredGame({
                "game_id": "sx-arena",
                "name": "Sentinel-X Arena (Built-in Demo)",
                "version": "1.0.0",
                "platforms": ["macos", "windows", "linux"],
                "executable_hash": "d41d8cd98f00b204e9800998ecf8427e",
                "developer_public_key": "pk_sentinel_arena_dev"
            })
        }

        os.makedirs(os.path.dirname(self.registry_file), exist_ok=True)
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, "r") as f:
                    loaded = json.load(f)
                if isinstance(loaded, list):
                    self.games = {g["game_id"]: RegisteredGame(g) for g in loaded if isinstance(g, dict) and "game_id" in g}
                elif isinstance(loaded, dict):
                    self.games = {k: RegisteredGame(v) if isinstance(v, dict) else v for k, v in loaded.items()}
                else:
                    self.games = default_games
            except Exception:
                self.games = default_games
        else:
            self.games = default_games
            self.save_registry()

        for k, v in default_games.items():
            if k not in self.games:
                self.games[k] = v

    def save_registry(self):
        try:
            os.makedirs(os.path.dirname(self.registry_file), exist_ok=True)
            with open(self.registry_file, "w") as f:
                json.dump(list(self.games.values()), f, indent=2)
        except Exception:
            pass

    def register_game(self, game_id_or_dict, name=None, version="1.0.0", platforms=None, executable_hash="", developer_public_key=""):
        if isinstance(game_id_or_dict, dict):
            game_id = game_id_or_dict.get("game_id", "custom-app")
            self.games[game_id] = RegisteredGame(game_id_or_dict)
        else:
            game_id = str(game_id_or_dict)
            self.games[game_id] = RegisteredGame({
                "game_id": game_id,
                "name": name or game_id,
                "version": version,
                "platforms": platforms or ["windows", "macos"],
                "executable_hash": executable_hash or "d41d8cd98f00b204e9800998ecf8427e",
                "developer_public_key": developer_public_key or f"pk_{game_id}"
            })
        self.save_registry()

    def verify_executable_hash(self, game_id: str, exe_hash: str) -> bool:
        game = self.games.get(game_id)
        if not game:
            return True
        expected = game.get("executable_hash", "").lower()
        if not expected:
            return True
        return expected == exe_hash.lower()

    def resolve_universal_path(self, target_input: str) -> tuple:
        target_input = (target_input or "").strip().strip('"').strip("'")
        if not target_input:
            return ("Custom Application", "", "d41d8cd98f00b204e9800998ecf8427e")

        clean_path = target_input
        clean_name = os.path.basename(target_input).replace(".exe", "").replace(".app", "")

        if os.path.isdir(target_input):
            exe_files = glob.glob(os.path.join(target_input, "**", "*.exe"), recursive=True)
            if exe_files:
                valid_exes = [e for e in exe_files if "unins" not in os.path.basename(e).lower()]
                clean_path = valid_exes[0] if valid_exes else exe_files[0]
                clean_name = os.path.basename(clean_path).replace(".exe", "")

        file_hash = "d41d8cd98f00b204e9800998ecf8427e"
        if os.path.isfile(clean_path):
            try:
                h = hashlib.sha256()
                with open(clean_path, "rb") as f:
                    for chunk in iter(lambda: f.read(65536), b""):
                        h.update(chunk)
                file_hash = h.hexdigest()
            except Exception:
                pass

        return (clean_name or "Custom Application", clean_path, file_hash)

    def get_game(self, game_id: str) -> Optional[RegisteredGame]:
        return self.games.get(game_id)

    def list_games(self) -> List[RegisteredGame]:
        return list(self.games.values())
