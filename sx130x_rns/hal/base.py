from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class RXPacket:
    payload: bytes
    frequency: int
    bandwidth: int
    spreading_factor: int
    coding_rate: int
    rssi: float
    snr: float
    timestamp: float
    channel_index: int
    crc_ok: bool = True


class SX130xHAL(ABC):
    @abstractmethod
    def init(self) -> None: ...

    @abstractmethod
    def start(self) -> None: ...

    @abstractmethod
    def stop(self) -> None: ...

    @abstractmethod
    def receive(self) -> list[RXPacket]: ...

    @abstractmethod
    def transmit(self, payload: bytes, frequency: int, bandwidth: int, spreading_factor: int, coding_rate: int, tx_power: int) -> bool: ...

    @abstractmethod
    def set_channel_plan(self, channels: list[dict[str, int | str]]) -> None: ...

    @abstractmethod
    def get_status(self) -> dict[str, object]: ...
