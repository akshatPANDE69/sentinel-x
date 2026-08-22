import hashlib
import os
import time
from typing import Dict, Optional, List, Tuple
from server.registry.game_registry import GameRegistry
from server.security.attestation import AttestationService
from server.security.policy import PolicyEngine, SecurityPolicyAction

class SessionState:
    STOPPED = "STOPPED"
    STARTED = "STARTED"
    DISCOVERING = "DISCOVERING"
    GAME_FOUND = "GAME_FOUND"
    SESSION_NEGOTIATING = "SESSION_NEGOTIATING"
    ATTESTING = "ATTESTING"
    PROTECTED = "PROTECTED"
    DEGRADED = "DEGRADED"
    QUARANTINED = "QUARANTINED"
    RECOVERING = "RECOVERING"
    RESTORED = "RESTORED"
    ERROR = "ERROR"

class ProtectedSession:
    def __init__(self, session_id: str, game_id: str, process_id: int, session_key: str):
        self.session_id = session_id
        self.game_id = game_id
        self.process_id = process_id
        self.session_key = session_key
        self.state = SessionState.STARTED
        self.created_at = int(time.time() * 1000)
        self.last_heartbeat_at = self.created_at
        self.heartbeat_sequence = 0
        self.trust_score = 1.0
        self.policy_action = SecurityPolicyAction.ALLOW
        self.active_challenge_nonce: Optional[str] = None
        self.attestation_verified = False
        self.threats_blocked = 0
        self.integrity_checks_count = 0
        self.evidence_history: List[dict] = []

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "game_id": self.game_id,
            "process_id": self.process_id,
            "state": self.state,
            "created_at": self.created_at,
            "last_heartbeat_at": self.last_heartbeat_at,
            "heartbeat_sequence": self.heartbeat_sequence,
            "trust_score": round(self.trust_score, 4),
            "policy_action": self.policy_action,
            "attestation_verified": self.attestation_verified,
            "threats_blocked": self.threats_blocked,
            "integrity_checks_count": self.integrity_checks_count
        }

class SessionManager:
    """
    Authoritative Session Lifecycle Manager.
    Manages session creation, cryptographic binding, heartbeats, and policy-driven transitions.
    """
    def __init__(self, game_registry: GameRegistry):
        self.game_registry = game_registry
        self.attestation_service = AttestationService()
        self.policy_engine = PolicyEngine()
        self.sessions: Dict[str, ProtectedSession] = {}
        self.process_to_session: Dict[int, str] = {}

    def create_session(self, game_id: str, process_id: int) -> Tuple[Optional[ProtectedSession], str]:
        game = self.game_registry.get_game(game_id)
        if not game:
            return None, "UNREGISTERED_GAME_ID"

        session_id = f"SX-{os.urandom(4).hex().upper()}"
        session_key = hashlib.sha256(f"{session_id}:{game_id}:{os.urandom(16).hex()}".encode('utf-8')).hexdigest()
        
        session = ProtectedSession(session_id, game_id, process_id, session_key)
        session.state = SessionState.SESSION_NEGOTIATING
        
        self.sessions[session_id] = session
        self.process_to_session[process_id] = session_id
        
        # Issue challenge nonce
        challenge = self.attestation_service.issue_challenge(session_id, game_id)
        session.active_challenge_nonce = challenge["nonce"]
        session.state = SessionState.ATTESTING
        
        return session, "OK"

    def attest_session(self, session_id: str, measurement_bundle: dict, client_signature: str) -> Tuple[bool, str]:
        session = self.sessions.get(session_id)
        if not session:
            return False, "SESSION_NOT_FOUND"

        if not session.active_challenge_nonce:
            return False, "NO_ACTIVE_CHALLENGE"

        # Verify executable hash against registry
        exe_hash = measurement_bundle.get("executable_hash", "")
        if not self.game_registry.verify_executable_hash(session.game_id, exe_hash):
            session.state = SessionState.ERROR
            return False, "EXECUTABLE_HASH_MISMATCH_UNTRUSTED_BINARY"

        # Verify cryptographic signature
        ok, reason = self.attestation_service.verify_attestation_bundle(
            session_id, session.game_id, session.active_challenge_nonce,
            measurement_bundle, client_signature, session.session_key
        )
        
        if not ok:
            session.state = SessionState.ERROR
            return False, reason

        session.attestation_verified = True
        session.state = SessionState.PROTECTED
        session.active_challenge_nonce = None
        session.integrity_checks_count += 1
        return True, "OK"

    def record_heartbeat(self, session_id: str, seq_id: int, integrity_digest: str) -> Tuple[bool, str]:
        session = self.sessions.get(session_id)
        if not session:
            return False, "SESSION_NOT_FOUND"

        session.last_heartbeat_at = int(time.time() * 1000)
        session.heartbeat_sequence = seq_id
        session.integrity_checks_count += 1
        return True, "OK"

    def check_timeouts(self, now_ms: Optional[int] = None) -> List[str]:
        now = now_ms or int(time.time() * 1000)
        degraded_sessions = []
        for sid, sess in self.sessions.items():
            if sess.state in [SessionState.PROTECTED, SessionState.DEGRADED]:
                age_ms = now - sess.last_heartbeat_at
                if age_ms > 6000: # 6 seconds timeout
                    sess.state = SessionState.QUARANTINED
                    sess.policy_action = SecurityPolicyAction.QUARANTINE
                    degraded_sessions.append(sid)
                elif age_ms > 3000: # 3 seconds timeout
                    sess.state = SessionState.DEGRADED
                    sess.policy_action = SecurityPolicyAction.MONITOR
        return degraded_sessions

    def get_session(self, session_id: str) -> Optional[ProtectedSession]:
        return self.sessions.get(session_id)

    def get_active_session(self) -> Optional[ProtectedSession]:
        active_list = [
            s for s in self.sessions.values()
            if s.state in [SessionState.PROTECTED, SessionState.DEGRADED, SessionState.QUARANTINED, SessionState.RECOVERING]
        ]
        if not active_list:
            return None
        # Return the most recently active session
        return max(active_list, key=lambda s: s.last_heartbeat_at)
