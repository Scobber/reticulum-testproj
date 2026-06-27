import time

from sx130x_rns.config import load_config
from sx130x_rns.hal.base import RXPacket
from sx130x_rns.interface import SX130xInterface


def test_interface_rx_dedupe_and_tx(tmp_path) -> None:
    cfg_file = tmp_path / "cfg.ini"
    cfg_file.write_text(
        "\n".join(
            [
                "[[SX130x]]",
                "enabled = yes",
                "region = AU915",
                "tx_policy = reply_same_channel",
                "[[SX130x.channels]]",
                "name = c0",
                "frequency = 915200000",
                "bandwidth = 125000",
                "spreading_factor = 7",
                "coding_rate = 5",
            ]
        ),
        encoding="utf-8",
    )
    cfg = load_config(cfg_file)
    iface = SX130xInterface(cfg)
    iface.start()

    received: list[bytes] = []
    iface.set_rx_callback(received.append)

    pkt = RXPacket(
        payload=b"hello",
        frequency=915200000,
        bandwidth=125000,
        spreading_factor=7,
        coding_rate=5,
        rssi=-70,
        snr=5.0,
        timestamp=time.time(),
        channel_index=0,
        crc_ok=True,
    )
    iface.inject_mock_packet(pkt)
    iface.inject_mock_packet(pkt)
    assert iface.poll_receive() == 1
    assert received == [b"hello"]

    iface.queue_transmit(b"world")
    assert iface.process_tx_queue() == 1
    iface.stop()
