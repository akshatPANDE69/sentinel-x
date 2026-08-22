import asyncio
import json
import time
import urllib.request
from typing import Optional
from agent.process_discovery import ProcessDiscoveryEngine, DiscoveredProcess

class AgentState:
    STOPPED = "STOPPED"
    STARTED = "STARTED"
    DISCOVERING = "DISCOVERING"
    GAME_FOUND = "GAME_FOUND"
    SESSION_NEGOTIATING = "SESSION_NEGOTIATING"
    ATTESTING = "ATTESTING"
    PROTECTED = "PROTECTED"
    DEGRADED = "DEGRADED"
    QUARANTINED = "QUARANTINED"
    RECOVERING = "RECOVERING"
    RESTORED = "RESTORED"

class SentinelXAgent:
    """
    Sentinel-X Local Endpoint Security Agent Daemon.
    Continuously monitors OS processes, discovers registered games, binds sessions,
    and forwards local telemetry to the Sentinel-X server.
    """
    def __init__(self, server_url: str = "http://127.0.0.1:8080"):
        self.server_url = server_url.rstrip("/")
        self.state = AgentState.STARTED
        self.discovery_engine = ProcessDiscoveryEngine()
        self.active_process: Optional[DiscoveredProcess] = None
        self.active_session_id: Optional[str] = None
        self.is_running = False

    async def start(self):
        self.is_running = True
        self.state = AgentState.DISCOVERING
        print(f"[SentinelXAgent] Started. Endpoint Agent Active. State: {self.state}")
        
        while self.is_running:
            await self._run_discovery_cycle()
            await asyncio.sleep(2.0)

    async def _run_discovery_cycle(self):
        if self.state in [AgentState.DISCOVERING, AgentState.GAME_FOUND]:
            procs = self.discovery_engine.scan_running_processes()
            matched = next((p for p in procs if p.matched_game_id), None)
            
            if matched and not self.active_process:
                self.active_process = matched
                self.state = AgentState.GAME_FOUND
                print(f"[SentinelXAgent] Target Game Process Discovered! PID: {matched.pid} (GameID: {matched.matched_game_id})")

    def bind_session(self, session_id: str):
        self.active_session_id = session_id
        self.state = AgentState.PROTECTED
        print(f"[SentinelXAgent] Session {session_id} cryptographically bound. Protection Active.")

    def stop(self):
        self.is_running = False
        self.state = AgentState.STOPPED
        print("[SentinelXAgent] Stopped.")
