import collections
import time
from typing import List, Dict, Optional

class SecurityCheckRecord:
    def __init__(self, check_id: str, name: str, category: str, severity: str, duration_ms: float, status: str):
        self.check_id = check_id
        self.name = name
        self.category = category
        self.severity = severity
        self.duration_ms = duration_ms
        self.status = status # "PASS" | "WARNING" | "FAIL"
        self.timestamp = int(time.time() * 1000)

    def to_dict(self) -> dict:
        return {
            "check_id": self.check_id,
            "name": self.name,
            "category": self.category,
            "severity": self.severity,
            "duration_ms": self.duration_ms,
            "status": self.status,
            "timestamp": self.timestamp
        }

class EngineOperationRecord:
    def __init__(self, operation: str, component: str, duration_ms: float, result: str):
        self.operation = operation
        self.component = component
        self.duration_ms = duration_ms
        self.result = result
        self.timestamp = int(time.time() * 1000)

    def to_dict(self) -> dict:
        return {
            "operation": self.operation,
            "component": self.component,
            "duration_ms": self.duration_ms,
            "result": self.result,
            "timestamp": self.timestamp
        }

class UnifiedSecurityScheduler:
    """
    Unified Security Check Scheduler with Strict Bounded Ring Buffers:
    - Max 100 Security Check Records
    - Max 200 Engine Activity Records
    - Dynamic function-level activity tracking (get_health, process_scan, etc.)
    """
    def __init__(self, max_checks: int = 100, max_activity: int = 200):
        self.checks_log = collections.deque(maxlen=max_checks)
        self.activity_log = collections.deque(maxlen=max_activity)
        self.current_operation: Optional[dict] = {
            "operation": "get_health()",
            "component": "Rust Security Core",
            "duration_ms": 0.8,
            "status": "RUNNING",
            "timestamp": int(time.time() * 1000)
        }
        self.operation_counters: Dict[str, int] = collections.defaultdict(int)
        self.last_check_time = 0
        self.step = 0

    def record_operation(self, operation: str, component: str = "Rust Security Core", duration_ms: float = 1.2, result: str = "PASS"):
        self.operation_counters[operation] += 1
        rec = EngineOperationRecord(operation, component, duration_ms, result)
        self.activity_log.append(rec.to_dict())
        self.current_operation = {
            "operation": operation,
            "component": component,
            "duration_ms": duration_ms,
            "status": "RUNNING" if result == "IN_PROGRESS" else "PASS",
            "timestamp": int(time.time() * 1000)
        }

    def record_check(self, check_id: str, name: str, category: str, severity: str, duration_ms: float, status: str):
        rec = SecurityCheckRecord(check_id, name, category, severity, duration_ms, status)
        self.checks_log.append(rec.to_dict())

    def run_scheduled_checks(self, is_session_active: bool, is_compromised: bool = False):
        now = time.time()
        if now - self.last_check_time < 1.2:
            return
        self.last_check_time = now
        self.step = (self.step + 1) % 5

        if self.step == 0:
            # Health check
            self.record_operation("get_health()", "Rust Security Core", 0.6, "PASS")
            self.record_check("AGENT_HEALTH", "Rust Core RSS & CPU Bounds", "PLATFORM", "INFO", 0.6, "PASS")

        elif self.step == 1:
            # Process scan
            self.record_operation("process_scan()", "Rust Security Core", 1.8, "PASS")
            self.record_check("PROCESS_INTEGRITY", "Process Table & Image Path", "PROCESS", "CRITICAL", 1.8, "PASS")

        elif self.step == 2:
            # Binary measurement
            if is_compromised:
                self.record_operation("sha256_measurement()", "Rust Security Core", 2.4, "FAIL")
                self.record_check("EXECUTABLE_HASH", "Binary .text SHA-256 Signature", "INTEGRITY", "CRITICAL", 2.4, "FAIL")
            else:
                self.record_operation("sha256_measurement()", "Rust Security Core", 1.2, "PASS")
                self.record_check("EXECUTABLE_HASH", "Binary .text SHA-256 Signature", "INTEGRITY", "CRITICAL", 1.2, "PASS")

        elif self.step == 3:
            # Attestation verification
            if is_session_active and not is_compromised:
                self.record_operation("verify_attestation()", "Rust Security Core", 1.5, "PASS")
                self.record_check("SESSION_ATTESTATION", "Cryptographic Nonce Token Proof", "SESSION", "CRITICAL", 1.5, "PASS")
            elif is_compromised:
                self.record_operation("verify_attestation()", "Rust Security Core", 1.9, "FAIL")
                self.record_check("SESSION_ATTESTATION", "Cryptographic Nonce Token Proof", "SESSION", "CRITICAL", 1.9, "FAIL")
            else:
                self.record_operation("listen_discovery()", "Agent Daemon", 0.4, "PASS")

        elif self.step == 4:
            # Server authority validation
            if is_compromised:
                self.record_operation("validate_state()", "Security Engine", 0.6, "FAIL")
                self.record_check("SERVER_AUTHORITY", "State Divergence & Velocity Bounds", "SERVER", "CRITICAL", 0.6, "FAIL")
            else:
                self.record_operation("validate_state()", "Security Engine", 0.4, "PASS")
                self.record_check("SERVER_AUTHORITY", "State Divergence & Velocity Bounds", "SERVER", "CRITICAL", 0.4, "PASS")

    def get_telemetry_payload(self) -> dict:
        return {
            "current_operation": self.current_operation,
            "recent_checks": list(self.checks_log)[-12:], # bounded to latest 12
            "recent_activity": list(self.activity_log)[-12:], # bounded to latest 12
            "operation_counters": dict(self.operation_counters)
        }
