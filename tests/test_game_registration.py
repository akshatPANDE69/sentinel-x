import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server.registry.game_registry import GameRegistry

def test_registration():
    reg = GameRegistry()
    
    # 1. Verify default seeded game
    default_game = reg.get_game("sx-arena")
    assert default_game is not None, "Default game sx-arena must be registered"
    assert default_game.executable_hash == "d41d8cd98f00b204e9800998ecf8427e"
    
    # 2. Register custom game
    custom = reg.register_game(
        game_id="custom-fps-2026",
        name="Cyber Ops",
        version="2.1.0",
        platforms=["macos", "windows"],
        executable_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        sdk_version="1.0"
    )
    assert custom.game_id == "custom-fps-2026"
    assert len(reg.list_games()) >= 2
    
    # 3. Test executable hash verification
    assert reg.verify_executable_hash("custom-fps-2026", "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855")
    assert not reg.verify_executable_hash("custom-fps-2026", "0000000000000000000000000000000000000000000000000000000000000000")
    
    print("✅ test_game_registration passed!")

if __name__ == "__main__":
    test_registration()
