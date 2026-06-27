from .base import RXPacket, SX130xHAL


class SemtechSX130xHAL(SX130xHAL):
    """Initial Semtech HAL integration stub.

    This class is intentionally conservative and side-effect free until native
    bindings/wrappers are wired in for sx1302_hal/lora_gateway.
    """

    def __init__(self, device: str, reset_pin: int | None = None, chip: str = "sx1302") -> None:
        self.device = device
        self.reset_pin = reset_pin
        self.chip = chip
        self.initialized = False
        self.started = False
        self._channels: list[dict[str, int | str]] = []

    def init(self) -> None:
        self.initialized = True

    def start(self) -> None:
        if not self.initialized:
            raise RuntimeError("HAL not initialized")
        self.started = True

    def stop(self) -> None:
        self.started = False

    def receive(self) -> list[RXPacket]:
        return []

    def transmit(self, payload: bytes, frequency: int, bandwidth: int, spreading_factor: int, coding_rate: int, tx_power: int) -> bool:
        if not self.started:
            return False
        return False

    def set_channel_plan(self, channels: list[dict[str, int | str]]) -> None:
        self._channels = channels

    def get_status(self) -> dict[str, object]:
        return {
            "chip": self.chip,
            "device": self.device,
            "reset_pin": self.reset_pin,
            "initialized": self.initialized,
            "started": self.started,
            "channels": len(self._channels),
            "backend": "semtech_stub",
        }
