"""Cuckoo filter: buckets of fingerprints with partial-key cuckoo hashing."""

from login_checker.base import LoginChecker


class CuckooFilter(LoginChecker):
    """Cuckoo filter: buckets of fingerprints with partial-key cuckoo hashing."""

    def __init__(self) -> None:
        # TODO: choose constructor parameters and initialize storage
        raise NotImplementedError

    def add(self, login: str) -> None:
        # TODO
        raise NotImplementedError

    def contains(self, login: str) -> bool:
        # TODO
        raise NotImplementedError
