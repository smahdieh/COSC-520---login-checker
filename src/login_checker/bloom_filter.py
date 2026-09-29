"""Bloom filter (Bloom, 1970)."""

import math
from collections.abc import Iterable, Iterator

from login_checker.base import LoginChecker
from login_checker.hashing import hash_pair


class BloomFilter(LoginChecker):
    """Bit array of m bits with k hash functions.

    No false negatives, but false positives happen with probability
    about (1 - e^(-kn/m))^k. Items can't be removed.
    add and contains are O(k).
    """

    def __init__(
        self,
        expected_items: int,
        fp_rate: float = 0.01,
        logins: Iterable[str] = (),
    ) -> None:
        """Input: expected number of logins n, target false positive rate p,
        and starting logins (optional). m and k are picked from n and p.
        """
        if expected_items < 1:
            raise ValueError("expected_items must be at least 1")
        if not 0 < fp_rate < 1:
            raise ValueError("fp_rate must be between 0 and 1")
        self.num_bits = self.optimal_num_bits(expected_items, fp_rate)
        self.num_hashes = self.optimal_num_hashes(self.num_bits, expected_items)
        self._bits = bytearray((self.num_bits + 7) // 8)
        self._count = 0
        for login in logins:
            self.add(login)

    @staticmethod
    def optimal_num_bits(n: int, p: float) -> int:
        """Input: n, p. Output: m = -n ln(p) / (ln 2)^2, rounded up."""
        return math.ceil(-n * math.log(p) / (math.log(2) ** 2))

    @staticmethod
    def optimal_num_hashes(m: int, n: int) -> int:
        """Input: m, n. Output: k = (m / n) ln 2, rounded (at least 1)."""
        return max(1, round((m / n) * math.log(2)))

    def _positions(self, login: str) -> Iterator[int]:
        """Get the k bit positions using double hashing: (h1 + i*h2) mod m.

        Input: login. Output: k indexes in [0, m).
        """
        h1, h2 = hash_pair(login)
        for i in range(self.num_hashes):
            yield (h1 + i * h2) % self.num_bits

    def add(self, login: str) -> None:
        """Set the login's k bits. Input: login. Output: None."""
        for pos in self._positions(login):
            self._bits[pos >> 3] |= 1 << (pos & 7)
        self._count += 1

    def contains(self, login: str) -> bool:
        """Check the login's k bits.

        Input: login. Output: False if definitely new, True if probably taken.
        """
        for pos in self._positions(login):
            if not self._bits[pos >> 3] & (1 << (pos & 7)):
                return False
        return True

    def expected_fp_rate(self) -> float:
        """Theoretical false positive rate for the items added so far."""
        k, m = self.num_hashes, self.num_bits
        return (1 - math.exp(-k * self._count / m)) ** k

    @property
    def memory_bytes(self) -> int:
        """Size of the bit array in bytes."""
        return len(self._bits)

    def __len__(self) -> int:
        """Number of logins added."""
        return self._count
