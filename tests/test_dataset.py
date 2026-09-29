"""Unit tests for the dataset generator."""

from login_checker.dataset import generate_logins, load_logins, save_logins


def test_generates_requested_count():
    """Returns exactly the number of logins asked for."""
    assert len(generate_logins(5_000)) == 5_000


def test_logins_are_unique():
    """No login appears twice."""
    logins = generate_logins(20_000)
    assert len(set(logins)) == len(logins)


def test_same_seed_same_output():
    """The dataset is reproducible from its seed."""
    assert generate_logins(1_000, seed=1) == generate_logins(1_000, seed=1)
    assert generate_logins(1_000, seed=1) != generate_logins(1_000, seed=2)


def test_logins_look_valid():
    """Logins are non-empty and have no spaces or newlines."""
    for login in generate_logins(5_000):
        assert login
        assert " " not in login and "\n" not in login


def test_save_and_load_round_trip(tmp_path):
    """Saving then loading gives back the same list; limit reads a prefix."""
    logins = generate_logins(1_000)
    path = tmp_path / "logins.txt"
    save_logins(logins, path)
    assert load_logins(path) == logins
    assert load_logins(path, limit=10) == logins[:10]
