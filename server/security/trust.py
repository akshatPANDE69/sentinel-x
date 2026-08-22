import time

class TrustState:
    TRUSTED = "TRUSTED"        # 0.85 - 1.00
    DEGRADED = "DEGRADED"      # 0.50 - 0.84
    COMPROMISED = "COMPROMISED"# < 0.50


class DynamicTrustEngine:
    def __init__(self, decay_rate=0.015, recovery_rate=0.03):
        self.trust_scores = {}  # player_id -> float (0.0 to 1.0)
        self.trust_states = {}  # player_id -> TrustState
        self.state_history = {} # player_id -> list of event dicts
        self.decay_rate = decay_rate
        self.recovery_rate = recovery_rate

    def register_player(self, player_id):
        self.trust_scores[player_id] = 1.0
        self.trust_states[player_id] = TrustState.TRUSTED
        self.state_history[player_id] = []

    def unregister_player(self, player_id):
        self.trust_scores.pop(player_id, None)
        self.trust_states.pop(player_id, None)
        self.state_history.pop(player_id, None)

    def get_trust_score(self, player_id):
        return self.trust_scores.get(player_id, 1.0)

    def get_trust_state(self, player_id):
        return self.trust_states.get(player_id, TrustState.TRUSTED)

    def set_trust(self, player_id, score, reason="MANUAL_OVERRIDE"):
        score = max(0.0, min(1.0, score))
        old_score = self.trust_scores.get(player_id, 1.0)
        old_state = self.trust_states.get(player_id, TrustState.TRUSTED)
        
        self.trust_scores[player_id] = score
        new_state = self._calculate_state(score)
        self.trust_states[player_id] = new_state
        
        event = {
            "timestamp": time.time(),
            "old_score": round(old_score, 3),
            "new_score": round(score, 3),
            "old_state": old_state,
            "new_state": new_state,
            "reason": reason
        }
        self.state_history.setdefault(player_id, []).append(event)
        return new_state, event

    def update_with_evidence(self, player_id, evidence_result):
        old_score = self.trust_scores.get(player_id, 1.0)
        old_state = self.trust_states.get(player_id, TrustState.TRUSTED)
        
        penalty = evidence_result["total_penalty"]
        
        if evidence_result["is_clean"]:
            # Clean tick: slight recovery towards 1.0
            new_score = min(1.0, old_score + self.recovery_rate)
        else:
            # Anomaly detected: apply penalties
            new_score = max(0.0, old_score - penalty)
            
        self.trust_scores[player_id] = new_score
        new_state = self._calculate_state(new_score)
        self.trust_states[player_id] = new_state
        
        state_changed = (old_state != new_state)
        event = {
            "timestamp": time.time(),
            "old_score": round(old_score, 3),
            "new_score": round(new_score, 3),
            "old_state": old_state,
            "new_state": new_state,
            "penalty": round(penalty, 3),
            "flags": evidence_result["flags"],
            "state_changed": state_changed
        }
        
        if not evidence_result["is_clean"] or state_changed:
            self.state_history.setdefault(player_id, []).append(event)
            
        return new_score, new_state, event

    def _calculate_state(self, score):
        if score >= 0.85:
            return TrustState.TRUSTED
        elif score >= 0.50:
            return TrustState.DEGRADED
        else:
            return TrustState.COMPROMISED
