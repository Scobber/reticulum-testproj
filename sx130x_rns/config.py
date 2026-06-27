from dataclasses import dataclass, field
from pathlib import Path

from .radio.channel import Channel, build_channel


def _as_bool(value: str) -> bool:
    return value.strip().lower() in ("1", "true", "yes", "on")


@dataclass
class SX130xConfig:
    enabled: bool = True
    device: str = "/dev/spidev0.0"
    reset_pin: int | None = None
    chip: str = "sx1302"
    region: str = "AU915"
    tx_power: int = 20
    dedupe_window_ms: int = 1500
    tx_policy: str = "reply_same_channel"
    fixed_channel_index: int = 0
    channels: list[Channel] = field(default_factory=list)


def preset_channels(region: str) -> list[Channel]:
    r = region.upper()
    if r == "AU915":
        freqs = [915200000, 915400000]
    elif r == "US915":
        freqs = [902300000, 902500000]
    elif r == "EU868":
        freqs = [868100000, 868300000]
    else:
        raise ValueError(f"unsupported region {region}")

    return [
        Channel(name=f"{r.lower()}_{idx}", frequency=freq, bandwidth=125000, spreading_factor=7, coding_rate=5, index=idx)
        for idx, freq in enumerate(freqs)
    ]


def load_config(path: str | Path) -> SX130xConfig:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    main: dict[str, str] = {}
    channel_blocks: list[dict[str, str]] = []
    current: dict[str, str] | None = None

    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith(";"):
            continue
        if line == "[[SX130x]]":
            current = main
            continue
        if line == "[[SX130x.channels]]":
            current = {}
            channel_blocks.append(current)
            continue
        if "=" not in line or current is None:
            continue

        key, value = line.split("=", 1)
        current[key.strip()] = value.strip()

    config = SX130xConfig(
        enabled=_as_bool(main.get("enabled", "yes")),
        device=main.get("device", "/dev/spidev0.0"),
        reset_pin=int(main["reset_pin"]) if main.get("reset_pin") else None,
        chip=main.get("chip", "sx1302"),
        region=main.get("region", "AU915"),
        tx_power=int(main.get("tx_power", "20")),
        dedupe_window_ms=int(main.get("dedupe_window_ms", "1500")),
        tx_policy=main.get("tx_policy", "reply_same_channel"),
        fixed_channel_index=int(main.get("fixed_channel_index", "0")),
    )

    channels: list[Channel] = []
    for idx, block in enumerate(channel_blocks):
        channels.append(build_channel(idx, block))

    if not channels:
        channels = preset_channels(config.region)

    config.channels = channels
    return config
