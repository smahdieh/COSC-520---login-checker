"""Linear search over an unsorted list."""

from collections.abc import Iterable

from login_checker.base import LoginChecker


class LinearSearch(LoginChecker):
    """Logins in a plain list. Lookup is O(n), add is O(1)."""

    def __init__(self, logins: Iterable[str] = ()) -> None:
        """Input: logins to start with (optional)."""
        self._items: list[str] = list(logins)

    def add(self, login: str) -> None:
        """Append a login. Input: login. Output: None."""
        self._items.append(login)

    def contains(self, login: str) -> bool:
        """Compare against every stored login.

        Input: login. Output: True if found.
        """
        for item in self._items:
            if item == login:
                return True
        return False

    def __len__(self) -> int:
        """Number of stored logins."""
        return len(self._items)
