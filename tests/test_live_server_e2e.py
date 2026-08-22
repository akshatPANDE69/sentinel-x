#!/usr/bin/env python3
import asyncio
import json
import urllib.request
import urllib.error
import hmac
import hashlib

def test_live_server():
    print("Testing Live Sentinel-X Server Integration (Zero-Mock)...")

    # 1. Test Game Registration API
    reg_payload = json.dumps({
        "game_id": "test-arena-v2",
        "name": "Sentinel Arena V2",
        "version": "2.0.0",
        "platforms": ["macos", "windows"],
        "executable_hash": "d41d8cd98f00b204e9800998ecf8427e",
        "developer_public_key": "pk_live_test_key"
    }).encode('utf-8')
    req_reg = urllib.request.Request("http://127.0.0.1:8080/api/games/register", data=reg_payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req_reg) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        assert data.get("success") == True
        print(f"✅ Live Game Registered: {data['game']['name']} (ID: {data['game']['game_id']})")

    # 2. Test Games List API
    with urllib.request.urlopen("http://127.0.0.1:8080/api/games/list") as resp:
        data = json.loads(resp.read().decode('utf-8'))
        assert len(data.get("games", [])) >= 2
        print(f"✅ Live Games List: {len(data['games'])} registered games found")

    # 3. Test Session Creation API
    sess_payload = json.dumps({"game_id": "sx-arena", "process_id": 9999}).encode('utf-8')
    req_sess = urllib.request.Request("http://127.0.0.1:8080/api/sessions/create", data=sess_payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req_sess) as resp:
        sess_data = json.loads(resp.read().decode('utf-8'))
        assert sess_data.get("success") == True
        session_id = sess_data["session"]["session_id"]
        session_key = sess_data["session_key"]
        nonce = sess_data["challenge"]["nonce"]
        print(f"✅ Live Session Created: ID {session_id} | State: {sess_data['session']['state']}")

    # 4. Test Attestation Verification API
    bundle = {"executable_hash": "d41d8cd98f00b204e9800998ecf8427e", "platform": "macOS_arm64", "agent_version": "1.0.0"}
    canonical = f"{session_id}:sx-arena:{nonce}:d41d8cd98f00b204e9800998ecf8427e:macOS_arm64:1.0.0"
    sig = hmac.new(session_key.encode('utf-8'), canonical.encode('utf-8'), hashlib.sha256).hexdigest()
    
    attest_payload = json.dumps({"session_id": session_id, "measurement_bundle": bundle, "signature": sig}).encode('utf-8')
    req_attest = urllib.request.Request("http://127.0.0.1:8080/api/attest/verify", data=attest_payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req_attest) as resp:
        attest_data = json.loads(resp.read().decode('utf-8'))
        assert attest_data.get("success") == True
        assert attest_data["session"]["state"] == "PROTECTED"
        print(f"✅ Live Attestation Solved & Verified: Session State = PROTECTED")

    # 5. Test Heartbeat API
    hb_payload = json.dumps({"session_id": session_id, "seq_id": 1, "integrity_digest": "hb_live_ok"}).encode('utf-8')
    req_hb = urllib.request.Request("http://127.0.0.1:8080/api/sessions/heartbeat", data=hb_payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req_hb) as resp:
        hb_data = json.loads(resp.read().decode('utf-8'))
        assert hb_data.get("success") == True
        print(f"✅ Live Heartbeat Processed: Policy Action = {hb_data.get('policy_action')}")

    # 6. Test Agent Status API
    with urllib.request.urlopen("http://127.0.0.1:8080/api/agent/status") as resp:
        agent_data = json.loads(resp.read().decode('utf-8'))
        assert agent_data.get("active_session") is not None
        assert agent_data["active_session"]["session_id"] == session_id
        print(f"✅ Live Agent Status: Agent State = {agent_data.get('agent_state')} | Bound Session = {session_id}")

    print("\n====================================================================")
    print("🎯 ALL LIVE SERVER ZERO-TRUST INTEGRATION TESTS PASSED 100%!")
    print("====================================================================")

if __name__ == "__main__":
    test_live_server()
