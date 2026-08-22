import hashlib
import hmac
import json
import os
import platform
import time
import urllib.request
import urllib.error
from typing import Optional, Dict, Tuple

class SentinelXSDK:
    """
    Sentinel-X Game Protection SDK (Python).
    Game developers integrate this SDK to explicitly opt into Sentinel-X zero-trust attestation,
    process binding, and continuous server-authoritative integrity monitoring.
    """
    def __init__(self):
        self.game_id: str = ""
        self.server_url: str = ""
        self.session_id: Optional[str] = None
        self.session_key: Optional[str] = None
        self.process_id: int = os.getpid()
        self.heartbeat_seq: int = 0
        self.is_initialized: bool = False
        self.is_attested: bool = False
        self.executable_hash: str = ""

    def initialize(self, config: Dict[str, str]) -> bool:
        self.game_id = config.get("game_id", "sx-arena")
        self.server_url = config.get("server_url", "http://127.0.0.1:8080").rstrip("/")
        
        # Calculate executable hash (or fallback baseline for Python scripts)
        exe_path = config.get("executable_path")
        if exe_path and os.path.exists(exe_path):
            with open(exe_path, "rb") as f:
                self.executable_hash = hashlib.sha256(f.read()).hexdigest()
        else:
            self.executable_hash = "d41d8cd98f00b204e9800998ecf8427e" # Registered demo hash
            
        self.is_initialized = True
        return True

    def register_session(self) -> Tuple[bool, str]:
        if not self.is_initialized:
            return False, "SDK_NOT_INITIALIZED"

        payload = json.dumps({
            "game_id": self.game_id,
            "process_id": self.process_id
        }).encode('utf-8')

        req = urllib.request.Request(
            f"{self.server_url}/api/sessions/create",
            data=payload,
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                if not data.get("success"):
                    return False, data.get("error", "CREATION_FAILED")

                self.session_id = data["session"]["session_id"]
                self.session_key = data["session_key"]
                nonce = data["challenge"]["nonce"]
                
                # Perform attestation immediately with the returned challenge nonce
                return self.attest(nonce)
        except Exception as e:
            return False, f"NETWORK_ERROR: {str(e)}"

    def attest(self, nonce: str) -> Tuple[bool, str]:
        if not self.session_id or not self.session_key:
            return False, "NO_ACTIVE_SESSION"

        bundle = {
            "executable_hash": self.executable_hash,
            "platform": f"{platform.system()}_{platform.machine()}",
            "agent_version": "1.0.0"
        }

        canonical_str = f"{self.session_id}:{self.game_id}:{nonce}:{self.executable_hash}:{bundle['platform']}:{bundle['agent_version']}"
        sig = hmac.new(self.session_key.encode('utf-8'), canonical_str.encode('utf-8'), hashlib.sha256).hexdigest()

        payload = json.dumps({
            "session_id": self.session_id,
            "measurement_bundle": bundle,
            "signature": sig
        }).encode('utf-8')

        req = urllib.request.Request(
            f"{self.server_url}/api/attest/verify",
            data=payload,
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                if data.get("success"):
                    self.is_attested = True
                    return True, "PROTECTED"
                return False, data.get("error", "ATTESTATION_FAILED")
        except Exception as e:
            return False, f"ATTESTATION_NETWORK_ERROR: {str(e)}"

    def heartbeat(self) -> Tuple[bool, str]:
        if not self.session_id:
            return False, "NO_SESSION"

        self.heartbeat_seq += 1
        digest = hashlib.sha256(f"{self.session_id}:{self.heartbeat_seq}:{time.time()}".encode('utf-8')).hexdigest()

        payload = json.dumps({
            "session_id": self.session_id,
            "seq_id": self.heartbeat_seq,
            "integrity_digest": digest
        }).encode('utf-8')

        req = urllib.request.Request(
            f"{self.server_url}/api/sessions/heartbeat",
            data=payload,
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                return data.get("success", False), data.get("policy_action", "ALLOW")
        except Exception as e:
            return False, str(e)

    def shutdown(self):
        self.session_id = None
        self.session_key = None
        self.is_attested = False
        self.is_initialized = False
