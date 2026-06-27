from sx130x_rns.radio.channel import Channel
from sx130x_rns.radio.peer_memory import PeerMemory
from sx130x_rns.radio.tx_scheduler import TxRequest, TxScheduler


def _channels() -> list[Channel]:
    return [
        Channel("c0", 915200000, 125000, 7, 5, 0),
        Channel("c1", 915400000, 125000, 7, 5, 1),
    ]


def test_tx_policy_fixed_channel() -> None:
    sched = TxScheduler(_channels(), tx_policy="fixed_channel", fixed_channel_index=1)
    ch = sched.choose_channel(TxRequest(payload=b"x"), PeerMemory())
    assert ch.index == 1


def test_tx_policy_reply_same_channel_uses_hint() -> None:
    sched = TxScheduler(_channels(), tx_policy="reply_same_channel", fixed_channel_index=0)
    ch = sched.choose_channel(TxRequest(payload=b"x", hint_channel_index=1), PeerMemory())
    assert ch.index == 1
