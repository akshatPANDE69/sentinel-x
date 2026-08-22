import math
import time

class MultiVectorEvidenceEngine:
    AUTHORITATIVE_CLEAN_HASH = "d41d8cd98f00b204e9800998ecf8427e"

    def __init__(self):
        self.last_eval_time = {}

    def evaluate_telemetry(self, player, raw_packet, obstacles, all_players):
        """
        Evaluates 3 orthogonal telemetry vectors:
        1. Integrity Vector (Memory hashes, hook flags, clock drift)
        2. Behavioral Vector (Aim jerk, impossible velocity, occlusion aim)
        3. Server State Vector (Position discrepancy, health freeze)
        """
        now = time.time()
        pid = player.id
        
        # 1. INTEGRITY VECTOR
        client_mem_hash = raw_packet.get("memory_hash", player.simulated_memory_hash)
        memory_intact = (client_mem_hash == self.AUTHORITATIVE_CLEAN_HASH)
        hook_detected = raw_packet.get("has_vmt_hook", player.has_vmt_hook)
        dll_injected = raw_packet.get("has_dll_injected", player.has_dll_injected)
        clock_drift = raw_packet.get("clock_drift", player.clock_drift_factor)
        
        integrity_penalty = 0.0
        integrity_flags = []
        if not memory_intact:
            integrity_penalty += 0.60
            integrity_flags.append("MEM_TAMPER_PAGE_HASH_MISMATCH")
        if hook_detected:
            integrity_penalty += 0.55
            integrity_flags.append("VMT_HOOK_SIGNATURE_DETECTED")
        if dll_injected:
            integrity_penalty += 0.50
            integrity_flags.append("UNVERIFIED_MODULE_INJECTION")
        if clock_drift > 1.3:
            integrity_penalty += min(0.50, (clock_drift - 1.0) * 0.35)
            integrity_flags.append(f"CLOCK_SKEW_SPEEDHACK_{clock_drift:.1f}x")

        # 2. BEHAVIORAL VECTOR
        aim_jerk = raw_packet.get("aim_jerk", 0.0)
        speed_claimed = raw_packet.get("speed_multiplier", player.speed_multiplier)
        aiming_at_occluded = False
        
        # Check if aiming directly at an occluded enemy
        player_angle = raw_packet.get("angle", player.angle)
        for other in all_players.values():
            if other.id != player.id and not other.is_quarantined:
                dx = other.x - player.x
                dy = other.y - player.y
                dist = math.hypot(dx, dy)
                if 40.0 < dist < 450.0:
                    angle_to_other = math.atan2(dy, dx)
                    angle_diff = abs((player_angle - angle_to_other + math.pi) % (2 * math.pi) - math.pi)
                    if angle_diff < 0.12:  # within ~7 degrees
                        # Check ray intersection with obstacles
                        is_blocked = any(obs.intersects_ray(player.x, player.y, other.x, other.y) for obs in obstacles)
                        if is_blocked and raw_packet.get("wallhack_active", player.wallhack_active):
                            aiming_at_occluded = True
                            break

        behavior_penalty = 0.0
        behavior_flags = []
        if aim_jerk > 450.0:  # degrees per sec^2
            behavior_penalty += min(0.45, (aim_jerk - 450.0) / 1000.0 + 0.20)
            behavior_flags.append(f"AIMBOT_ANGULAR_JERK_{int(aim_jerk)}deg/s2")
        if speed_claimed > 1.5:
            behavior_penalty += min(0.40, (speed_claimed - 1.0) * 0.25)
            behavior_flags.append(f"IMPOSSIBLE_VELOCITY_VECTOR_{speed_claimed:.1f}x")
        if aiming_at_occluded:
            behavior_penalty += 0.35
            behavior_flags.append("OCCLUDED_ESP_RAYCAST_VIOLATION")

        # 3. SERVER STATE VECTOR
        claimed_health = raw_packet.get("health", player.health)
        server_penalty = 0.0
        server_flags = []
        if claimed_health > player.health + 5 and player.health < 100:
            server_penalty += 0.45
            server_flags.append(f"HEALTH_FREEZE_TAMPER_{claimed_health}HP")

        total_penalty = min(1.0, integrity_penalty + behavior_penalty + server_penalty)
        all_flags = integrity_flags + behavior_flags + server_flags

        return {
            "timestamp": now,
            "player_id": pid,
            "total_penalty": total_penalty,
            "integrity_penalty": integrity_penalty,
            "behavior_penalty": behavior_penalty,
            "server_penalty": server_penalty,
            "flags": all_flags,
            "is_clean": len(all_flags) == 0,
            "metrics": {
                "memory_intact": memory_intact,
                "clock_drift": clock_drift,
                "aim_jerk": aim_jerk,
                "speed_multiplier": speed_claimed,
                "aiming_at_occluded": aiming_at_occluded
            }
        }
