"""Cuckoo filter (Fan et al., "Cuckoo Filter: Practically Better Than Bloom", 2014)."""

import math
import random
from array import array
from collections.abc import Iterable

from login_checker.base import LoginChecker
from login_checker.hashing import hash64

# Odd constant for hashing a fingerprint when finding the other bucket.
_FP_MIX = 0x5BD1E995


class CuckooFilter(LoginChecker):
    """Stores short fingerprints in buckets; supports delete.

    Each login can go in one of two buckets:
        i1 = hash(login), i2 = i1 XOR hash(fingerprint)
    so we can move a fingerprint without knowing the original login.
    A slot value of 0 means empty.

    Lookup is O(1) (two buckets). False positive rate is at most 2b / 2^f.
    """

    def __init__(
        self,
        capacity: int,
        bucket_size: int = 4,
        fingerprint_bits: int = 12,
        max_kicks: int = 500,
        seed: int = 0,
        logins: Iterable[str] = (),
    ) -> None:
        """Input: expected number of logins, slots per bucket (b),
        fingerprint size in bits (f), max relocations per insert,
        random seed, and starting logins (optional).
        """
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        if bucket_size < 1:
            raise ValueError("bucket_size must be at least 1")
        if not 1 <= fingerprint_bits <= 32:
            raise ValueError("fingerprint_bits must be between 1 and 32")
        # Aim for ~95% load, rounded up to a power of two so we can use a bit mask.
        needed = math.ceil(capacity / (bucket_size * 0.95))
        self.num_buckets = 1 << max(0, (needed - 1).bit_length())
        self.bucket_size = bucket_size
        self.fingerprint_bits = fingerprint_bits
        self.max_kicks = max_kicks
        self._fp_mask = (1 << fingerprint_bits) - 1
        self._index_mask = self.num_buckets - 1
        # One flat array; bucket i is slots [i*b, (i+1)*b).
        typecode = "B" if fingerprint_bits <= 8 else "H" if fingerprint_bits <= 16 else "I"
        self._slots = array(typecode, [0]) * (self.num_buckets * bucket_size)
        self._count = 0
        # Fingerprint left over when an insert fails, kept so it isn't lost.
        self._victim: tuple[int, int] | None = None
        self._rng = random.Random(seed)
        for login in logins:
            self.add(login)

    def _fingerprint_and_index(self, login: str) -> tuple[int, int]:
        """Input: login. Output: (fingerprint, first bucket index)."""
        value = hash64(login)
        fingerprint = (value >> 32) & self._fp_mask
        if fingerprint == 0:
            fingerprint = 1
        return fingerprint, value & self._index_mask

    def alt_index(self, index: int, fingerprint: int) -> int:
        """Input: a bucket index and fingerprint. Output: the other bucket."""
        return (index ^ (fingerprint * _FP_MIX)) & self._index_mask

    def _bucket_has(self, index: int, fingerprint: int) -> bool:
        """Input: bucket index, fingerprint. Output: True if it's in the bucket."""
        start = index * self.bucket_size
        for slot in range(start, start + self.bucket_size):
            if self._slots[slot] == fingerprint:
                return True
        return False

    def _bucket_insert(self, index: int, fingerprint: int) -> bool:
        """Input: bucket index, fingerprint. Output: True if there was a free slot."""
        start = index * self.bucket_size
        for slot in range(start, start + self.bucket_size):
            if self._slots[slot] == 0:
                self._slots[slot] = fingerprint
                return True
        return False

    def _bucket_remove(self, index: int, fingerprint: int) -> bool:
        """Input: bucket index, fingerprint. Output: True if one was removed."""
        start = index * self.bucket_size
        for slot in range(start, start + self.bucket_size):
            if self._slots[slot] == fingerprint:
                self._slots[slot] = 0
                return True
        return False

    def add(self, login: str) -> bool:
        """Insert a login. If both buckets are full, kick out a random
        fingerprint and move it to its other bucket (up to max_kicks times).

        Input: login. Output: True if stored, False if the filter is full.
        """
        if self._victim is not None:
            return False
        fingerprint, i1 = self._fingerprint_and_index(login)
        i2 = self.alt_index(i1, fingerprint)
        if self._bucket_insert(i1, fingerprint) or self._bucket_insert(i2, fingerprint):
            self._count += 1
            return True

        index = self._rng.choice((i1, i2))
        for _ in range(self.max_kicks):
            slot = index * self.bucket_size + self._rng.randrange(self.bucket_size)
            fingerprint, self._slots[slot] = self._slots[slot], fingerprint
            index = self.alt_index(index, fingerprint)
            if self._bucket_insert(index, fingerprint):
                self._count += 1
                return True
        self._victim = (index, fingerprint)
        self._count += 1
        return False

    def contains(self, login: str) -> bool:
        """Look for the login's fingerprint in its two buckets.

        Input: login. Output: False if definitely new, True if probably taken.
        """
        fingerprint, i1 = self._fingerprint_and_index(login)
        i2 = self.alt_index(i1, fingerprint)
        if self._bucket_has(i1, fingerprint) or self._bucket_has(i2, fingerprint):
            return True
        return self._victim is not None and self._victim[1] == fingerprint and self._victim[0] in (i1, i2)

    def delete(self, login: str) -> bool:
        """Remove a login. Only delete logins that were really added.

        Input: login. Output: True if removed, False if not found.
        """
        fingerprint, i1 = self._fingerprint_and_index(login)
        i2 = self.alt_index(i1, fingerprint)
        if self._bucket_remove(i1, fingerprint) or self._bucket_remove(i2, fingerprint):
            removed = True
        elif self._victim is not None and self._victim[1] == fingerprint and self._victim[0] in (i1, i2):
            self._victim = None
            removed = True
        else:
            return False
        self._count -= 1
        # A slot was freed, so try to put the victim back.
        if self._victim is not None:
            index, victim_fp = self._victim
            if self._bucket_insert(index, victim_fp) or self._bucket_insert(self.alt_index(index, victim_fp), victim_fp):
                self._victim = None
        return removed

    @property
    def load_factor(self) -> float:
        """Fraction of slots in use."""
        return self._count / (self.num_buckets * self.bucket_size)

    @property
    def memory_bytes(self) -> int:
        """Size of the slot array in bytes."""
        return len(self._slots) * self._slots.itemsize

    def __len__(self) -> int:
        """Number of stored fingerprints."""
        return self._count
