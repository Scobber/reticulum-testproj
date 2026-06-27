from collections import deque
import hashlib
import logging

from .config import SX130xConfig
from .hal.base import RXPacket, SX130xHAL
from .hal.mock import MockSX130xHAL
from .radio.airtime import lora_airtime_ms
from .radio.dedupe import DedupeCache
from .radio.peer_memory import PeerMemory
from .radio.regulatory import RegulatoryLimiter
from .radio.tx_scheduler import TxRequest, TxScheduler


class SX130xInterface:
    def __init__(self, config: SX130xConfig, hal: SX130xHAL | None = None, logger: logging.Logger | None = None) -> None:
        self.config = config
        self.hal = hal if hal is not None else MockSX130xHAL()
        self.log = logger if logger is not None else logging.getLogger(__name__)
        self.dedupe = DedupeCache(window_ms=config.dedupe_window_ms)
        self.peer_memory = PeerMemory()
        self.regulatory = RegulatoryLimiter(config.region)
        self.scheduler = TxScheduler(config.channels, tx_policy=config.tx_policy, fixed_channel_index=config.fixed_channel_index)
        self.tx_queue: deque[TxRequest] = self.scheduler.queue
        self.rx_callback = None
        self._last_rx_metadata: dict[str, dict[str, object]] = {}
        self.started = False

    def start(self) -> None:
        self.hal.init()
        self.hal.set_channel_plan(
            [
                {
                    "name": c.name,
                    "frequency": c.frequency,
                    "bandwidth": c.bandwidth,
                    "spreading_factor": c.spreading_factor,
                    "coding_rate": c.coding_rate,
                    "index": c.index,
                }
                for c in self.config.channels
            ]
        )
        self.hal.start()
        self.started = True
        self.log.info("SX130xInterface started chip=%s region=%s channels=%d", self.config.chip, self.config.region, len(self.config.channels))

    def stop(self) -> None:
        self.hal.stop()
        self.started = False

    def set_rx_callback(self, callback) -> None:
        self.rx_callback = callback

    @staticmethod
    def _peer_hint(payload: bytes) -> str:
        return hashlib.sha256(payload).hexdigest()[:16]

    def poll_receive(self) -> int:
        processed = 0
        for packet in self.hal.receive():
            if not packet.crc_ok:
                continue

            key = self.dedupe.make_key(
                payload=packet.payload,
                timestamp=packet.timestamp,
                frequency=packet.frequency,
                bandwidth=packet.bandwidth,
                spreading_factor=packet.spreading_factor,
                coding_rate=packet.coding_rate,
            )
            if self.dedupe.seen_or_add(key):
                self.log.debug("dedupe hit channel=%s", packet.channel_index)
                continue

            peer_id = self._peer_hint(packet.payload)
            self.peer_memory.update_rx(
                peer_id=peer_id,
                frequency=packet.frequency,
                spreading_factor=packet.spreading_factor,
                bandwidth=packet.bandwidth,
                rssi=packet.rssi,
                snr=packet.snr,
                timestamp=packet.timestamp,
                channel_index=packet.channel_index,
            )

            self._last_rx_metadata[peer_id] = {
                "frequency": packet.frequency,
                "bandwidth": packet.bandwidth,
                "spreading_factor": packet.spreading_factor,
                "coding_rate": packet.coding_rate,
                "rssi": packet.rssi,
                "snr": packet.snr,
                "timestamp": packet.timestamp,
                "channel_index": packet.channel_index,
            }
            if self.rx_callback is not None:
                self.rx_callback(packet.payload)

            processed += 1
        return processed

    def queue_transmit(self, payload: bytes, peer_id: str | None = None, hint_channel_index: int | None = None) -> None:
        self.scheduler.enqueue(TxRequest(payload=payload, peer_id=peer_id, hint_channel_index=hint_channel_index))

    def process_tx_queue(self) -> int:
        sent = 0
        while True:
            req = self.scheduler.next()
            if req is None:
                break
            channel = self.scheduler.choose_channel(req, self.peer_memory)
            if not self.regulatory.validate_channel_frequency(channel.frequency):
                self.log.warning("regulatory block invalid_frequency=%s", channel.frequency)
                continue
            if not self.regulatory.validate_tx_power(self.config.tx_power):
                self.log.warning("regulatory block tx_power=%s", self.config.tx_power)
                continue

            airtime = lora_airtime_ms(
                payload_len=len(req.payload),
                spreading_factor=channel.spreading_factor,
                bandwidth=channel.bandwidth,
                coding_rate=channel.coding_rate,
            )
            allowed, reason = self.regulatory.can_transmit(airtime)
            if not allowed:
                self.log.warning("regulatory block reason=%s", reason)
                continue

            ok = self.hal.transmit(
                payload=req.payload,
                frequency=channel.frequency,
                bandwidth=channel.bandwidth,
                spreading_factor=channel.spreading_factor,
                coding_rate=channel.coding_rate,
                tx_power=self.config.tx_power,
            )
            if ok:
                self.regulatory.record_transmit(airtime)
                sent += 1
                if req.peer_id:
                    self.peer_memory.mark_tx_result(req.peer_id, success=True)
            else:
                if req.peer_id:
                    self.peer_memory.mark_tx_result(req.peer_id, success=False)
        return sent

    def inject_mock_packet(self, packet: RXPacket) -> None:
        if isinstance(self.hal, MockSX130xHAL):
            self.hal.rx_queue.append(packet)
        else:
            raise RuntimeError("inject_mock_packet is only supported with MockSX130xHAL")

    def get_status(self) -> dict[str, object]:
        return {
            "started": self.started,
            "hal": self.hal.get_status(),
            "dedupe": self.dedupe.stats(),
            "tx_queue": self.scheduler.queue_size(),
            "regulatory": self.regulatory.state(),
        }
