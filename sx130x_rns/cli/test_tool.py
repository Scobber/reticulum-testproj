import argparse
import time

from sx130x_rns.config import load_config
from sx130x_rns.hal.base import RXPacket
from sx130x_rns.interface import SX130xInterface


def cmd_validate_config(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    print(f"OK region={cfg.region} chip={cfg.chip} channels={len(cfg.channels)}")
    return 0


def cmd_detect(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    iface = SX130xInterface(cfg)
    iface.start()
    status = iface.get_status()
    print(status["hal"])
    iface.stop()
    return 0


def cmd_channel_plan(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    for ch in cfg.channels:
        print(f"{ch.index}: {ch.name} {ch.frequency}Hz SF{ch.spreading_factor} BW{ch.bandwidth}")
    return 0


def cmd_rx_test(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    iface = SX130xInterface(cfg)
    iface.start()
    iface.set_rx_callback(lambda payload: print(payload.hex()))

    iface.inject_mock_packet(
        RXPacket(
            payload=b"hello",
            frequency=cfg.channels[0].frequency,
            bandwidth=cfg.channels[0].bandwidth,
            spreading_factor=cfg.channels[0].spreading_factor,
            coding_rate=cfg.channels[0].coding_rate,
            rssi=-50,
            snr=8.2,
            timestamp=time.time(),
            channel_index=cfg.channels[0].index,
            crc_ok=True,
        )
    )
    print(f"processed={iface.poll_receive()}")
    print(f"dedupe={iface.dedupe.stats()}")
    iface.stop()
    return 0


def cmd_tx_test(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    iface = SX130xInterface(cfg)
    iface.start()
    iface.queue_transmit(args.payload.encode("utf-8"))
    print(f"sent={iface.process_tx_queue()}")
    iface.stop()
    return 0


def cmd_dedupe(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    iface = SX130xInterface(cfg)
    print(iface.dedupe.stats())
    return 0


def cmd_tx_queue(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    iface = SX130xInterface(cfg)
    print({"queued": iface.scheduler.queue_size()})
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="sx130x-rns-test")
    p.add_argument("--config", default="examples/au915.ini")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("validate-config")
    sub.add_parser("detect")
    sub.add_parser("channel-plan")
    rx = sub.add_parser("rx-test")
    tx = sub.add_parser("tx-test")
    tx.add_argument("--payload", default="test")
    sub.add_parser("dedupe")
    sub.add_parser("tx-queue")

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    commands = {
        "validate-config": cmd_validate_config,
        "detect": cmd_detect,
        "channel-plan": cmd_channel_plan,
        "rx-test": cmd_rx_test,
        "tx-test": cmd_tx_test,
        "dedupe": cmd_dedupe,
        "tx-queue": cmd_tx_queue,
    }
    return commands[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
