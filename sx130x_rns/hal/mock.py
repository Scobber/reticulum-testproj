from .base import RXPacket, SX130xHAL


class MockSX130xHAL(SX130xHAL):
    def __init__(self) -> None:
        self.started = False
        self.initialized = False
        self.channels: list[dict[str, int | str]] = []
        self.rx_queue: list[RXPacket] = []
        self.tx_packets: list[dict[str, object]] = []

    def init(self) -> None:
        self.initialized = True

    def start(self) -> None:
        if not self.initialized:
            raise RuntimeError("HAL not initialized")
        self.started = True

    def stop(self) -> None:
        self.started = False

    def receive(self) -> list[RXPacket]:
        packets = list(self.rx_queue)
        self.rx_queue.clear()
        return packets

    def transmit(self, payload: bytes, frequency: int, bandwidth: int, spreading_factor: int, coding_rate: int, tx_power: int) -> bool:
        if not self.started:
            return False
        self.tx_packets.append(
            {
                "payload": payload,
                "frequency": frequency,
                "bandwidth": bandwidth,
                "spreading_factor": spreading_factor,
                "coding_rate": coding_rate,
                "tx_power": tx_power,
            }
        )
        return True

    def set_channel_plan(self, channels: list[dict[str, int | str]]) -> None:
        self.channels = channels

    def get_status(self) -> dict[str, object]:
        return {
            "initialized": self.initialized,
            "started": self.started,
            "rx_queued": len(self.rx_queue),
            "tx_count": len(self.tx_packets),
        }
