use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub enum EvidenceSeverity {
    INFO,
    LOW,
    MEDIUM,
    HIGH,
    CRITICAL,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Evidence {
    pub evidence_id: String,
    pub evidence_type: String,
    pub source_vector: String,
    pub severity: EvidenceSeverity,
    pub confidence: f64,
    pub details: serde_json::Value,
    pub timestamp: DateTime<Utc>,
}

impl Evidence {
    pub fn new(
        evidence_type: &str,
        source_vector: &str,
        severity: EvidenceSeverity,
        confidence: f64,
        details: serde_json::Value,
    ) -> Self {
        Self {
            evidence_id: format!("EV-{}", chrono::Utc::now().timestamp_nanos_opt().unwrap_or(0) % 1_000_000),
            evidence_type: evidence_type.to_string(),
            source_vector: source_vector.to_string(),
            severity,
            confidence: confidence.clamp(0.0, 1.0),
            details,
            timestamp: Utc::now(),
        }
    }
}
