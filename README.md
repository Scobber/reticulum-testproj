# reticulum-sx130x

A Reticulum interface for Semtech SX1301/SX1302/SX1303 concentrators.

## Design intent

This project models a concentrator as **one Reticulum interface** with:
- many RX paths
- one managed TX path

It is **not LoRaWAN**, and it is **not 8 fake RNodes**.

## Quick start

```bash
python -m pip install -e .[dev]
pytest -q
sx130x-rns-test validate-config --config examples/au915.ini
```

## Configuration format

Use Reticulum-style double-bracket sections:

```ini
[[SX130x]]
type = SX130xInterface
enabled = yes
device = /dev/spidev0.0
reset_pin = 17
chip = sx1302
region = AU915
tx_power = 20
dedupe_window_ms = 1500
tx_policy = reply_same_channel

[[SX130x.channels]]
name = au915_0
frequency = 915200000
bandwidth = 125000
spreading_factor = 7
coding_rate = 5
```

See `examples/` and `docs/` for details.
