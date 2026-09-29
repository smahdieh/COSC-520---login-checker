"""Base class for all login checkers."""

from abc import ABC, abstractmethod


class LoginChecker(ABC):
    """Common interface so every structure can be benchmarked the same way."""

    @abstractmethod
    def add(self, login: str) -> None:
        """Store a login.

        Input: login (str). Output: None.
        """

    @abstractmethod
    def contains(self, login: str) -> bool:
        """Check if a login is taken.

        Input: login (str). Output: True if found (filters can give false positives).
        """

    def __contains__(self, login: str) -> bool:
        """Support `login in checker`."""
        return self.contains(login)
