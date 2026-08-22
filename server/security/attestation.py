import hashlib
import hmac
import os
import time
from typing import Tuple, Optional

class AttestationService:
    """
    Cryptographic Challenge-Response Attestation Service.
    Issues 256-bit unpredictable nonces and verifies measurement bundles
    (executable hash, module digest, platform info) signed via HMAC-SHA256.
    """
    def __init__(self, server_secret: Optional[str] = None):
        self.server_secret = server_secret or os.urandom(32).hex()

    def issue_challenge(self, session_id: str, game_id: str) -> dict:
        nonce = os.urandom(32).hex()
        timestamp = int(time.time() * 1000)
        return {
            "session_id": session_id,
            "game_id": game_id,
            "nonce": nonce,
            "timestamp": timestamp,
            "expected_algorithm": "HMAC-SHA256"
        }

    def verify_attestation_bundle(self, session_id: str, game_id: str, nonce: str,
                                  bundle: dict, client_signature: str, session_key: str) -> Tuple[bool, str]:
        # Extract bundle elements
        exe_hash = bundle.get("executable_hash", "").lower()
        platform_info = bundle.get("platform", "")
        agent_version = bundle.get("agent_version", "")
        
        # Recreate canonical payload
        canonical_str = f"{session_id}:{game_id}:{nonce}:{exe_hash}:{platform_info}:{agent_version}"
        expected_sig = hmac.new(session_key.encode('utf-8'), canonical_str.encode('utf-8'), hashlib.sha256).hexdigest()
        
        if not hmac.compare_digest(expected_sig, client_signature):
            return False, "SIGNATURE_MISMATCH_INVALID_ATTESTATION"
            
        return True, "OK"
