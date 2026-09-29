"""Cuckoo filter: buckets of fingerprints with partial-key cuckoo hashing.

Based on Fan, Andersen, Kaminsky and Mitzenmacher, "Cuckoo Filter:
Practically Better Than Bloom", CoNEXT 2014.
"""

import math
import random
from array import array
from collections.abc import Iterable

from login_checker.base import LoginChecker
from login_checker.hashing import hash64

# Odd 32-bit constant used to hash a fingerprint when computing the
# alternate bucket (the same trick as the reference implementation).
_FP_MIX = 0x5BD1E995


class CuckooFilter(LoginChecker):
    """Probabilistic set membership that also supports deletion.

    The table has B buckets (B a power of two) with b slots each. A login x
    is stored as a small f-bit fingerprint in one of two buckets:
        i1 = hash(x) mod B
        i2 = i1 XOR hash(fingerprint) mod B
    Because XOR is its own inverse, either bucket can be computed from the
    other using only the fingerprint, so stored items can be moved
    ("kicked") without knowing the original login.

    A slot value of 0 means empty, so fingerprints are never 0.

    Time:  contains and delete O(b) worst case (2 buckets are read);
           add O(1) amortized expected, at most max_kicks relocations.
    Space: about B * b * f bits; false-positive rate at most 2b / 2^f.
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
        """Allocate a table large enough for `capacity` logins.

        The bucket count is capacity / (bucket_size * 0.95) rounded up to a
        power of two, since the filter reliably reaches about 95% load with
        4-slot buckets.

        Input:  capacity -- expected number of logins (>= 1).
                bucket_size -- b, slots per bucket.
                fingerprint_bits -- f, bits per fingerprint (1..32).
                max_kicks -- relocation attempts before add() gives up.
                seed -- seed for the random choice of which item to kick.
                logins -- initial logins to insert (default: none).
        Output: None.
        """
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        if bucket_size < 1:
            raise ValueError("bucket_size must be at least 1")
        if not 1 <= fingerprint_bits <= 32:
            raise ValueError("fingerprint_bits must be between 1 and 32")
        needed = math.ceil(capacity / (bucket_size * 0.95))
        self.num_buckets = 1 << max(0, (needed - 1).bit_length())
        self.bucket_size = bucket_size
        self.fingerprint_bits = fingerprint_bits
        self.max_kicks = max_kicks
        self._fp_mask = (1 << fingerprint_bits) - 1
        self._index_mask = self.num_buckets - 1
        # Flat array of slots: bucket i occupies [i*b, (i+1)*b).
        typecode = "B" if fingerprint_bits <= 8 else "H" if fingerprint_bits <= 16 else "I"
        self._slots = array(typecode, [0]) * (self.num_buckets * bucket_size)
        self._count = 0
        # If add() runs out of kicks, the last evicted fingerprint is kept
        # here so no previously added login is lost (no false negatives).
        self._victim: tuple[int, int] | None = None
        self._rng = random.Random(seed)
        for login in logins:
            self.add(login)

    def _fingerprint_and_index(self, login: str) -> tuple[int, int]:
        """Compute a login's fingerprint and primary bucket from one hash.

        Input:  login -- the username to hash.
        Output: (fingerprint, i1). The low bits pick the bucket, the high
                32 bits give the fingerprint; a zero fingerprint becomes 1.
        """
        value = hash64(login)
        fingerprint = (value >> 32) & self._fp_mask
        if fingerprint == 0:
            fingerprint = 1
        return fingerprint, value & self._index_mask

    def alt_index(self, index: int, fingerprint: int) -> int:
        """Compute the other candidate bucket for a fingerprint.

        Input:  index -- one of the fingerprint's two buckets.
                fingerprint -- the stored fingerprint.
        Output: the other bucket, index XOR hash(fingerprint), masked to B.
                Applying it twice returns the original index.
        """
        return (index ^ (fingerprint * _FP_MIX)) & self._index_mask

    def _bucket_has(self, index: int, fingerprint: int) -> bool:
        """Check whether a bucket holds a fingerprint.

        Input:  index -- bucket number; fingerprint -- value to find.
        Output: True if any slot in the bucket equals the fingerprint.
        """
        start = index * self.bucket_size
        for slot in range(start, start + self.bucket_size):
            if self._slots[slot] == fingerprint:
                return True
        return False

    def _bucket_insert(self, index: int, fingerprint: int) -> bool:
        """Put a fingerprint in the first empty slot of a bucket.

        Input:  index -- bucket number; fingerprint -- value to store.
        Output: True if stored, False if the bucket was full.
        """
        start = index * self.bucket_size
        for slot in range(start, start + self.bucket_size):
            if self._slots[slot] == 0:
                self._slots[slot] = fingerprint
                return True
        return False

    def _bucket_remove(self, index: int, fingerprint: int) -> bool:
        """Clear one slot in a bucket that holds a fingerprint.

        Input:  index -- bucket number; fingerprint -- value to remove.
        Output: True if a matching slot was cleared, otherwise False.
        """
        start = index * self.bucket_size
        for slot in range(start, start + self.bucket_size):
            if self._slots[slot] == fingerprint:
                self._slots[slot] = 0
                return True
        return False

    def add(self, login: str) -> bool:
        """Insert a login's fingerprint, relocating others if needed.

        Tries both candidate buckets first. If both are full, repeatedly
        evicts a random fingerprint, moves it to its alternate bucket, and
        continues with the evicted item, up to max_kicks times.

        Input:  login -- the username to store.
        Output: True if stored; False if the filter is full. On failure
                the last evicted fingerprint is kept in a victim slot, so
                every earlier login is still reported as present.
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
        """Check the login's two candidate buckets for its fingerprint.

        Input:  login -- the username to look up.
        Output: False if the login is definitely absent; True if it is
                probably present (may be a false positive).
        """
        fingerprint, i1 = self._fingerprint_and_index(login)
        i2 = self.alt_index(i1, fingerprint)
        if self._bucket_has(i1, fingerprint) or self._bucket_has(i2, fingerprint):
            return True
        return self._victim is not None and self._victim[1] == fingerprint and self._victim[0] in (i1, i2)

    def delete(self, login: str) -> bool:
        """Remove one copy of a login's fingerprint.

        Only delete logins that were actually added; deleting a false
        positive would remove another login's fingerprint.

        Input:  login -- the username to remove.
        Output: True if a matching fingerprint was removed, otherwise False.
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
        # A freed slot may make room for the victim again.
        if self._victim is not None:
            index, victim_fp = self._victim
            if self._bucket_insert(index, victim_fp) or self._bucket_insert(self.alt_index(index, victim_fp), victim_fp):
                self._victim = None
        return removed

    @property
    def load_factor(self) -> float:
        """Return the fraction of slots in use."""
        return self._count / (self.num_buckets * self.bucket_size)

    @property
    def memory_bytes(self) -> int:
        """Return the size of the slot array in bytes."""
        return len(self._slots) * self._slots.itemsize

    def __len__(self) -> int:
        """Return the number of fingerprints stored."""
        return self._count
