"""Create and load synthetic login datasets."""

import random
import string
from pathlib import Path

FIRST_NAMES = [
    "alex", "amir", "anna", "ben", "chen", "chris", "david", "elena", "emma", "fatemeh",
    "hana", "ivan", "jack", "james", "jin", "julia", "kate", "leo", "li", "lucas",
    "maria", "mahdi", "maya", "mike", "mohammed", "nina", "noah", "olivia", "omar", "priya",
    "raj", "reza", "sam", "sara", "sofia", "tom", "wei", "yuki", "zara", "zoe",
]
LAST_NAMES = [
    "ahmadi", "brown", "chen", "davis", "garcia", "gupta", "hosseini", "johnson", "kim", "lee",
    "lopez", "martin", "miller", "nguyen", "patel", "rossi", "sato", "silva", "smith", "taylor",
    "wang", "wilson", "wong", "young", "zhang",
]
WORDS = [
    "blue", "cat", "cloud", "code", "dark", "dragon", "fire", "fox", "game", "ghost",
    "happy", "king", "lion", "moon", "ninja", "pixel", "queen", "red", "shadow", "sky",
    "star", "storm", "sun", "tiger", "wolf",
]
SEPARATORS = ["", "", ".", "_"]
RANDOM_CHARS = string.ascii_lowercase + string.digits


def _name_login(rng: random.Random) -> str:
    """Input: rng. Output: a login like 'sara.patel', 'jlee42' or 'omar_ahmadi7'."""
    first, last = rng.choice(FIRST_NAMES), rng.choice(LAST_NAMES)
    if rng.random() < 0.3:
        first = first[0]
    login = first + rng.choice(SEPARATORS) + last
    if rng.random() < 0.7:
        login += str(rng.randrange(10 ** rng.randint(1, 4)))
    return login


def _word_login(rng: random.Random) -> str:
    """Input: rng. Output: a login like 'darkwolf' or 'pixel_ninja2024'."""
    login = rng.choice(WORDS) + rng.choice(SEPARATORS) + rng.choice(WORDS)
    if rng.random() < 0.8:
        login += str(rng.randrange(10 ** rng.randint(1, 4)))
    return login


def _random_login(rng: random.Random) -> str:
    """Input: rng. Output: a random 6-16 character login like 'x7kq2pzd'."""
    length = rng.randint(6, 16)
    return "".join(rng.choices(RANDOM_CHARS, k=length))


def generate_logins(count: int, seed: int = 520) -> list[str]:
    """Make `count` unique logins from a mix of name, word and random patterns.

    Input: number of logins, random seed (same seed gives the same list).
    Output: list of unique logins in generation order.
    """
    rng = random.Random(seed)
    makers = [_name_login, _word_login, _random_login]
    weights = [0.4, 0.3, 0.3]
    seen: set[str] = set()
    logins: list[str] = []
    while len(logins) < count:
        login = rng.choices(makers, weights)[0](rng)
        if login not in seen:
            seen.add(login)
            logins.append(login)
    return logins


def save_logins(logins: list[str], path: str | Path) -> None:
    """Write one login per line. Input: logins, file path. Output: None."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write("\n".join(logins))
        f.write("\n")


def load_logins(path: str | Path, limit: int | None = None) -> list[str]:
    """Read logins from a file.

    Input: file path, optional max number of lines to read.
    Output: list of logins.
    """
    logins = []
    with Path(path).open(encoding="utf-8") as f:
        for line in f:
            if limit is not None and len(logins) >= limit:
                break
            logins.append(line.rstrip("\n"))
    return logins
