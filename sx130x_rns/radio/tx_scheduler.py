from collections import deque
from dataclasses import dataclass

from .channel import Channel
from .peer_memory import PeerMemory


@dataclass
class TxRequest:
    payload: bytes
    peer_id: str | None = None
    hint_channel_index: int | None = None


class TxScheduler:
    def __init__(self, channels: list[Channel], tx_policy: str = "fixed_channel", fixed_channel_index: int = 0) -> None:
        self.channels = channels
        self.tx_policy = tx_policy
        self.fixed_channel_index = fixed_channel_index
        self.queue: deque[TxRequest] = deque()
        self._rr_index = 0

    def enqueue(self, request: TxRequest) -> None:
        self.queue.append(request)

    def queue_size(self) -> int:
        return len(self.queue)

    def choose_channel(self, request: TxRequest, peer_memory: PeerMemory) -> Channel:
        if not self.channels:
            raise RuntimeError("no channels configured")

        if self.tx_policy == "fixed_channel":
            idx = self.fixed_channel_index % len(self.channels)
            return self.channels[idx]

        if self.tx_policy == "reply_same_channel":
            if request.hint_channel_index is not None:
                return self.channels[request.hint_channel_index % len(self.channels)]
            if request.peer_id:
                rec = peer_memory.get(request.peer_id)
                if rec and rec.last_channel_index is not None:
                    return self.channels[rec.last_channel_index % len(self.channels)]
            return self.channels[self.fixed_channel_index % len(self.channels)]

        if self.tx_policy == "round_robin":
            channel = self.channels[self._rr_index % len(self.channels)]
            self._rr_index += 1
            return channel

        return self.channels[self.fixed_channel_index % len(self.channels)]

    def next(self) -> TxRequest | None:
        if not self.queue:
            return None
        return self.queue.popleft()
