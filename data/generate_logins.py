"""Generate the login dataset used by the benchmarks.

Creates two files:
  logins.txt         -- n registered logins (the data we store)
  absent_logins.txt  -- logins that are NOT in logins.txt (used to test
                        "new user" lookups and to measure false positives)

Usage:
  python data/generate_logins.py                  # 10 million logins
  python data/generate_logins.py --n 100000       # smaller test run
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from login_checker.dataset import generate_logins, save_logins  # noqa: E402

DATA_DIR = Path(__file__).resolve().parent


def main() -> None:
    """Parse arguments, generate the logins and write both files."""
    parser = argparse.ArgumentParser(description="Generate synthetic login datasets.")
    parser.add_argument("--n", type=int, default=10_000_000, help="number of registered logins")
    parser.add_argument("--absent", type=int, default=100_000, help="number of absent logins")
    parser.add_argument("--seed", type=int, default=520, help="random seed")
    parser.add_argument("--out-dir", type=Path, default=DATA_DIR, help="output folder")
    args = parser.parse_args()

    start = time.perf_counter()
    # Generate both sets together so absent logins are guaranteed to be unused.
    logins = generate_logins(args.n + args.absent, seed=args.seed)
    registered, absent = logins[: args.n], logins[args.n :]

    save_logins(registered, args.out_dir / "logins.txt")
    save_logins(absent, args.out_dir / "absent_logins.txt")
    elapsed = time.perf_counter() - start
    print(f"Wrote {len(registered):,} logins and {len(absent):,} absent logins "
          f"to {args.out_dir} in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
