import asyncio
import math
import os
import random
import subprocess
import time
import uuid

from server.engine.entity import Player, Projectile, Obstacle
from server.engine.checkpoint import StateCheckpoint, CircularCheckpointBuffer
from server.security.evidence import MultiVectorEvidenceEngine
from server.security.trust import DynamicTrustEngine, TrustState
from server.security.recovery import AutonomousRecoveryEngine

class AuthoritativeGameServer:
    def __init__(self, tick_rate=60):
        self.tick_rate = tick_rate
        self.tick_interval = 1.0 / tick_rate
        self.width = 1200
        self.height = 760
        self.frame_id = 0
        self.running = False
        
        # Game State
        self.players = {}     # player_id -> Player
        self.projectiles = {} # proj_id -> Projectile
        self.obstacles = self._init_arena_obstacles()
        
        # Security & Checkpoints
        self.checkpoint_buffer = CircularCheckpointBuffer(capacity=600)
        self.evidence_engine = MultiVectorEvidenceEngine()
        self.trust_engine = DynamicTrustEngine()
        self.recovery_engine = AutonomousRecoveryEngine(self.checkpoint_buffer, self.trust_engine)
        
        # Event Queues & Broadcasters
        self.broadcast_callbacks = []
        self.soc_callbacks = []
        self.pending_inputs = {} # player_id -> list of input packets
        
        # Native Vector Scanner Path
        self.scanner_bin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "agent", "native", "vector_scanner"))
        self.last_simd_scan_result = {
            "status": "READY",
            "throughput_gbs": 5.8,
            "simd_engine": "ARM_NEON_128 / AVX2_256",
            "matches": 0,
            "scanned_mb": 128
        }
        
        # Spawn some friendly/enemy AI Sentinel Bots
        self._spawn_ai_sentinels()

    def _init_arena_obstacles(self):
        obs = [
            Obstacle(0, 0, 1200, 20, "wall", "#0f172a"),
            Obstacle(0, 740, 1200, 20, "wall", "#0f172a"),
            Obstacle(0, 0, 20, 760, "wall", "#0f172a"),
            Obstacle(1180, 0, 20, 760, "wall", "#0f172a"),
            
            Obstacle(520, 280, 160, 200, "vault", "#1e293b"),
            Obstacle(240, 160, 120, 40, "cover", "#334155"),
            Obstacle(840, 160, 120, 40, "cover", "#334155"),
            Obstacle(240, 560, 120, 40, "cover", "#334155"),
            Obstacle(840, 560, 120, 40, "cover", "#334155"),
            Obstacle(180, 340, 40, 100, "pillar", "#475569"),
            Obstacle(980, 340, 40, 100, "pillar", "#475569")
        ]
        return obs

    def _spawn_ai_sentinels(self):
        bots = [
            ("bot-alpha", "SENTINEL-UNIT-ALPHA", 300, 300, "#ffaa00"),
            ("bot-bravo", "SENTINEL-UNIT-BRAVO", 900, 300, "#ff5500"),
            ("bot-gamma", "SENTINEL-UNIT-GAMMA", 600, 620, "#aa00ff")
        ]
        for bid, name, bx, by, color in bots:
            bot = Player(bid, name, bx, by, color=color, is_bot=True)
            self.players[bid] = bot
            self.trust_engine.register_player(bid)

    def add_player(self, player_id, name="CYBER_OPERATOR"):
        px = random.uniform(100, 220)
        py = random.uniform(200, 500)
        p = Player(player_id, name, px, py, color="#00ffcc", is_bot=False)
        self.players[player_id] = p
        self.trust_engine.register_player(player_id)
        return p

    def remove_player(self, player_id):
        self.players.pop(player_id, None)
        self.trust_engine.unregister_player(player_id)
        self.pending_inputs.pop(player_id, None)

    def queue_input(self, player_id, input_packet):
        self.pending_inputs.setdefault(player_id, []).append(input_packet)

    def trigger_cheat_injection(self, player_id, cheat_type, enabled=True):
        player = self.players.get(player_id)
        if not player:
            return False
            
        if cheat_type == "speedhack":
            player.speed_multiplier = 3.5 if enabled else 1.0
            player.clock_drift_factor = 3.5 if enabled else 1.0
        elif cheat_type == "aimbot":
            pass
        elif cheat_type == "memory_tamper":
            player.simulated_memory_hash = "DEADBEEF_CORRUPTED_HASH" if enabled else "d41d8cd98f00b204e9800998ecf8427e"
        elif cheat_type == "vmt_hook":
            player.has_vmt_hook = enabled
        elif cheat_type == "dll_inject":
            player.has_dll_injected = enabled
        elif cheat_type == "wallhack":
            player.wallhack_active = enabled
        elif cheat_type == "handle_strip":
            player.handle_stripped = enabled
        elif cheat_type == "remote_thread":
            player.remote_thread_injected = enabled
        elif cheat_type == "nmi_unbacked":
            player.nmi_unbacked_trap = enabled
            player.last_nmi_rip_address = "0x00007FF7DEADBEEF [UNBACKED_SHELLCODE]" if enabled else "0x00007FF689AB1200 [ntdll.dll]"
        elif cheat_type == "simd_scan":
            player.simd_signature_match = enabled
            if enabled:
                self.run_simd_scan()
        return True

    def run_simd_scan(self):
        try:
            if os.path.exists(self.scanner_bin):
                out = subprocess.check_output([self.scanner_bin], timeout=2.0)
                import json
                self.last_simd_scan_result = json.loads(out.decode('utf-8'))
        except Exception:
            pass
        return self.last_simd_scan_result

    async def run_loop(self):
        self.running = True
        last_time = time.time()
        
        while self.running:
            now = time.time()
            dt = now - last_time
            last_time = now
            
            self.frame_id += 1
            
            # 1. Process client inputs & update players
            self._update_players(dt)
            
            # 2. Update AI Bots
            self._update_bots(dt)
            
            # 3. Update projectiles & collisions
            self._update_projectiles(dt)
            
            # 4. Security Attestation & Multi-Vector Evidence
            self._evaluate_security()
            
            # 5. Record Authoritative Merkle Checkpoint
            self._record_checkpoint()
            
            # 6. Broadcast World State & SOC Telemetry
            if self.frame_id % 2 == 0:  # 30 Hz
                await self._broadcast_world_state()
            if self.frame_id % 3 == 0:  # 20 Hz
                await self._broadcast_soc_telemetry()
                
            elapsed = time.time() - now
            sleep_time = max(0.001, self.tick_interval - elapsed)
            await asyncio.sleep(sleep_time)

    def _update_players(self, dt):
        for pid, player in list(self.players.items()):
            if player.is_bot:
                continue
                
            inputs = self.pending_inputs.get(pid, [])
            self.pending_inputs[pid] = []
            
            if player.is_quarantined:
                continue
                
            if inputs:
                latest = inputs[-1]
                dx = latest.get("dx", 0)
                dy = latest.get("dy", 0)
                player.angle = latest.get("angle", player.angle)
                
                # Ingest client telemetry from signed packet
                if "memory_hash" in latest:
                    player.simulated_memory_hash = latest["memory_hash"]
                if "has_vmt_hook" in latest:
                    player.has_vmt_hook = latest["has_vmt_hook"]
                if "has_dll_injected" in latest:
                    player.has_dll_injected = latest["has_dll_injected"]
                if "clock_drift" in latest:
                    player.clock_drift_factor = float(latest["clock_drift"])
                if "wallhack_active" in latest:
                    player.wallhack_active = bool(latest["wallhack_active"])
                if "aim_jerk" in latest:
                    player.aim_jerk_history.append(float(latest["aim_jerk"]))
                    if len(player.aim_jerk_history) > 15:
                        player.aim_jerk_history.pop(0)
                        
                # Ring 0 Kernel telemetry fields
                if "handle_stripped" in latest:
                    player.handle_stripped = bool(latest["handle_stripped"])
                if "remote_thread_injected" in latest:
                    player.remote_thread_injected = bool(latest["remote_thread_injected"])
                if "nmi_unbacked_trap" in latest:
                    player.nmi_unbacked_trap = bool(latest["nmi_unbacked_trap"])
                if "simd_signature_match" in latest:
                    player.simd_signature_match = bool(latest["simd_signature_match"])

                # Apply speed
                speed = 220.0 * player.speed_multiplier
                player.vx = dx * speed
                player.vy = dy * speed
                
                if latest.get("shoot", False):
                    self._fire_projectile(player)

            new_x = player.x + player.vx * dt
            new_y = player.y + player.vy * dt
            
            if not self._check_obstacle_collision(new_x, player.y, player.radius):
                player.x = max(player.radius, min(self.width - player.radius, new_x))
            if not self._check_obstacle_collision(player.x, new_y, player.radius):
                player.y = max(player.radius, min(self.height - player.radius, new_y))

    def _update_bots(self, dt):
        now = time.time()
        for player in self.players.values():
            if not player.is_bot:
                continue
            human = next((p for p in self.players.values() if not p.is_bot and not p.is_quarantined), None)
            if human:
                dx = human.x - player.x
                dy = human.y - player.y
                dist = math.hypot(dx, dy)
                player.angle = math.atan2(dy, dx)
                
                if dist > 250:
                    player.vx = (dx / dist) * 120.0
                    player.vy = (dy / dist) * 120.0
                else:
                    player.vx = (-dy / dist) * 90.0
                    player.vy = (dx / dist) * 90.0
                    
                has_los = not any(obs.intersects_ray(player.x, player.y, human.x, human.y) for obs in self.obstacles)
                if has_los and (now - player.last_shot_time) > 1.8:
                    self._fire_projectile(player)
            else:
                player.vx = math.cos(now + float(hash(player.id) % 10)) * 60.0
                player.vy = math.sin(now + float(hash(player.id) % 10)) * 60.0
                
            new_x = player.x + player.vx * dt
            new_y = player.y + player.vy * dt
            if not self._check_obstacle_collision(new_x, player.y, player.radius):
                player.x = max(player.radius, min(self.width - player.radius, new_x))
            if not self._check_obstacle_collision(player.x, new_y, player.radius):
                player.y = max(player.radius, min(self.height - player.radius, new_y))

    def _fire_projectile(self, player):
        now = time.time()
        if (now - player.last_shot_time) < 0.18:
            return
        player.last_shot_time = now
        
        proj_id = f"proj-{uuid.uuid4().hex[:8]}"
        speed = 520.0
        vx = math.cos(player.angle) * speed
        vy = math.sin(player.angle) * speed
        
        sx = player.x + math.cos(player.angle) * (player.radius + 6)
        sy = player.y + math.sin(player.angle) * (player.radius + 6)
        
        p = Projectile(proj_id, player.id, sx, sy, vx, vy, damage=20, color=player.color)
        self.projectiles[proj_id] = p

    def _update_projectiles(self, dt):
        for pid, proj in list(self.projectiles.items()):
            proj.update(dt)
            if proj.x < 0 or proj.x > self.width or proj.y < 0 or proj.y > self.height or proj.is_expired():
                self.projectiles.pop(pid, None)
                continue
                
            hit_obs = any(obs.collides_with_circle(proj.x, proj.y, proj.radius) for obs in self.obstacles)
            if hit_obs:
                self.projectiles.pop(pid, None)
                continue
                
            for pl in self.players.values():
                if pl.id != proj.owner_id and not pl.is_quarantined:
                    dx = pl.x - proj.x
                    dy = pl.y - proj.y
                    if (dx*dx + dy*dy) < ((pl.radius + proj.radius)**2):
                        pl.health = max(0, pl.health - proj.damage)
                        owner = self.players.get(proj.owner_id)
                        if owner:
                            owner.score += 10
                        self.projectiles.pop(pid, None)
                        
                        if pl.health == 0:
                            pl.health = 100
                            pl.x = random.uniform(100, 1100)
                            pl.y = random.uniform(100, 650)
                        break

    def _check_obstacle_collision(self, cx, cy, r):
        return any(obs.collides_with_circle(cx, cy, r) for obs in self.obstacles)

    def _evaluate_security(self):
        for player in self.players.values():
            if player.is_bot:
                continue
                
            packet = {
                "memory_hash": player.simulated_memory_hash,
                "has_vmt_hook": player.has_vmt_hook,
                "has_dll_injected": player.has_dll_injected,
                "clock_drift": player.clock_drift_factor,
                "speed_multiplier": player.speed_multiplier,
                "angle": player.angle,
                "aim_jerk": player.aim_jerk_history[-1] if player.aim_jerk_history else 0.0,
                "wallhack_active": player.wallhack_active,
                "health": player.health,
                # Kernel telemetry
                "handle_stripped": player.handle_stripped,
                "remote_thread_injected": player.remote_thread_injected,
                "nmi_unbacked_trap": player.nmi_unbacked_trap,
                "simd_signature_match": player.simd_signature_match
            }
            
            ev = self.evidence_engine.evaluate_telemetry(player, packet, self.obstacles, self.players)
            new_score, state, event = self.trust_engine.update_with_evidence(player.id, ev)
            
            if state == TrustState.COMPROMISED and not player.is_quarantined:
                self.recovery_engine.initiate_recovery(player, trigger_reason="TRUST_SCORE_COLLAPSE")

    def _record_checkpoint(self):
        now = time.time()
        p_snaps = {pid: p.copy_snapshot() for pid, p in self.players.items()}
        pr_snaps = [pr.to_dict() for pr in self.projectiles.values()]
        t_scores = {pid: self.trust_engine.get_trust_score(pid) for pid in self.players}
        
        human_p = next((p for p in self.players.values() if not p.is_bot), None)
        is_verified = True
        if human_p:
            is_verified = (self.trust_engine.get_trust_score(human_p.id) >= 0.85)
            
        cp = StateCheckpoint(self.frame_id, now, p_snaps, pr_snaps, t_scores, is_verified=is_verified)
        self.checkpoint_buffer.push(cp)

    async def _broadcast_world_state(self):
        world_msg = {
            "type": "WORLD_STATE",
            "frame_id": self.frame_id,
            "timestamp": time.time(),
            "players": [p.to_dict() for p in self.players.values()],
            "projectiles": [pr.to_dict() for pr in self.projectiles.values()]
        }
        for cb in self.broadcast_callbacks:
            try:
                await cb(world_msg)
            except Exception:
                pass

    async def _broadcast_soc_telemetry(self):
        human_p = next((p for p in self.players.values() if not p.is_bot), None)
        if not human_p:
            return
            
        pid = human_p.id
        ts = self.trust_engine.get_trust_score(pid)
        state = self.trust_engine.get_trust_state(pid)
        recovery_active = (pid in self.recovery_engine.active_recoveries)
        rec_info = self.recovery_engine.active_recoveries.get(pid, None)
        
        soc_msg = {
            "type": "SOC_TELEMETRY",
            "frame_id": self.frame_id,
            "timestamp": time.time(),
            "player_id": pid,
            "player_name": human_p.name,
            "trust_score": round(ts, 3),
            "trust_state": state,
            "is_quarantined": human_p.is_quarantined,
            "recovery_active": recovery_active,
            "recovery_info": rec_info,
            "recent_checkpoints": self.checkpoint_buffer.get_recent_summaries(limit=8),
            "telemetry_metrics": {
                "memory_hash": human_p.simulated_memory_hash,
                "memory_intact": (human_p.simulated_memory_hash == "d41d8cd98f00b204e9800998ecf8427e"),
                "has_vmt_hook": human_p.has_vmt_hook,
                "has_dll_injected": human_p.has_dll_injected,
                "clock_drift": round(human_p.clock_drift_factor, 2),
                "speed_multiplier": round(human_p.speed_multiplier, 2),
                "aim_jerk": human_p.aim_jerk_history[-1] if human_p.aim_jerk_history else 0.0,
                "wallhack_active": human_p.wallhack_active,
                # Ring 0 Kernel Metrics
                "handle_stripped": human_p.handle_stripped,
                "remote_thread_injected": human_p.remote_thread_injected,
                "nmi_unbacked_trap": human_p.nmi_unbacked_trap,
                "nmi_rip_address": human_p.last_nmi_rip_address,
                "simd_signature_match": human_p.simd_signature_match,
                "simd_throughput_gbs": self.last_simd_scan_result.get("throughput_gbs", 5.8),
                "simd_engine": self.last_simd_scan_result.get("simd_engine", "ARM_NEON_128")
            }
        }
        for cb in self.soc_callbacks:
            try:
                await cb(soc_msg)
            except Exception:
                pass
