"""Hash functions used by the hash table and the filters.

We use BLAKE2b instead of Python's hash() because hash() changes
between runs, which would make the results non-reproducible.
"""

import hashlib

MASK_64 = (1 << 64) - 1


def hash64(text: str, seed: int = 0) -> int:
    """Hash a string to a 64-bit integer.

    Input: text, seed (a different seed gives a different hash function).
    Output: int in [0, 2^64).
    """
    key = (seed & MASK_64).to_bytes(8, "little")
    digest = hashlib.blake2b(text.encode("utf-8"), digest_size=8, key=key).digest()
    return int.from_bytes(digest, "little")


def hash_pair(text: str) -> tuple[int, int]:
    """Split one 64-bit hash into two 32-bit hashes for double hashing.

    Input: text. Output: (h1, h2), with h2 always odd so it is never 0.
    """
    value = hash64(text)
    h1 = value & 0xFFFFFFFF
    h2 = (value >> 32) | 1
    return h1, h2
