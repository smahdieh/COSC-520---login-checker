"""Hash table with separate chaining."""

from collections.abc import Iterable

from login_checker.base import LoginChecker
from login_checker.hashing import hash64


class HashTable(LoginChecker):
    """Each bucket is a list of logins. Doubles in size when too full.

    Lookup and add are O(1) on average, O(n) in the worst case.
    """

    def __init__(
        self,
        logins: Iterable[str] = (),
        initial_capacity: int = 8,
        max_load_factor: float = 0.75,
    ) -> None:
        """Input: starting logins (optional), number of buckets, and the
        load factor that triggers a resize.
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
        """Number of buckets."""
        return len(self._buckets)

    @property
    def load_factor(self) -> float:
        """Stored logins / buckets."""
        return self._size / len(self._buckets)

    def _bucket_for(self, login: str) -> list[str]:
        """Input: login. Output: the bucket it hashes to."""
        return self._buckets[hash64(login) % len(self._buckets)]

    def _resize(self, new_capacity: int) -> None:
        """Rehash every login into a new bucket array.

        Input: new number of buckets. Output: None.
        """
        old_buckets = self._buckets
        self._buckets = [[] for _ in range(new_capacity)]
        for chain in old_buckets:
            for login in chain:
                self._bucket_for(login).append(login)

    def add(self, login: str) -> None:
        """Add a login (duplicates are ignored). Input: login. Output: None."""
        chain = self._bucket_for(login)
        for item in chain:
            if item == login:
                return
        chain.append(login)
        self._size += 1
        if self.load_factor > self._max_load:
            self._resize(2 * len(self._buckets))

    def contains(self, login: str) -> bool:
        """Look in the login's bucket only.

        Input: login. Output: True if found.
        """
        for item in self._bucket_for(login):
            if item == login:
                return True
        return False

    def __len__(self) -> int:
        """Number of stored logins."""
        return self._size
