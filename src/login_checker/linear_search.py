"""Unsorted list of logins checked with a linear scan."""

from collections.abc import Iterable

from login_checker.base import LoginChecker


class LinearSearch(LoginChecker):
    """Stores logins in an unsorted list and scans every element on lookup.

    Time:  add O(1) amortized, contains O(n) comparisons.
    Space: O(n) references to the stored strings.
    """

    def __init__(self, logins: Iterable[str] = ()) -> None:
        """Create the structure, optionally pre-loaded with logins.

        Input:  logins -- initial logins to store (default: none).
        Output: None.
        """
        self._items: list[str] = list(logins)

    def add(self, login: str) -> None:
        """Append a login to the end of the list.

        Input:  login -- the username to store.
        Output: None.
        """
        self._items.append(login)

    def contains(self, login: str) -> bool:
        """Scan the list from start to end looking for an exact match.

        Input:  login -- the username to look up.
        Output: True if the login is stored, otherwise False.
        """
        for item in self._items:
            if item == login:
                return True
        return False

    def __len__(self) -> int:
        """Return the number of stored logins."""
        return len(self._items)
