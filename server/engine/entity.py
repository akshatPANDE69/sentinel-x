import math
import time
import uuid

class Player:
    def __init__(self, player_id, name, x, y, color="#00ffcc", is_bot=False):
        self.id = player_id
        self.name = name
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 16.0
        self.health = 100
        self.max_health = 100
        self.angle = 0.0  # radians
        self.score = 0
        self.color = color
        self.is_bot = is_bot
        self.speed_multiplier = 1.0
        self.last_shot_time = 0.0
        self.is_quarantined = False
        self.aim_jerk_history = []
        self.simulated_memory_hash = "d41d8cd98f00b204e9800998ecf8427e"
        self.has_vmt_hook = False
        self.has_dll_injected = False
        self.clock_drift_factor = 1.0
        self.wallhack_active = False

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "x": round(self.x, 2),
            "y": round(self.y, 2),
            "vx": round(self.vx, 2),
            "vy": round(self.vy, 2),
            "radius": self.radius,
            "health": self.health,
            "max_health": self.max_health,
            "angle": round(self.angle, 3),
            "score": self.score,
            "color": self.color,
            "is_bot": self.is_bot,
            "is_quarantined": self.is_quarantined,
            "speed_multiplier": round(self.speed_multiplier, 2)
        }

    def copy_snapshot(self):
        return {
            "x": self.x,
            "y": self.y,
            "vx": self.vx,
            "vy": self.vy,
            "health": self.health,
            "angle": self.angle,
            "score": self.score,
            "speed_multiplier": self.speed_multiplier,
            "is_quarantined": self.is_quarantined,
            "memory_hash": self.simulated_memory_hash
        }

    def restore_from_snapshot(self, snap):
        self.x = snap["x"]
        self.y = snap["y"]
        self.vx = snap["vx"]
        self.vy = snap["vy"]
        self.health = snap["health"]
        self.angle = snap["angle"]
        self.score = snap["score"]
        self.speed_multiplier = snap.get("speed_multiplier", 1.0)
        self.simulated_memory_hash = snap.get("memory_hash", "d41d8cd98f00b204e9800998ecf8427e")
        self.has_vmt_hook = False
        self.has_dll_injected = False
        self.clock_drift_factor = 1.0
        self.wallhack_active = False


class Projectile:
    def __init__(self, proj_id, owner_id, x, y, vx, vy, damage=25, color="#ff0055"):
        self.id = proj_id
        self.owner_id = owner_id
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.radius = 4.0
        self.damage = damage
        self.color = color
        self.created_at = time.time()
        self.life_time = 2.5  # seconds

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

    def is_expired(self):
        return (time.time() - self.created_at) > self.life_time

    def to_dict(self):
        return {
            "id": self.id,
            "owner_id": self.owner_id,
            "x": round(self.x, 2),
            "y": round(self.y, 2),
            "vx": round(self.vx, 2),
            "vy": round(self.vy, 2),
            "radius": self.radius,
            "damage": self.damage,
            "color": self.color
        }


class Obstacle:
    def __init__(self, x, y, w, h, obs_type="wall", color="#1a2639"):
        self.x = float(x)
        self.y = float(y)
        self.w = float(w)
        self.h = float(h)
        self.type = obs_type
        self.color = color

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "w": self.w,
            "h": self.h,
            "type": self.type,
            "color": self.color
        }

    def collides_with_circle(self, cx, cy, r):
        closest_x = max(self.x, min(cx, self.x + self.w))
        closest_y = max(self.y, min(cy, self.y + self.h))
        dx = cx - closest_x
        dy = cy - closest_y
        return (dx * dx + dy * dy) < (r * r)

    def intersects_ray(self, x1, y1, x2, y2):
        # AABB ray intersection
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0:
            dx = 1e-6
        if dy == 0:
            dy = 1e-6

        t1 = (self.x - x1) / dx
        t2 = (self.x + self.w - x1) / dx
        t3 = (self.y - y1) / dy
        t4 = (self.y + self.h - y1) / dy

        tmin = max(min(t1, t2), min(t3, t4))
        tmax = min(max(t1, t2), max(t3, t4))

        if tmax < 0 or tmin > tmax or tmin > 1.0:
            return False
        return True
