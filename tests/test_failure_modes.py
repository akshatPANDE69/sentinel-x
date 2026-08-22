#!/usr/bin/env python3
import json
import urllib.request
import urllib.error
import hmac
import hashlib

def test_failure_modes():
    print("Testing Sentinel-X Zero-Trust Failure Modes...")

    # 1. Test Unregistered Game Rejection
    bad_sess_payload = json.dumps({"game_id": "unregistered_cheat_game", "process_id": 1111}).encode('utf-8')
    req_bad = urllib.request.Request("http://127.0.0.1:8080/api/sessions/create", data=bad_sess_payload, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req_bad)
        assert False, "Unregistered game must be rejected"
    except urllib.error.HTTPError as e:
        assert e.code == 400
        print("✅ Failure Test 1 Passed: Unregistered game rejected (HTTP 400)")

    # 2. Test Modified Executable Hash Rejection
    sess_payload = json.dumps({"game_id": "sx-arena", "process_id": 2222}).encode('utf-8')
    req_sess = urllib.request.Request("http://127.0.0.1:8080/api/sessions/create", data=sess_payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req_sess) as resp:
        sess_data = json.loads(resp.read().decode('utf-8'))
        sid = sess_data["session"]["session_id"]
        skey = sess_data["session_key"]
        nonce = sess_data["challenge"]["nonce"]

    # Tampered executable hash
    tampered_bundle = {"executable_hash": "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", "platform": "macOS", "agent_version": "1.0.0"}
    tampered_canonical = f"{sid}:sx-arena:{nonce}:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff:macOS:1.0.0"
    tampered_sig = hmac.new(skey.encode('utf-8'), tampered_canonical.encode('utf-8'), hashlib.sha256).hexdigest()

    req_tamper = urllib.request.Request("http://127.0.0.1:8080/api/attest/verify", data=json.dumps({
        "session_id": sid, "measurement_bundle": tampered_bundle, "signature": tampered_sig
    }).encode('utf-8'), headers={"Content-Type": "application/json"})

    try:
        urllib.request.urlopen(req_tamper)
        assert False, "Modified executable binary must fail attestation"
    except urllib.error.HTTPError as e:
        assert e.code == 403
        print("✅ Failure Test 2 Passed: Modified executable hash rejected (HTTP 403)")

    # 3. Test Forged HMAC Signature Rejection
    req_forged = urllib.request.Request("http://127.0.0.1:8080/api/attest/verify", data=json.dumps({
        "session_id": sid,
        "measurement_bundle": {"executable_hash": "d41d8cd98f00b204e9800998ecf8427e", "platform": "macOS", "agent_version": "1.0.0"},
        "signature": "deadbeefcafebabe000000000000000000000000000000000000000000000000"
    }).encode('utf-8'), headers={"Content-Type": "application/json"})

    try:
        urllib.request.urlopen(req_forged)
        assert False, "Forged HMAC signature must fail attestation"
    except urllib.error.HTTPError as e:
        assert e.code == 403
        print("✅ Failure Test 3 Passed: Forged attestation signature rejected (HTTP 403)")

    print("\n====================================================================")
    print("🎯 ALL SECURITY FAILURE TESTS PASSED 100%!")
    print("====================================================================")

if __name__ == "__main__":
    test_failure_modes()
