"""Short demo: register users and check new logins with all five structures.

Usage:
  python demo.py
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from login_checker.binary_search import BinarySearch  # noqa: E402
from login_checker.bloom_filter import BloomFilter  # noqa: E402
from login_checker.cuckoo_filter import CuckooFilter  # noqa: E402
from login_checker.dataset import generate_logins  # noqa: E402
from login_checker.hash_table import HashTable  # noqa: E402
from login_checker.linear_search import LinearSearch  # noqa: E402

N = 100_000


def main() -> None:
    """Build each structure from N logins and check a few usernames."""
    logins = generate_logins(N, seed=520)
    print(f"Existing users: {N:,} logins, e.g. {', '.join(logins[:4])}\n")

    checkers = {
        "Linear search": LinearSearch(logins),
        "Binary search": BinarySearch(logins),
        "Hash table": HashTable(logins),
        "Bloom filter": BloomFilter(expected_items=N, fp_rate=0.01, logins=logins),
        "Cuckoo filter": CuckooFilter(capacity=N, logins=logins),
    }

    # Two taken logins and two that no one has registered.
    queries = [logins[0], logins[N // 2], "brand_new_user_2026", "cosc520_student"]
    for login in queries:
        print(f"Is '{login}' taken?")
        for name, checker in checkers.items():
            start = time.perf_counter()
            taken = checker.contains(login)
            micros = (time.perf_counter() - start) * 1e6
            print(f"  {name:<14} {'TAKEN' if taken else 'available':<10} {micros:9.1f} µs")
        print()

    # Registering a new user: check, then add.
    new_user = "cosc520_student"
    print(f"Registering '{new_user}' in every structure...")
    for checker in checkers.values():
        checker.add(new_user)
    print("  now taken in all:", all(c.contains(new_user) for c in checkers.values()))

    # Only the Cuckoo filter can delete (e.g. an account is closed).
    cuckoo = checkers["Cuckoo filter"]
    cuckoo.delete(new_user)
    print(f"  deleted from Cuckoo filter, taken now: {cuckoo.contains(new_user)}")


if __name__ == "__main__":
    main()
