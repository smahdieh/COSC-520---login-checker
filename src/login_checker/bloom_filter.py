"""Bloom filter: m-bit array with k hash functions (Bloom, 1970)."""

import math
from collections.abc import Iterable, Iterator

from login_checker.base import LoginChecker
from login_checker.hashing import hash_pair


class BloomFilter(LoginChecker):
    """Probabilistic set membership using an m-bit array and k hashes.

    add sets k bits; contains checks that all k bits are set. There are no
    false negatives, but a login never added may be reported as present
    with probability p = (1 - e^(-kn/m))^k. Logins cannot be removed.

    The k bit positions come from double hashing (Kirsch & Mitzenmacher,
    2006): g_i(x) = (h1(x) + i * h2(x)) mod m, for i = 0..k-1.

    Time:  add and contains O(k).
    Space: m bits, independent of login length.
    """

    def __init__(
        self,
        expected_items: int,
        fp_rate: float = 0.01,
        logins: Iterable[str] = (),
    ) -> None:
        """Size the filter for n items at a target false-positive rate.

        Uses the optimal sizing formulas:
            m = ceil(-n * ln(p) / (ln 2)^2)   bits
            k = round((m / n) * ln 2)         hash functions

        Input:  expected_items -- n, the number of logins expected (>= 1).
                fp_rate -- p, the target false-positive rate, in (0, 1).
                logins -- initial logins to insert (default: none).
        Output: None.
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
        """Compute the bit-array size m for n items and false-positive rate p.

        Input:  n -- expected number of items; p -- target false-positive rate.
        Output: m = ceil(-n ln p / (ln 2)^2).
        """
        return math.ceil(-n * math.log(p) / (math.log(2) ** 2))

    @staticmethod
    def optimal_num_hashes(m: int, n: int) -> int:
        """Compute the number of hash functions k that minimizes false positives.

        Input:  m -- number of bits; n -- expected number of items.
        Output: k = round((m / n) ln 2), at least 1.
        """
        return max(1, round((m / n) * math.log(2)))

    def _positions(self, login: str) -> Iterator[int]:
        """Yield the k bit positions for a login.

        Input:  login -- the username to hash.
        Output: k integers in [0, m), from (h1 + i * h2) mod m.
        """
        h1, h2 = hash_pair(login)
        for i in range(self.num_hashes):
            yield (h1 + i * h2) % self.num_bits

    def add(self, login: str) -> None:
        """Set the k bits for a login.

        Input:  login -- the username to store.
        Output: None.
        """
        for pos in self._positions(login):
            self._bits[pos >> 3] |= 1 << (pos & 7)
        self._count += 1

    def contains(self, login: str) -> bool:
        """Check whether all k bits for a login are set.

        Input:  login -- the username to look up.
        Output: False if the login was definitely never added; True if it
                probably was (may be a false positive).
        """
        for pos in self._positions(login):
            if not self._bits[pos >> 3] & (1 << (pos & 7)):
                return False
        return True

    def expected_fp_rate(self) -> float:
        """Estimate the current false-positive rate from the items added so far.

        Input:  none.
        Output: (1 - e^(-k * count / m))^k.
        """
        k, m = self.num_hashes, self.num_bits
        return (1 - math.exp(-k * self._count / m)) ** k

    @property
    def memory_bytes(self) -> int:
        """Return the size of the bit array in bytes."""
        return len(self._bits)

    def __len__(self) -> int:
        """Return how many add() calls have been made."""
        return self._count
