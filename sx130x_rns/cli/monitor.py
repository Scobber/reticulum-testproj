import argparse
import time

from sx130x_rns.config import load_config
from sx130x_rns.interface import SX130xInterface


def main() -> int:
    parser = argparse.ArgumentParser(prog="sx130x-rns-monitor")
    parser.add_argument("--config", default="examples/au915.ini")
    parser.add_argument("--interval", type=float, default=1.0)
    parser.add_argument("--count", type=int, default=5)
    args = parser.parse_args()

    cfg = load_config(args.config)
    iface = SX130xInterface(cfg)
    iface.start()

    try:
        for _ in range(args.count):
            iface.poll_receive()
            print(iface.get_status())
            time.sleep(args.interval)
    finally:
        iface.stop()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
