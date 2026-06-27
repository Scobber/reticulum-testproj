from sx130x_rns.radio.peer_memory import PeerMemory


def test_peer_memory_update_and_result() -> None:
    pm = PeerMemory()
    pm.update_rx("peer1", 915200000, 7, 125000, -60, 9.1, timestamp=1.0, channel_index=1)
    pm.mark_tx_result("peer1", True)
    rec = pm.get("peer1")
    assert rec is not None
    assert rec.last_channel_index == 1
    assert rec.success_count == 1
