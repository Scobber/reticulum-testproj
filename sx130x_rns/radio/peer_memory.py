import time
from dataclasses import dataclass


@dataclass
class PeerRecord:
    peer_id: str
    last_frequency: int
    last_spreading_factor: int
    last_bandwidth: int
    last_rssi: float
    last_snr: float
    timestamp: float
    success_count: int = 0
    failure_count: int = 0
    last_channel_index: int | None = None


class PeerMemory:
    def __init__(self) -> None:
        self._records: dict[str, PeerRecord] = {}

    def update_rx(
        self,
        peer_id: str,
        frequency: int,
        spreading_factor: int,
        bandwidth: int,
        rssi: float,
        snr: float,
        timestamp: float | None = None,
        channel_index: int | None = None,
    ) -> None:
        timestamp = timestamp if timestamp is not None else time.time()
        current = self._records.get(peer_id)
        self._records[peer_id] = PeerRecord(
            peer_id=peer_id,
            last_frequency=frequency,
            last_spreading_factor=spreading_factor,
            last_bandwidth=bandwidth,
            last_rssi=rssi,
            last_snr=snr,
            timestamp=timestamp,
            success_count=current.success_count if current else 0,
            failure_count=current.failure_count if current else 0,
            last_channel_index=channel_index,
        )

    def mark_tx_result(self, peer_id: str, success: bool) -> None:
        rec = self._records.get(peer_id)
        if rec is None:
            return
        if success:
            rec.success_count += 1
        else:
            rec.failure_count += 1

    def get(self, peer_id: str) -> PeerRecord | None:
        return self._records.get(peer_id)
