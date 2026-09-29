"""Binary search over a sorted list."""

from collections.abc import Iterable

from login_checker.base import LoginChecker


class BinarySearch(LoginChecker):
    """Logins kept sorted. Build O(n log n), lookup O(log n), add O(n)."""

    def __init__(self, logins: Iterable[str] = ()) -> None:
        """Input: logins to start with (optional). They are sorted once."""
        self._items: list[str] = sorted(logins)

    def _lower_bound(self, login: str) -> int:
        """Find where a login is, or where it would go.

        Input: login. Output: first index with item >= login.
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
        """Insert a login in sorted order. Input: login. Output: None."""
        self._items.insert(self._lower_bound(login), login)

    def contains(self, login: str) -> bool:
        """Binary search for a login.

        Input: login. Output: True if found.
        """
        index = self._lower_bound(login)
        return index < len(self._items) and self._items[index] == login

    def __len__(self) -> int:
        """Number of stored logins."""
        return len(self._items)
