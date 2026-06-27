from sx130x_rns.radio.regulatory import RegulatoryLimiter


def test_regulatory_frequency_validation() -> None:
    reg = RegulatoryLimiter("AU915")
    assert reg.validate_channel_frequency(915200000)
    assert not reg.validate_channel_frequency(800000000)


def test_regulatory_duty_cycle_for_eu868() -> None:
    reg = RegulatoryLimiter("EU868")
    ok, reason = reg.can_transmit(1000, now=1.0)
    assert ok and reason is None
    reg.record_transmit(35000, now=1.0)
    ok2, reason2 = reg.can_transmit(2000, now=2.0)
    assert not ok2
    assert reason2 == "duty_cycle_exceeded"
