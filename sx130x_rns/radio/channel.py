from dataclasses import dataclass


@dataclass(frozen=True)
class Channel:
    name: str
    frequency: int
    bandwidth: int
    spreading_factor: int
    coding_rate: int
    index: int = 0

    def validate(self) -> None:
        if self.frequency <= 0:
            raise ValueError("frequency must be positive")
        if self.bandwidth not in (125000, 250000, 500000):
            raise ValueError("bandwidth must be one of 125000/250000/500000")
        if not (7 <= self.spreading_factor <= 12):
            raise ValueError("spreading_factor must be 7..12")
        if self.coding_rate not in (5, 6, 7, 8):
            raise ValueError("coding_rate must be 5..8")


def build_channel(index: int, values: dict[str, str]) -> Channel:
    channel = Channel(
        name=values["name"],
        frequency=int(values["frequency"]),
        bandwidth=int(values["bandwidth"]),
        spreading_factor=int(values["spreading_factor"]),
        coding_rate=int(values["coding_rate"]),
        index=index,
    )
    channel.validate()
    return channel
