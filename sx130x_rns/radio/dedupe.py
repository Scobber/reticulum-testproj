import hashlib
import time


class DedupeCache:
    def __init__(self, window_ms: int = 1500) -> None:
        if window_ms <= 0:
            raise ValueError("window_ms must be > 0")
        self.window_ms = window_ms
        self._cache: dict[str, float] = {}
        self.hits = 0
        self.misses = 0

    def _cleanup(self, now: float) -> None:
        stale_before = now - (self.window_ms / 1000.0)
        stale = [k for k, ts in self._cache.items() if ts < stale_before]
        for key in stale:
            self._cache.pop(key, None)

    def make_key(
        self,
        payload: bytes,
        timestamp: float,
        frequency: int,
        bandwidth: int,
        spreading_factor: int,
        coding_rate: int,
    ) -> str:
        rounded_ts = int(timestamp * 1000) // self.window_ms
        digest = hashlib.sha256()
        digest.update(payload)
        digest.update(str(rounded_ts).encode())
        digest.update(f"{frequency}:{bandwidth}:{spreading_factor}:{coding_rate}".encode())
        return digest.hexdigest()

    def seen_or_add(self, key: str, now: float | None = None) -> bool:
        now = now if now is not None else time.time()
        self._cleanup(now)
        if key in self._cache:
            self.hits += 1
            return True
        self._cache[key] = now
        self.misses += 1
        return False

    def stats(self) -> dict[str, int]:
        return {"hits": self.hits, "misses": self.misses, "size": len(self._cache)}
