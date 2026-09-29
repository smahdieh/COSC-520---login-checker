"""Unit tests for HashTable."""

import pytest

from login_checker.hash_table import HashTable


def test_empty_contains_nothing():
    """A new, empty table reports every login as free."""
    assert not HashTable().contains("alice")


def test_added_login_is_found():
    """A login is found after it is added; others are not."""
    table = HashTable()
    table.add("alice")
    assert table.contains("alice")
    assert "alice" in table
    assert not table.contains("bob")


def test_long_chains_still_work():
    """With resizing effectively disabled, collisions form chains that are scanned correctly."""
    table = HashTable(initial_capacity=2, max_load_factor=1_000)
    logins = [f"user{i}" for i in range(200)]
    for name in logins:
        table.add(name)
    assert table.capacity == 2
    assert all(table.contains(name) for name in logins)
    assert not table.contains("user200")


def test_resize_keeps_all_logins():
    """Growing past the load factor doubles capacity and keeps every login."""
    table = HashTable(initial_capacity=4, max_load_factor=0.75)
    logins = [f"user{i}" for i in range(1_000)]
    for name in logins:
        table.add(name)
    assert table.capacity > 4
    assert table.load_factor <= 0.75
    assert all(table.contains(name) for name in logins)


def test_duplicates_are_stored_once():
    """Adding the same login twice does not increase the size."""
    table = HashTable(["alice"])
    table.add("alice")
    assert len(table) == 1


def test_invalid_arguments_raise():
    """Non-positive capacity or load factor is rejected."""
    with pytest.raises(ValueError):
        HashTable(initial_capacity=0)
    with pytest.raises(ValueError):
        HashTable(max_load_factor=0)
