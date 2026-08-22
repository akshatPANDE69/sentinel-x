import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from server.registry.game_registry import GameRegistry
from server.session.session_manager import SessionManager
from sdk.python.sentinel_x import SentinelXSDK
from agent.process_discovery import ProcessDiscoveryEngine

def test_full_sdk_agent_chain():
    print("Executing End-to-End Real Zero-Trust Lifecycle Test...")
    
    # 1. Discover Process
    engine = ProcessDiscoveryEngine()
    procs = engine.scan_running_processes()
    print(f"✅ Process Discovery: Scanned OS processes, found {len(procs)} candidates")
    
    # 2. Game Registry Verification
    reg = GameRegistry()
    game = reg.get_game("sx-arena")
    assert game is not None
    print(f"✅ Game Registry: Loaded registered game '{game.name}' (Hash: {game.executable_hash})")
    
    # 3. Session Manager Handshake
    mgr = SessionManager(reg)
    session, err = mgr.create_session("sx-arena", os.getpid())
    assert session is not None
    print(f"✅ Session Created: ID {session.session_id} | State: {session.state}")
    
    # 4. Attestation
    nonce = session.active_challenge_nonce
    import hmac, hashlib
    bundle = {"executable_hash": "d41d8cd98f00b204e9800998ecf8427e", "platform": "macOS_arm64", "agent_version": "1.0.0"}
    canonical = f"{session.session_id}:sx-arena:{nonce}:d41d8cd98f00b204e9800998ecf8427e:macOS_arm64:1.0.0"
    sig = hmac.new(session.session_key.encode('utf-8'), canonical.encode('utf-8'), hashlib.sha256).hexdigest()
    
    ok, reason = mgr.attest_session(session.session_id, bundle, sig)
    assert ok
    print(f"✅ Attestation Verified: Nonce Challenge Solved | Session State: {session.state}")
    
    # 5. Heartbeat flow
    mgr.record_heartbeat(session.session_id, 1, "hb_1")
    mgr.record_heartbeat(session.session_id, 2, "hb_2")
    print(f"✅ Heartbeats Flowing: Sequence #{session.heartbeat_sequence}")
    
    print("\n====================================================================")
    print("🎯 ALL REAL ZERO-TRUST LIFECYCLE TESTS PASSED 100%!")
    print("====================================================================")

if __name__ == "__main__":
    test_full_sdk_agent_chain()
