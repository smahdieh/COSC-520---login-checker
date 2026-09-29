"""Unit tests for LinearSearch."""

from login_checker.linear_search import LinearSearch


def test_empty_contains_nothing():
    """A new, empty structure reports every login as free."""
    assert not LinearSearch().contains("alice")


def test_added_login_is_found():
    """A login is found after it is added."""
    checker = LinearSearch()
    checker.add("alice")
    assert checker.contains("alice")
    assert "alice" in checker


def test_missing_login_is_not_found():
    """Logins that were never added are reported as free."""
    checker = LinearSearch(["alice", "bob"])
    assert not checker.contains("carol")


def test_match_is_exact():
    """Lookup is case-sensitive and does not match prefixes."""
    checker = LinearSearch(["Alice"])
    assert not checker.contains("alice")
    assert not checker.contains("Ali")


def test_initial_logins_and_length():
    """Logins passed to the constructor are stored and counted."""
    logins = [f"user{i}" for i in range(100)]
    checker = LinearSearch(logins)
    assert len(checker) == 100
    assert all(checker.contains(name) for name in logins)
