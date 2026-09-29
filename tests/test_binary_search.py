"""Unit tests for BinarySearch."""

import random

from login_checker.binary_search import BinarySearch


def test_empty_contains_nothing():
    """A new, empty structure reports every login as free."""
    assert not BinarySearch().contains("alice")


def test_single_element():
    """Works when the array holds exactly one login."""
    checker = BinarySearch(["alice"])
    assert checker.contains("alice")
    assert not checker.contains("bob")


def test_first_last_and_middle_elements():
    """Boundary positions of the sorted array are found."""
    logins = ["amy", "bob", "cat", "dan", "eve"]
    checker = BinarySearch(logins)
    for name in logins:
        assert checker.contains(name)


def test_missing_before_between_and_after():
    """Absent logins that sort before, between or after stored ones are free."""
    checker = BinarySearch(["bob", "dan"])
    for name in ["aaa", "carl", "zed"]:
        assert not checker.contains(name)


def test_add_keeps_array_sorted():
    """Inserting in random order still allows every login to be found."""
    logins = [f"user{i}" for i in range(500)]
    random.Random(42).shuffle(logins)
    checker = BinarySearch()
    for name in logins:
        checker.add(name)
    assert checker._items == sorted(logins)
    assert all(checker.contains(name) for name in logins)
    assert not checker.contains("user500")


def test_matches_linear_scan_on_random_data():
    """Agrees with Python's `in` on a list for random queries."""
    rng = random.Random(0)
    logins = [f"u{rng.randrange(10_000)}" for _ in range(2_000)]
    checker = BinarySearch(logins)
    for _ in range(1_000):
        query = f"u{rng.randrange(10_000)}"
        assert checker.contains(query) == (query in logins)
