"""Unit tests for CuckooFilter."""

import pytest

from login_checker.cuckoo_filter import CuckooFilter


def test_empty_contains_nothing():
    """A new filter has only empty slots, so nothing is reported present."""
    assert not CuckooFilter(capacity=100).contains("alice")


def test_no_false_negatives():
    """Every successfully added login is always reported present."""
    logins = [f"user{i}" for i in range(10_000)]
    cuckoo = CuckooFilter(capacity=10_000)
    assert all(cuckoo.add(name) for name in logins)
    assert all(cuckoo.contains(name) for name in logins)


def test_false_positive_rate_below_bound():
    """Measured false-positive rate stays under 2b / 2^f (with some slack)."""
    n = 10_000
    cuckoo = CuckooFilter(capacity=n, bucket_size=4, fingerprint_bits=12)
    for i in range(n):
        cuckoo.add(f"user{i}")
    bound = 2 * 4 / 2**12
    false_positives = sum(cuckoo.contains(f"other{i}") for i in range(n))
    assert false_positives / n < 2 * bound


def test_delete_removes_login():
    """A deleted login is no longer found, and other logins are unaffected."""
    cuckoo = CuckooFilter(capacity=100, logins=["alice", "bob"])
    assert cuckoo.delete("alice")
    assert not cuckoo.contains("alice")
    assert cuckoo.contains("bob")
    assert len(cuckoo) == 1


def test_delete_missing_login_returns_false():
    """Deleting something never added returns False without crashing."""
    cuckoo = CuckooFilter(capacity=100, logins=["alice"])
    assert not cuckoo.delete("carol")
    assert len(cuckoo) == 1


def test_alt_index_is_symmetric():
    """alt(alt(i, fp), fp) == i, so items can move back and forth."""
    cuckoo = CuckooFilter(capacity=1_000)
    for i in range(1_000):
        fingerprint, index = cuckoo._fingerprint_and_index(f"user{i}")
        other = cuckoo.alt_index(index, fingerprint)
        assert 0 <= other < cuckoo.num_buckets
        assert cuckoo.alt_index(other, fingerprint) == index


def test_fingerprint_is_never_zero():
    """Zero marks an empty slot, so real fingerprints must be non-zero."""
    cuckoo = CuckooFilter(capacity=100, fingerprint_bits=2)
    for i in range(1_000):
        fingerprint, _ = cuckoo._fingerprint_and_index(f"user{i}")
        assert fingerprint != 0


def test_full_filter_reports_failure_without_losing_items():
    """Overfilling returns False instead of looping, and earlier logins are still found."""
    cuckoo = CuckooFilter(capacity=8, bucket_size=2, max_kicks=50)
    added = []
    for i in range(1_000):
        name = f"user{i}"
        if not cuckoo.add(name):
            break
        added.append(name)
    else:
        pytest.fail("filter never reported itself full")
    assert all(cuckoo.contains(name) for name in added)


def test_table_size_is_power_of_two():
    """Bucket count is a power of two so masking works as mod."""
    for capacity in [1, 7, 100, 12_345]:
        buckets = CuckooFilter(capacity=capacity).num_buckets
        assert buckets & (buckets - 1) == 0


def test_invalid_arguments_raise():
    """Bad constructor arguments are rejected."""
    with pytest.raises(ValueError):
        CuckooFilter(capacity=0)
    with pytest.raises(ValueError):
        CuckooFilter(capacity=10, fingerprint_bits=0)
