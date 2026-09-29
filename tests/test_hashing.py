"""Unit tests for the shared hash functions."""

from login_checker.hashing import hash64, hash_pair


def test_hash64_is_deterministic():
    """The same input and seed always give the same hash."""
    assert hash64("alice") == hash64("alice")


def test_hash64_is_64_bit():
    """Hashes fall in the unsigned 64-bit range."""
    for word in ["", "a", "alice", "x" * 1000]:
        assert 0 <= hash64(word) < 2**64


def test_hash64_seed_changes_output():
    """Different seeds act as different hash functions."""
    assert hash64("alice", seed=0) != hash64("alice", seed=1)


def test_hash64_spreads_similar_inputs():
    """Near-identical logins do not collide."""
    values = {hash64(f"user{i}") for i in range(10_000)}
    assert len(values) == 10_000


def test_hash_pair_second_hash_is_odd():
    """h2 is always odd, so it is never zero in double hashing."""
    for i in range(1000):
        h1, h2 = hash_pair(f"user{i}")
        assert 0 <= h1 < 2**32
        assert h2 % 2 == 1
