from sx130x_rns.radio.dedupe import DedupeCache


def test_dedupe_cache_hits_and_expiry() -> None:
    cache = DedupeCache(window_ms=100)
    key = cache.make_key(b"abc", 10.0, 915200000, 125000, 7, 5)

    assert cache.seen_or_add(key, now=1.0) is False
    assert cache.seen_or_add(key, now=1.05) is True
    assert cache.seen_or_add(key, now=1.2) is False
