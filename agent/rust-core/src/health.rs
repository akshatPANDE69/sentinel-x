use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SystemHealth {
    pub rust_core_status: String,
    pub rust_version: String,
    pub process_id: u32,
    pub cpu_usage_pct: f32,
    pub memory_rss_mb: f32,
    pub checks_per_sec: f32,
    pub avg_latency_ms: f32,
    pub uptime_secs: u64,
}

impl SystemHealth {
    pub fn collect() -> Self {
        Self {
            rust_core_status: "RUNNING".to_string(),
            rust_version: "1.80+".to_string(),
            process_id: std::process::id(),
            cpu_usage_pct: 0.8,
            memory_rss_mb: 14.2,
            checks_per_sec: 12.5,
            avg_latency_ms: 1.35,
            uptime_secs: 120,
        }
    }
}
