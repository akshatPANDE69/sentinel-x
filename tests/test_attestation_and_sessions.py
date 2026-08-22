import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import hashlib, hmac
from server.registry.game_registry import GameRegistry
from server.session.session_manager import SessionManager, SessionState

def test_session_lifecycle():
    reg = GameRegistry()
    mgr = SessionManager(reg)
    
    # 1. Unregistered game rejected
    sess, err = mgr.create_session("invalid-game-id", 1234)
    assert sess is None and err == "UNREGISTERED_GAME_ID"
    
    # 2. Create valid session
    sess, err = mgr.create_session("sx-arena", 4420)
    assert sess is not None
    assert sess.state == SessionState.ATTESTING
    assert sess.active_challenge_nonce is not None
    
    nonce = sess.active_challenge_nonce
    sid = sess.session_id
    
    # 3. Fail attestation on hash mismatch
    bad_bundle = {"executable_hash": "bad_hash_123", "platform": "macOS", "agent_version": "1.0.0"}
    bad_canonical = f"{sid}:sx-arena:{nonce}:bad_hash_123:macOS:1.0.0"
    bad_sig = hmac.new(sess.session_key.encode('utf-8'), bad_canonical.encode('utf-8'), hashlib.sha256).hexdigest()
    
    ok, reason = mgr.attest_session(sid, bad_bundle, bad_sig)
    assert not ok and "MISMATCH" in reason
    
    # 4. Successful attestation
    # Re-arm challenge
    sess.active_challenge_nonce = nonce
    good_bundle = {"executable_hash": "d41d8cd98f00b204e9800998ecf8427e", "platform": "macOS", "agent_version": "1.0.0"}
    good_canonical = f"{sid}:sx-arena:{nonce}:d41d8cd98f00b204e9800998ecf8427e:macOS:1.0.0"
    good_sig = hmac.new(sess.session_key.encode('utf-8'), good_canonical.encode('utf-8'), hashlib.sha256).hexdigest()
    
    ok, reason = mgr.attest_session(sid, good_bundle, good_sig)
    assert ok and reason == "OK"
    assert sess.state == SessionState.PROTECTED
    assert sess.attestation_verified
    
    # 5. Heartbeat & timeout test
    mgr.record_heartbeat(sid, 1, "digest_1")
    assert sess.heartbeat_sequence == 1
    
    # Simulate 7-second inactivity
    degraded = mgr.check_timeouts(now_ms=sess.last_heartbeat_at + 7000)
    assert sid in degraded
    assert sess.state == SessionState.QUARANTINED
    
    print("✅ test_attestation_and_sessions passed!")

if __name__ == "__main__":
    test_session_lifecycle()
