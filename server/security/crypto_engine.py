import base64
import hashlib
import hmac
import os
import time

class PolymorphicCryptoEngine:
    """
    Polymorphic Packet Encryption Engine
    
    Prevents packet-sniffing cheats from creating custom server emulators by dynamically
    rotating keystreams using session-specific ephemeral seeds, rolling packet sequence counters,
    and HMAC integrity tags.
    """
    def __init__(self, session_seed=None):
        self.session_seed = session_seed or os.urandom(32).hex()
        self.packet_counter = 0
        self.master_key = hashlib.sha256(self.session_seed.encode('utf-8')).digest()

    def derive_packet_key(self, seq_id, timestamp):
        # Derive ephemeral polymorphic key per packet
        salt = f"{seq_id}:{timestamp}:{self.session_seed}".encode('utf-8')
        return hashlib.sha256(self.master_key + salt).digest()

    def encrypt_payload(self, plaintext_str):
        self.packet_counter += 1
        now = int(time.time() * 1000)
        seq = self.packet_counter
        
        packet_key = self.derive_packet_key(seq, now)
        data_bytes = plaintext_str.encode('utf-8')
        
        # Keystream XOR cipher
        cipher_bytes = bytearray(len(data_bytes))
        for i in range(len(data_bytes)):
            cipher_bytes[i] = data_bytes[i] ^ packet_key[i % len(packet_key)]
            
        # HMAC-SHA256 integrity tag
        tag = hmac.new(packet_key, cipher_bytes, hashlib.sha256).hexdigest()[:16]
        
        return {
            "seq": seq,
            "ts": now,
            "poly_tag": tag,
            "payload_b64": base64.b64encode(cipher_bytes).decode('utf-8')
        }

    def decrypt_payload(self, packet_dict):
        seq = packet_dict.get("seq", 0)
        ts = packet_dict.get("ts", 0)
        tag = packet_dict.get("poly_tag", "")
        payload_b64 = packet_dict.get("payload_b64", "")
        
        if not payload_b64:
            return None, "EMPTY_PAYLOAD"
            
        cipher_bytes = base64.b64decode(payload_b64)
        packet_key = self.derive_packet_key(seq, ts)
        
        # Validate HMAC tag
        expected_tag = hmac.new(packet_key, cipher_bytes, hashlib.sha256).hexdigest()[:16]
        if not hmac.compare_digest(tag, expected_tag):
            return None, "HMAC_INTEGRITY_FAILURE_PACKET_TAMPERED"
            
        # Decrypt
        plain_bytes = bytearray(len(cipher_bytes))
        for i in range(len(cipher_bytes)):
            plain_bytes[i] = cipher_bytes[i] ^ packet_key[i % len(packet_key)]
            
        return plain_bytes.decode('utf-8'), "OK"
