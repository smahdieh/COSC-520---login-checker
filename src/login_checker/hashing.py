"""Hash functions shared by the hash table, Bloom filter and Cuckoo filter.

Python's built-in hash() is not used because it is randomly salted per
process (PYTHONHASHSEED), which would make results non-reproducible.
BLAKE2b from the standard library is used only as a hash *function*;
all data structures are implemented by hand.
"""

import hashlib

MASK_64 = (1 << 64) - 1


def hash64(text: str, seed: int = 0) -> int:
    """Hash a string to a 64-bit unsigned integer.

    Input:  text -- the string to hash.
            seed -- integer selecting an independent hash function
                    (different seeds give unrelated outputs).
    Output: an integer in [0, 2**64).
    """
    key = (seed & MASK_64).to_bytes(8, "little")
    digest = hashlib.blake2b(text.encode("utf-8"), digest_size=8, key=key).digest()
    return int.from_bytes(digest, "little")


def hash_pair(text: str) -> tuple[int, int]:
    """Return two independent 32-bit hashes of a string from one digest.

    Useful for double hashing (Kirsch & Mitzenmacher, 2006), where the i-th
    hash position is computed as (h1 + i * h2) mod m.

    Input:  text -- the string to hash.
    Output: (h1, h2) -- two integers in [0, 2**32); h2 is forced to be odd
            so that it is never 0 and cycles through all positions when m
            is a power of two.
    """
    value = hash64(text)
    h1 = value & 0xFFFFFFFF
    h2 = (value >> 32) | 1
    return h1, h2
