from math import ceil


def lora_airtime_ms(
    payload_len: int,
    spreading_factor: int,
    bandwidth: int,
    coding_rate: int,
    preamble_len: int = 8,
    explicit_header: bool = True,
    crc_on: bool = True,
    low_data_rate_opt: bool | None = None,
) -> float:
    if payload_len < 0:
        raise ValueError("payload_len must be >= 0")
    if not (7 <= spreading_factor <= 12):
        raise ValueError("spreading_factor must be 7..12")
    if coding_rate not in (5, 6, 7, 8):
        raise ValueError("coding_rate must be 5..8")
    if bandwidth <= 0:
        raise ValueError("bandwidth must be > 0")

    sf = spreading_factor
    bw = float(bandwidth)
    cr = coding_rate - 4
    ih = 0 if explicit_header else 1
    de = 1 if (low_data_rate_opt if low_data_rate_opt is not None else (sf >= 11 and bandwidth == 125000)) else 0
    crc = 1 if crc_on else 0

    t_sym = (2**sf) / bw
    t_preamble = (preamble_len + 4.25) * t_sym

    payload_symbol_num = 8 + max(
        ceil((8 * payload_len - 4 * sf + 28 + 16 * crc - 20 * ih) / (4 * (sf - 2 * de))) * (cr + 4),
        0,
    )

    t_payload = payload_symbol_num * t_sym
    return (t_preamble + t_payload) * 1000.0
