use std::thread;
use std::time::Duration;
use sentinel_core::{CheckScheduler, CryptoEngine, ProcessScanner, SystemHealth};

fn main() {
    println!("=======================================================");
    println!("   SENTINEL-X RUST SECURITY CORE ACTIVE (v1.0.0)      ");
    println!("   PID: {} | Architecture: Native aarch64/x86_64", std::process::id());
    println!("=======================================================");

    let mut scheduler = CheckScheduler::new_standard_suite();
    let candidates = ProcessScanner::scan_candidates(&["sentinel", "arena", "game", "python"]);
    println!("[Rust Core] Discovered {} candidate target processes", candidates.len());

    let health = SystemHealth::collect();
    let json_health = serde_json::to_string(&health).unwrap_or_default();
    println!("[Rust Core Health] {}", json_health);

    // If CLI argument --json-check is passed, output structured check report and exit
    if std::env::args().any(|a| a == "--json-check") {
        scheduler.execute_all();
        let json_checks = serde_json::to_string(&scheduler.checks).unwrap_or_default();
        println!("{}", json_checks);
        return;
    }

    println!("[Rust Core] Standalone loop active. Press Ctrl+C to terminate.");
    loop {
        scheduler.execute_all();
        thread::sleep(Duration::from_secs(2));
    }
}
