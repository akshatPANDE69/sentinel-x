import hashlib
import json
import time

def sha256_hash(data_str):
    return hashlib.sha256(data_str.encode('utf-8')).hexdigest()

class MerkleTree:
    @staticmethod
    def build_tree(leaf_data_list):
        if not leaf_data_list:
            return sha256_hash("EMPTY_STATE"), []
        
        leaves = [sha256_hash(json.dumps(d, sort_keys=True)) for d in leaf_data_list]
        tree_levels = [leaves]
        
        current_level = leaves
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i+1] if i+1 < len(current_level) else left
                combined = sha256_hash(left + right)
                next_level.append(combined)
            tree_levels.append(next_level)
            current_level = next_level
            
        root = current_level[0]
        return root, tree_levels


class StateCheckpoint:
    def __init__(self, frame_id, timestamp, player_snapshots, projectile_snapshots, trust_scores, is_verified=True):
        self.frame_id = frame_id
        self.timestamp = timestamp
        self.player_snapshots = player_snapshots  # dict: player_id -> dict
        self.projectile_snapshots = projectile_snapshots
        self.trust_scores = trust_scores          # dict: player_id -> float
        self.is_verified = is_verified
        
        # Build Merkle Root
        entities_data = []
        for pid, ps in sorted(player_snapshots.items()):
            entities_data.append({"type": "player", "id": pid, "state": ps, "trust": trust_scores.get(pid, 1.0)})
        for pr in projectile_snapshots:
            entities_data.append({"type": "projectile", "data": pr})
            
        self.merkle_root, self.merkle_levels = MerkleTree.build_tree(entities_data)

    def to_dict(self, include_tree=False):
        res = {
            "frame_id": self.frame_id,
            "timestamp": round(self.timestamp, 3),
            "merkle_root": self.merkle_root,
            "player_count": len(self.player_snapshots),
            "projectile_count": len(self.projectile_snapshots),
            "is_verified": self.is_verified,
            "trust_scores": {k: round(v, 3) for k, v in self.trust_scores.items()}
        }
        if include_tree:
            res["merkle_levels"] = self.merkle_levels
            res["player_snapshots"] = self.player_snapshots
        return res


class CircularCheckpointBuffer:
    def __init__(self, capacity=600):
        self.capacity = capacity
        self.buffer = []
        self.index = 0
        self.total_frames = 0

    def push(self, checkpoint):
        if len(self.buffer) < self.capacity:
            self.buffer.append(checkpoint)
        else:
            self.buffer[self.index] = checkpoint
        self.index = (self.index + 1) % self.capacity
        self.total_frames += 1

    def get_latest(self):
        if not self.buffer:
            return None
        prev_idx = (self.index - 1 + len(self.buffer)) % len(self.buffer)
        return self.buffer[prev_idx]

    def get_by_frame(self, frame_id):
        for cp in self.buffer:
            if cp and cp.frame_id == frame_id:
                return cp
        return None

    def find_last_trusted_checkpoint(self, player_id, min_trust=0.90, max_lookback_frames=300):
        # Search backwards in circular buffer
        count = len(self.buffer)
        if count == 0:
            return None
            
        for i in range(min(count, max_lookback_frames)):
            idx = (self.index - 1 - i + count) % count
            cp = self.buffer[idx]
            if cp and cp.is_verified:
                t = cp.trust_scores.get(player_id, 1.0)
                if t >= min_trust and player_id in cp.player_snapshots:
                    return cp
        return None

    def get_recent_summaries(self, limit=12):
        res = []
        count = len(self.buffer)
        for i in range(min(count, limit)):
            idx = (self.index - 1 - i + count) % count
            cp = self.buffer[idx]
            if cp:
                res.append(cp.to_dict(include_tree=False))
        return res
