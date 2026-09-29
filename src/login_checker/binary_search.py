"""Sorted array of logins checked with binary search."""

from collections.abc import Iterable

from login_checker.base import LoginChecker


class BinarySearch(LoginChecker):
    """Keeps logins in a sorted list and finds them by binary search.

    Time:  build O(n log n) (one sort), contains O(log n) comparisons,
           add O(n) because later elements must shift to keep order.
    Space: O(n) references to the stored strings.
    """

    def __init__(self, logins: Iterable[str] = ()) -> None:
        """Create the structure, sorting any initial logins once.

        Input:  logins -- initial logins to store (default: none).
        Output: None.
        """
        self._items: list[str] = sorted(logins)

    def _lower_bound(self, login: str) -> int:
        """Find the first index whose item is >= login.

        Input:  login -- the username to position.
        Output: index in [0, len(items)] where login is, or would be inserted.
        """
        lo, hi = 0, len(self._items)
        while lo < hi:
            mid = (lo + hi) // 2
            if self._items[mid] < login:
                lo = mid + 1
            else:
                hi = mid
        return lo

    def add(self, login: str) -> None:
        """Insert a login at its sorted position.

        Input:  login -- the username to store.
        Output: None.
        """
        self._items.insert(self._lower_bound(login), login)

    def contains(self, login: str) -> bool:
        """Binary-search the sorted list for an exact match.

        Input:  login -- the username to look up.
        Output: True if the login is stored, otherwise False.
        """
        index = self._lower_bound(login)
        return index < len(self._items) and self._items[index] == login

    def __len__(self) -> int:
        """Return the number of stored logins."""
        return len(self._items)
