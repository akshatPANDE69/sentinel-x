use hmac::{Hmac, Mac};
use sha2::{Digest, Sha256};

type HmacSha256 = Hmac<Sha256>;

pub struct CryptoEngine;

impl CryptoEngine {
    pub fn sha256_digest(data: &[u8]) -> String {
        let mut hasher = Sha256::new();
        hasher.update(data);
        format!("{:x}", hasher.finalize())
    }

    pub fn compute_hmac(key: &str, message: &str) -> Result<String, String> {
        let mut mac = HmacSha256::new_from_slice(key.as_bytes())
            .map_err(|e| format!("HMAC key initialization failed: {}", e))?;
        mac.update(message.as_bytes());
        let result = mac.finalize();
        Ok(format!("{:x}", result.into_bytes()))
    }

    pub fn verify_hmac(key: &str, message: &str, expected_hex: &str) -> bool {
        match Self::compute_hmac(key, message) {
            Ok(computed) => computed.eq_ignore_ascii_case(expected_hex),
            Err(_) => false,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sha256_and_hmac() {
        let digest = CryptoEngine::sha256_digest(b"sentinel-x");
        assert!(!digest.is_empty());

        let hmac = CryptoEngine::compute_hmac("secret_key", "test_message").unwrap();
        assert!(CryptoEngine::verify_hmac("secret_key", "test_message", &hmac));
        assert!(!CryptoEngine::verify_hmac("wrong_key", "test_message", &hmac));
    }
}
