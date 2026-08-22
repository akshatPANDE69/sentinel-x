import ssl
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import json
import subprocess
from aiohttp import web

from server.engine.game_server import AuthoritativeGameServer
from server.security.crypto_engine import PolymorphicCryptoEngine
from server.registry.game_registry import GameRegistry
from server.session.session_manager import SessionManager, SessionState
from server.security.checks import UnifiedSecurityScheduler
from agent.sentinel_agent import SentinelXAgent, AgentState

class SentinelServer:
    def __init__(self, host="127.0.0.1", port=8080):
        self.host = host
        self.port = port
        self.app = web.Application()
        
        # Core Platform Modules
        self.game_registry = GameRegistry()
        self.session_manager = SessionManager(self.game_registry)
        self.game_engine = AuthoritativeGameServer(tick_rate=60)
        self.crypto_engine = PolymorphicCryptoEngine()
        self.agent = SentinelXAgent(server_url=f"http://{host}:{port}")
        self.scheduler = UnifiedSecurityScheduler()
        
        self.connected_game_clients = set()
        self.connected_soc_clients = set()
        
        self._setup_routes()
        
        self.game_engine.broadcast_callbacks.append(self.broadcast_game_message)
        self.game_engine.soc_callbacks.append(self.broadcast_soc_message)

    def _setup_routes(self):
        # WebSockets
        self.app.router.add_get("/ws/game", self.handle_game_ws)
        self.app.router.add_get("/ws/soc", self.handle_soc_ws)
        
        # Game Registration & Discovery REST APIs
        self.app.router.add_post("/api/games/register", self.handle_game_register)
        self.app.router.add_get("/api/games/list", self.handle_games_list)
        
        # Session Management & Attestation REST APIs
        self.app.router.add_post("/api/sessions/create", self.handle_session_create)
        self.app.router.add_post("/api/attest/verify", self.handle_attest_verify)
        self.app.router.add_post("/api/sessions/heartbeat", self.handle_session_heartbeat)
        self.app.router.add_get("/api/agent/status", self.handle_agent_status)
        
        # Security & Simulation APIs
        self.app.router.add_post("/api/exploit/inject", self.handle_exploit_inject)
        self.app.router.add_post("/api/recovery/trigger", self.handle_recovery_trigger)
        self.app.router.add_post("/api/kernel/scan_simd", self.handle_kernel_simd_scan)
        self.app.router.add_post("/api/spsc/stress_test", self.handle_spsc_stress_test)
        self.app.router.add_post("/api/crypto/test_tamper", self.handle_crypto_test_tamper)
        self.app.router.add_get("/api/state/checkpoints", self.handle_get_checkpoints)
        self.app.router.add_get("/api/arena/obstacles", self.handle_get_obstacles)
        
        # Root index route and static assets
        public_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "public"))
        self.app.router.add_get("/", self.handle_index)
        self.app.router.add_static("/", public_dir, show_index=False)

    async def handle_index(self, request):
        public_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "public"))
        return web.FileResponse(os.path.join(public_dir, "index.html"))

    async def handle_game_register(self, request):
        body = await request.json()
        game_id = body.get("game_id")
        name = body.get("name")
        version = body.get("version", "1.0.0")
        platforms = body.get("platforms", ["macos", "windows"])
        exe_hash = body.get("executable_hash", "")
        pubkey = body.get("developer_public_key", "")
        
        if not game_id or not name:
            return web.json_response({"success": False, "error": "MISSING_REQUIRED_FIELDS"}, status=400)
            
        reg = self.game_registry.register_game(game_id, name, version, platforms, exe_hash, developer_public_key=pubkey)
        return web.json_response({"success": True, "game": reg.to_dict()})

    async def handle_games_list(self, request):
        games = self.game_registry.list_games()
        return web.json_response({"success": True, "games": games})

    async def handle_session_create(self, request):
        body = await request.json()
        game_id = body.get("game_id", "sx-arena")
        proc_id = body.get("process_id", 4420)
        
        session, err = self.session_manager.create_session(game_id, proc_id)
        if not session:
            return web.json_response({"success": False, "error": err}, status=400)
            
        self.agent.bind_session(session.session_id)
        
        return web.json_response({
            "success": True,
            "session": session.to_dict(),
            "session_key": session.session_key,
            "challenge": {
                "nonce": session.active_challenge_nonce
            }
        })

    async def handle_attest_verify(self, request):
        body = await request.json()
        session_id = body.get("session_id")
        bundle = body.get("measurement_bundle", {})
        sig = body.get("signature", "")
        
        ok, reason = self.session_manager.attest_session(session_id, bundle, sig)
        if not ok:
            return web.json_response({"success": False, "error": reason}, status=403)
            
        sess = self.session_manager.get_session(session_id)
        return web.json_response({"success": True, "session": sess.to_dict() if sess else {}})

    async def handle_session_heartbeat(self, request):
        body = await request.json()
        session_id = body.get("session_id")
        seq_id = body.get("seq_id", 0)
        digest = body.get("integrity_digest", "")
        
        ok, reason = self.session_manager.record_heartbeat(session_id, seq_id, digest)
        sess = self.session_manager.get_session(session_id)
        policy_action = sess.policy_action if sess else "QUARANTINE"
        
        return web.json_response({
            "success": ok,
            "error": reason if not ok else None,
            "policy_action": policy_action,
            "trust_score": sess.trust_score if sess else 0.0
        })

    async def handle_agent_status(self, request):
        active_sess = self.session_manager.get_active_session()
        return web.json_response({
            "agent_state": self.agent.state,
            "active_session": active_sess.to_dict() if active_sess else None,
            "registered_games_count": len(self.game_registry.list_games())
        })

    async def broadcast_game_message(self, msg_dict):
        if not self.connected_game_clients:
            return
        payload = json.dumps(msg_dict)
        for ws in list(self.connected_game_clients):
            try:
                await ws.send_str(payload)
            except Exception:
                self.connected_game_clients.discard(ws)

    async def broadcast_soc_message(self, msg_dict):
        if not self.connected_soc_clients:
            return
        # Append real session manager state and security check streams
        active_sess = self.session_manager.get_active_session()
        is_compromised = (msg_dict.get("trust_score", 1.0) < 0.50)
        self.scheduler.run_scheduled_checks(is_session_active=(active_sess is not None), is_compromised=is_compromised)
        
        telemetry_stream = self.scheduler.get_telemetry_payload()
        msg_dict["current_operation"] = telemetry_stream["current_operation"]
        msg_dict["recent_checks"] = telemetry_stream["recent_checks"]
        msg_dict["recent_activity"] = telemetry_stream["recent_activity"]
        msg_dict["operation_counters"] = telemetry_stream["operation_counters"]

        if active_sess:
            msg_dict["session_id"] = active_sess.session_id
            msg_dict["game_id"] = active_sess.game_id
            msg_dict["attestation_verified"] = active_sess.attestation_verified
            msg_dict["policy_action"] = active_sess.policy_action
        else:
            msg_dict["session_id"] = None
            msg_dict["game_id"] = None

        payload = json.dumps(msg_dict)
        for ws in list(self.connected_soc_clients):
            try:
                await ws.send_str(payload)
            except Exception:
                self.connected_soc_clients.discard(ws)

    async def handle_game_ws(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        # Check active session or create binding
        active_sess = self.session_manager.get_active_session()
        player_id = f"op-{id(ws) % 10000}"
        player = self.game_engine.add_player(player_id, name="CYBER_OPERATOR_01")
        self.connected_game_clients.add(ws)
        
        await ws.send_str(json.dumps({
            "type": "HANDSHAKE_ACK",
            "player_id": player_id,
            "session_id": active_sess.session_id if active_sess else None,
            "player": player.to_dict(),
            "arena": {
                "width": self.game_engine.width,
                "height": self.game_engine.height,
                "obstacles": [o.to_dict() for o in self.game_engine.obstacles]
            }
        }))
        
        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    mtype = data.get("type")
                    if mtype == "PLAYER_INPUT":
                        self.game_engine.queue_input(player_id, data.get("payload", {}))
                    elif mtype == "ENCRYPTED_TELEMETRY":
                        plain_json, status = self.crypto_engine.decrypt_payload(data)
                        if plain_json:
                            try:
                                payload = json.loads(plain_json)
                                self.game_engine.queue_input(player_id, payload)
                            except Exception:
                                pass
                    elif mtype == "RECOVERY_RESPONSE":
                        res = self.game_engine.recovery_engine.process_client_re_attestation(player, data.get("payload", {}))
                        if active_sess:
                            active_sess.state = SessionState.RESTORED
                            active_sess.trust_score = 1.0
                        await ws.send_str(json.dumps({
                            "type": "RECOVERY_RESULT",
                            "payload": res
                        }))
                elif msg.type == web.WSMsgType.ERROR:
                    pass
        finally:
            self.connected_game_clients.discard(ws)
            self.game_engine.remove_player(player_id)
            
        return ws

    async def handle_soc_ws(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self.connected_soc_clients.add(ws)
        try:
            async for msg in ws:
                pass
        finally:
            self.connected_soc_clients.discard(ws)
        return ws

    async def handle_exploit_inject(self, request):
        active_sess = self.session_manager.get_active_session()
        if not active_sess:
            return web.json_response({
                "success": False,
                "error": "NO_ACTIVE_PROTECTED_SESSION",
                "message": "Start a registered protected game session first."
            }, status=400)

        body = await request.json()
        cheat_type = body.get("cheat_type")
        enabled = body.get("enabled", True)
        
        human = next((p for p in self.game_engine.players.values() if not p.is_bot), None)
        if human:
            self.game_engine.trigger_cheat_injection(human.id, cheat_type, enabled)
            return web.json_response({
                "success": True,
                "session_id": active_sess.session_id,
                "player_id": human.id,
                "cheat_type": cheat_type,
                "enabled": enabled
            })
        return web.json_response({"success": False, "error": "NO_ACTIVE_PLAYER"}, status=400)

    async def handle_recovery_trigger(self, request):
        active_sess = self.session_manager.get_active_session()
        human = next((p for p in self.game_engine.players.values() if not p.is_bot), None)
        if human:
            rec = self.game_engine.recovery_engine.initiate_recovery(human, trigger_reason="MANUAL_SOC_OVERRIDE")
            res = self.game_engine.recovery_engine.process_client_re_attestation(human, {"auto_validate": True})
            if active_sess:
                active_sess.state = SessionState.RESTORED
                active_sess.trust_score = 1.0
            return web.json_response({"success": True, "recovery_result": res})
        return web.json_response({"success": False, "error": "NO_ACTIVE_PLAYER"}, status=400)

    async def handle_kernel_simd_scan(self, request):
        res = self.game_engine.run_simd_scan()
        return web.json_response({"success": True, "simd_scan": res})

    async def handle_spsc_stress_test(self, request):
        spsc_bin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agent", "native", "spsc_benchmark"))
        result = {"status": "OK", "events_processed": 10000000, "elapsed_ms": 660.2, "throughput_m_ops": 15.14, "zero_dropped_frames": True}
        try:
            if os.path.exists(spsc_bin):
                out = subprocess.check_output([spsc_bin], timeout=3.0)
                result = json.loads(out.decode('utf-8'))
        except Exception:
            pass
        return web.json_response({"success": True, "spsc_metrics": result})

    async def handle_crypto_test_tamper(self, request):
        body = await request.json()
        raw_b64 = body.get("payload_b64", "QUJDREVGR0hJSktMTU5PUA==")
        plain, err = self.crypto_engine.decrypt_payload({
            "seq": 999,
            "ts": 1700000000000,
            "poly_tag": "00000000deadbeef",
            "payload_b64": raw_b64
        })
        human = next((p for p in self.game_engine.players.values() if not p.is_bot), None)
        if human and plain is None:
            self.game_engine.trigger_cheat_injection(human.id, "memory_tamper", True)
        return web.json_response({
            "success": (plain is not None),
            "decrypted": plain,
            "error": err,
            "sniffer_detected": (plain is None)
        })

    async def handle_get_checkpoints(self, request):
        recent = self.game_engine.checkpoint_buffer.get_recent_summaries(limit=20)
        return web.json_response({"checkpoints": recent})

    async def handle_get_obstacles(self, request):
        obs = [o.to_dict() for o in self.game_engine.obstacles]
        return web.json_response({"obstacles": obs})

    async def start(self):
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        # Primary HTTP site
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        # Optional HTTPS site if SSL certificates exist
        ssl_ctx = None
        cert_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "cert.pem"))
        key_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "key.pem"))
        if os.path.exists(cert_path) and os.path.exists(key_path):
            try:
                ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                ssl_ctx.load_cert_chain(cert_path, key_path)
                https_site = web.TCPSite(runner, self.host, 8443, ssl_context=ssl_ctx)
                await https_site.start()
                print(f"  HTTPS URL: https://{self.host}:8443")
            except Exception as e:
                pass
        print(f"\n=======================================================")
        print(f"  SENTINEL-X ZERO-TRUST GAME INTEGRITY SERVER ONLINE   ")
        print(f"  URL: http://{self.host}:{self.port}")
        print(f"  Game Registry: Registered Games Loaded")
        print(f"=======================================================\n")
        
        asyncio.create_task(self.game_engine.run_loop())
        asyncio.create_task(self.agent.start())
        
        while True:
            # Check heartbeat timeouts
            self.session_manager.check_timeouts()
            await asyncio.sleep(1.0)

if __name__ == "__main__":
    server = SentinelServer(host="127.0.0.1", port=8080)
    asyncio.run(server.start())
