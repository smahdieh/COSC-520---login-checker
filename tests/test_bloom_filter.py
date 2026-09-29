"""Unit tests for BloomFilter."""

import math

import pytest

from login_checker.bloom_filter import BloomFilter


def test_empty_contains_nothing():
    """A new filter has no bits set, so nothing is reported present."""
    bloom = BloomFilter(expected_items=100)
    assert not bloom.contains("alice")


def test_no_false_negatives():
    """Every added login is always reported present."""
    logins = [f"user{i}" for i in range(10_000)]
    bloom = BloomFilter(expected_items=10_000, fp_rate=0.01, logins=logins)
    assert all(bloom.contains(name) for name in logins)


def test_false_positive_rate_near_target():
    """Measured false-positive rate on unseen logins stays close to p."""
    n = 10_000
    bloom = BloomFilter(expected_items=n, fp_rate=0.01)
    for i in range(n):
        bloom.add(f"user{i}")
    false_positives = sum(bloom.contains(f"other{i}") for i in range(n))
    assert false_positives / n < 0.02


def test_sizing_matches_formulas():
    """m and k follow m = -n ln p / (ln 2)^2 and k = (m/n) ln 2."""
    n, p = 1_000, 0.01
    bloom = BloomFilter(expected_items=n, fp_rate=p)
    assert bloom.num_bits == math.ceil(-n * math.log(p) / math.log(2) ** 2)
    assert bloom.num_hashes == round(bloom.num_bits / n * math.log(2))
    assert bloom.num_hashes == 7


def test_positions_are_in_range():
    """All k bit positions fall inside the m-bit array, including for ''."""
    bloom = BloomFilter(expected_items=50)
    for login in ["", "a", "alice", "x" * 500]:
        positions = list(bloom._positions(login))
        assert len(positions) == bloom.num_hashes
        assert all(0 <= pos < bloom.num_bits for pos in positions)


def test_expected_fp_rate_grows_with_items():
    """The estimated false-positive rate starts at 0 and increases as items are added."""
    bloom = BloomFilter(expected_items=1_000, fp_rate=0.01)
    assert bloom.expected_fp_rate() == 0
    for i in range(1_000):
        bloom.add(f"user{i}")
    assert 0.005 < bloom.expected_fp_rate() < 0.02


def test_invalid_arguments_raise():
    """Bad n or p values are rejected."""
    with pytest.raises(ValueError):
        BloomFilter(expected_items=0)
    with pytest.raises(ValueError):
        BloomFilter(expected_items=10, fp_rate=1.5)
