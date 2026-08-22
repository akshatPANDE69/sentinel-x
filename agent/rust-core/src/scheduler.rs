use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub enum CheckCategory {
    PROCESS,
    INTEGRITY,
    SESSION,
    PLATFORM,
    SERVER,
    BEHAVIOR,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub enum CheckSeverity {
    INFO,
    WARNING,
    CRITICAL,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub enum CheckResult {
    PASS,
    WARNING,
    FAIL,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SecurityCheck {
    pub check_id: String,
    pub name: String,
    pub category: CheckCategory,
    pub severity: CheckSeverity,
    pub interval_ms: u64,
    pub last_duration_ms: f64,
    pub last_result: CheckResult,
    pub last_run: DateTime<Utc>,
    pub execution_count: u64,
}

pub struct CheckScheduler {
    pub checks: Vec<SecurityCheck>,
}

impl CheckScheduler {
    pub fn new_standard_suite() -> Self {
        Self {
            checks: vec![
                SecurityCheck {
                    check_id: "PROCESS_INTEGRITY".to_string(),
                    name: "Process Table & Image Path".to_string(),
                    category: CheckCategory::PROCESS,
                    severity: CheckSeverity::CRITICAL,
                    interval_ms: 2000,
                    last_duration_ms: 0.8,
                    last_result: CheckResult::PASS,
                    last_run: Utc::now(),
                    execution_count: 0,
                },
                SecurityCheck {
                    check_id: "EXECUTABLE_HASH".to_string(),
                    name: "Binary .text SHA-256 Signature".to_string(),
                    category: CheckCategory::INTEGRITY,
                    severity: CheckSeverity::CRITICAL,
                    interval_ms: 5000,
                    last_duration_ms: 1.4,
                    last_result: CheckResult::PASS,
                    last_run: Utc::now(),
                    execution_count: 0,
                },
                SecurityCheck {
                    check_id: "MODULE_INTEGRITY".to_string(),
                    name: "Loaded Dynamic Library Verification".to_string(),
                    category: CheckCategory::INTEGRITY,
                    severity: CheckSeverity::WARNING,
                    interval_ms: 10000,
                    last_duration_ms: 2.1,
                    last_result: CheckResult::PASS,
                    last_run: Utc::now(),
                    execution_count: 0,
                },
                SecurityCheck {
                    check_id: "SESSION_ATTESTATION".to_string(),
                    name: "Cryptographic Nonce Token Proof".to_string(),
                    category: CheckCategory::SESSION,
                    severity: CheckSeverity::CRITICAL,
                    interval_ms: 3000,
                    last_duration_ms: 1.8,
                    last_result: CheckResult::PASS,
                    last_run: Utc::now(),
                    execution_count: 0,
                },
                SecurityCheck {
                    check_id: "SERVER_AUTHORITY".to_string(),
                    name: "State Divergence & Velocity Bounds".to_string(),
                    category: CheckCategory::SERVER,
                    severity: CheckSeverity::CRITICAL,
                    interval_ms: 1000,
                    last_duration_ms: 0.4,
                    last_result: CheckResult::PASS,
                    last_run: Utc::now(),
                    execution_count: 0,
                },
            ],
        }
    }

    pub fn execute_all(&mut self) {
        for check in &mut self.checks {
            check.execution_count += 1;
            check.last_run = Utc::now();
        }
    }
}
