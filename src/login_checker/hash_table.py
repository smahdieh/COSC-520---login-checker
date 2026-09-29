"""Hash table of logins (own implementation, not dict/set)."""

from login_checker.base import LoginChecker


class HashTable(LoginChecker):
    """Hash table of logins (own implementation, not dict/set)."""

    def __init__(self) -> None:
        # TODO: choose constructor parameters and initialize storage
        raise NotImplementedError

    def add(self, login: str) -> None:
        # TODO
        raise NotImplementedError

    def contains(self, login: str) -> bool:
        # TODO
        raise NotImplementedError
