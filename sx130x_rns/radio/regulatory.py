import time
from dataclasses import dataclass


@dataclass(frozen=True)
class RegionRule:
    name: str
    min_freq: int
    max_freq: int
    max_tx_power: int
    dwell_time_ms: int
    duty_cycle: float | None


REGION_RULES = {
    "AU915": RegionRule("AU915", 915000000, 928000000, 30, 400, None),
    "US915": RegionRule("US915", 902000000, 928000000, 30, 400, None),
    "EU868": RegionRule("EU868", 863000000, 870000000, 16, 0, 0.01),
}


class RegulatoryLimiter:
    def __init__(self, region: str) -> None:
        try:
            self.rule = REGION_RULES[region.upper()]
        except KeyError as exc:
            raise ValueError(f"unsupported region {region}") from exc
        self._tx_history: list[tuple[float, float]] = []

    def validate_channel_frequency(self, frequency: int) -> bool:
        return self.rule.min_freq <= frequency <= self.rule.max_freq

    def validate_tx_power(self, tx_power: int) -> bool:
        return tx_power <= self.rule.max_tx_power

    def can_transmit(self, airtime_ms: float, now: float | None = None) -> tuple[bool, str | None]:
        now = now if now is not None else time.time()

        if self.rule.dwell_time_ms and airtime_ms > self.rule.dwell_time_ms:
            return False, "dwell_time_exceeded"

        if self.rule.duty_cycle is not None:
            window = 3600.0
            self._tx_history = [(ts, at) for ts, at in self._tx_history if ts > now - window]
            used = sum(at for _, at in self._tx_history)
            allowed = window * 1000.0 * self.rule.duty_cycle
            if used + airtime_ms > allowed:
                return False, "duty_cycle_exceeded"

        return True, None

    def record_transmit(self, airtime_ms: float, now: float | None = None) -> None:
        now = now if now is not None else time.time()
        self._tx_history.append((now, airtime_ms))

    def state(self) -> dict[str, object]:
        return {
            "region": self.rule.name,
            "max_tx_power": self.rule.max_tx_power,
            "dwell_time_ms": self.rule.dwell_time_ms,
            "duty_cycle": self.rule.duty_cycle,
            "history_count": len(self._tx_history),
        }
