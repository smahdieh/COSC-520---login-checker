"""Unsorted list of logins checked with a linear scan."""

from login_checker.base import LoginChecker


class LinearSearch(LoginChecker):
    """Unsorted list of logins checked with a linear scan."""

    def __init__(self) -> None:
        # TODO: choose constructor parameters and initialize storage
        raise NotImplementedError

    def add(self, login: str) -> None:
        # TODO
        raise NotImplementedError

    def contains(self, login: str) -> bool:
        # TODO
        raise NotImplementedError
