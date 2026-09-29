"""Bloom filter: m-bit array with k hash functions."""

from login_checker.base import LoginChecker


class BloomFilter(LoginChecker):
    """Bloom filter: m-bit array with k hash functions."""

    def __init__(self) -> None:
        # TODO: choose constructor parameters and initialize storage
        raise NotImplementedError

    def add(self, login: str) -> None:
        # TODO
        raise NotImplementedError

    def contains(self, login: str) -> bool:
        # TODO
        raise NotImplementedError
