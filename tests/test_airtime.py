from sx130x_rns.radio.airtime import lora_airtime_ms


def test_airtime_increases_with_payload() -> None:
    short = lora_airtime_ms(5, 7, 125000, 5)
    long = lora_airtime_ms(50, 7, 125000, 5)
    assert long > short
