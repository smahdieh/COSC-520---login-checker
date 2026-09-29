"""Hash table of logins (own implementation, not dict/set)."""

from collections.abc import Iterable

from login_checker.base import LoginChecker
from login_checker.hashing import hash64


class HashTable(LoginChecker):
    """Hash set of logins using separate chaining and automatic resizing.

    Each bucket is a Python list (a "chain") holding the logins that hash
    to it. When the load factor alpha = size / capacity exceeds the limit,
    the bucket array doubles and every login is re-inserted.

    Time:  add and contains O(1 + alpha) expected, O(n) worst case
           (all logins in one chain); a resize costs O(n) but happens
           rarely, so add is O(1) amortized.
    Space: O(n + capacity).
    """

    def __init__(
        self,
        logins: Iterable[str] = (),
        initial_capacity: int = 8,
        max_load_factor: float = 0.75,
    ) -> None:
        """Create an empty table, then insert any initial logins.

        Input:  logins -- initial logins to store (default: none).
                initial_capacity -- starting number of buckets (>= 1).
                max_load_factor -- resize when size / capacity exceeds this.
        Output: None.
        """
        if initial_capacity < 1:
            raise ValueError("initial_capacity must be at least 1")
        if max_load_factor <= 0:
            raise ValueError("max_load_factor must be positive")
        self._buckets: list[list[str]] = [[] for _ in range(initial_capacity)]
        self._size = 0
        self._max_load = max_load_factor
        for login in logins:
            self.add(login)

    @property
    def capacity(self) -> int:
        """Return the current number of buckets."""
        return len(self._buckets)

    @property
    def load_factor(self) -> float:
        """Return alpha = number of stored logins / number of buckets."""
        return self._size / len(self._buckets)

    def _bucket_for(self, login: str) -> list[str]:
        """Return the chain that a login belongs in.

        Input:  login -- the username to locate.
        Output: the bucket list at index hash(login) mod capacity.
        """
        return self._buckets[hash64(login) % len(self._buckets)]

    def _resize(self, new_capacity: int) -> None:
        """Rebuild the table with a new number of buckets.

        Input:  new_capacity -- the number of buckets after resizing.
        Output: None. Every stored login is re-hashed into the new array.
        """
        old_buckets = self._buckets
        self._buckets = [[] for _ in range(new_capacity)]
        for chain in old_buckets:
            for login in chain:
                self._bucket_for(login).append(login)

    def add(self, login: str) -> None:
        """Insert a login if it is not already stored.

        Input:  login -- the username to store.
        Output: None. Duplicates are ignored, so the table acts as a set.
        """
        chain = self._bucket_for(login)
        for item in chain:
            if item == login:
                return
        chain.append(login)
        self._size += 1
        if self.load_factor > self._max_load:
            self._resize(2 * len(self._buckets))

    def contains(self, login: str) -> bool:
        """Hash the login and scan only its chain.

        Input:  login -- the username to look up.
        Output: True if the login is stored, otherwise False.
        """
        for item in self._bucket_for(login):
            if item == login:
                return True
        return False

    def __len__(self) -> int:
        """Return the number of distinct stored logins."""
        return self._size
