from sx130x_rns.hal.base import RXPacket
from sx130x_rns.hal.mock import MockSX130xHAL


def test_mock_hal_receive_transmit() -> None:
    hal = MockSX130xHAL()
    hal.init()
    hal.start()
    hal.rx_queue.append(
        RXPacket(b"abc", 915200000, 125000, 7, 5, -50, 8.0, 1.0, 0, True)
    )
    packets = hal.receive()
    assert len(packets) == 1
    assert hal.transmit(b"x", 915200000, 125000, 7, 5, 20)
    assert hal.get_status()["tx_count"] == 1
