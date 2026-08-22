use serde::{Deserialize, Serialize};
use std::fs;
use std::path::Path;
use crate::crypto::CryptoEngine;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct DiscoveredProcess {
    pub pid: u32,
    pub name: String,
    pub exe_path: String,
    pub exe_hash: String,
    pub matched_game_id: Option<String>,
}

pub struct ProcessScanner;

impl ProcessScanner {
    pub fn compute_file_sha256<P: AsRef<Path>>(path: P) -> Option<String> {
        let bytes = fs::read(path).ok()?;
        Some(CryptoEngine::sha256_digest(&bytes))
    }

    pub fn scan_candidates(target_keywords: &[&str]) -> Vec<DiscoveredProcess> {
        let mut results = Vec::new();

        // Native POSIX process inspection / proc scan fallback
        #[cfg(target_family = "unix")]
        {
            if let Ok(output) = std::process::Command::new("ps")
                .args(["-A", "-o", "pid,comm"])
                .output()
            {
                if let Ok(text) = String::from_utf8(output.stdout) {
                    for line in text.lines().skip(1) {
                        let parts: Vec<&str> = line.trim().split_whitespace().collect();
                        if parts.len() >= 2 {
                            if let Ok(pid) = parts[0].parse::<u32>() {
                                let comm = parts[1..].join(" ");
                                let lower = comm.to_lowercase();
                                if target_keywords.iter().any(|k| lower.contains(&k.to_lowercase())) {
                                    results.push(DiscoveredProcess {
                                        pid,
                                        name: comm.clone(),
                                        exe_path: comm,
                                        exe_hash: "d41d8cd98f00b204e9800998ecf8427e".to_string(),
                                        matched_game_id: Some("sx-arena".to_string()),
                                    });
                                }
                            }
                        }
                    }
                }
            }
        }

        results
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_process_scan() {
        let candidates = ProcessScanner::scan_candidates(&["sh", "zsh", "python"]);
        assert!(!candidates.is_empty());
    }
}
