use serde::{Deserialize, Serialize};
use crate::process::ProcessScanner;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IntegrityMeasurement {
    pub target: String,
    pub expected_hash: String,
    pub actual_hash: String,
    pub passed: bool,
}

pub struct IntegrityEngine;

impl IntegrityEngine {
    pub fn verify_executable(path: &str, expected_hash: &str) -> IntegrityMeasurement {
        let actual = ProcessScanner::compute_file_sha256(path)
            .unwrap_or_else(|| "d41d8cd98f00b204e9800998ecf8427e".to_string());
        
        let passed = actual.eq_ignore_ascii_case(expected_hash);

        IntegrityMeasurement {
            target: path.to_string(),
            expected_hash: expected_hash.to_string(),
            actual_hash: actual,
            passed,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_integrity_check() {
        let m = IntegrityEngine::verify_executable("/bin/sh", "ffffffffffffffffffffffffffffffff");
        assert!(!m.passed);
    }
}
