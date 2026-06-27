from pathlib import Path

from sx130x_rns.config import load_config


def test_load_config_parses_channels(tmp_path: Path) -> None:
    cfg_file = tmp_path / "test.ini"
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
    assert cfg.enabled is True
    assert cfg.region == "AU915"
    assert len(cfg.channels) == 1
    assert cfg.channels[0].frequency == 915200000
