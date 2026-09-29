"""Hash functions shared by the hash table, Bloom filter and Cuckoo filter.

Note: do not use Python's built-in hash() on strings -- it is randomly salted
per process (PYTHONHASHSEED), so results would not be reproducible.
"""

# TODO: implement your hash function(s) here, e.g. FNV-1a or a wrapper
# around hashlib that returns a 64-bit integer.
