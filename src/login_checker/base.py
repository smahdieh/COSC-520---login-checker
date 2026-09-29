"""Common interface shared by all login-checker data structures."""

from abc import ABC, abstractmethod


class LoginChecker(ABC):
    """Abstract base class for a structure that answers "is this login taken?".

    Every implementation exposes the same two methods so the benchmark
    code can treat all five structures uniformly.
    """

    @abstractmethod
    def add(self, login: str) -> None:
        """Insert a login into the structure.

        Input:  login -- the username to store.
        Output: None.
        """

    @abstractmethod
    def contains(self, login: str) -> bool:
        """Check whether a login is (probably) already taken.

        Input:  login -- the username to look up.
        Output: True if the login is present (filters may return a false
                positive), False if it is definitely not present.
        """

    def __contains__(self, login: str) -> bool:
        """Allow the `login in checker` syntax; delegates to contains()."""
        return self.contains(login)
