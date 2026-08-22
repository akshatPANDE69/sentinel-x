class SecurityPolicyAction:
    ALLOW = "ALLOW"
    MONITOR = "MONITOR"
    INCREASE_TELEMETRY = "INCREASE_TELEMETRY"
    QUARANTINE = "QUARANTINE"
    RECOVER = "RECOVER"
    REJECT = "REJECT"

class PolicyEngine:
    """
    Multi-tier Zero-Trust Policy Engine.
    Translates correlated Bayesian evidence and trust scores into progressive security actions.
    """
    def __init__(self):
        pass

    def evaluate_policy(self, trust_score: float, has_critical_integrity_failure: bool = False,
                        has_server_divergence: bool = False) -> str:
        # Critical structural failures trigger immediate quarantine / recovery
        if has_critical_integrity_failure or has_server_divergence:
            return SecurityPolicyAction.RECOVER

        if trust_score >= 0.85:
            return SecurityPolicyAction.ALLOW
        elif trust_score >= 0.70:
            return SecurityPolicyAction.MONITOR
        elif trust_score >= 0.50:
            return SecurityPolicyAction.INCREASE_TELEMETRY
        else:
            return SecurityPolicyAction.QUARANTINE
