"""Time build and lookup for each data structure over several values of n.

For every n, each structure is built from the first n logins, then timed on
a mix of taken logins (sampled from those n) and new logins (from
absent_logins.txt). Results go to results/results.csv.

Usage:
  python benchmarks/run_benchmarks.py                        # n = 1e3 .. 1e7
  python benchmarks/run_benchmarks.py --sizes 1000 10000     # quick run
"""

import argparse
import csv
import gc
import random
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from login_checker.binary_search import BinarySearch  # noqa: E402
from login_checker.bloom_filter import BloomFilter  # noqa: E402
from login_checker.cuckoo_filter import CuckooFilter  # noqa: E402
from login_checker.dataset import load_logins  # noqa: E402
from login_checker.hash_table import HashTable  # noqa: E402
from login_checker.linear_search import LinearSearch  # noqa: E402

FIELDS = [
    "structure", "n", "build_s", "lookup_us", "lookup_taken_us", "lookup_new_us",
    "queries", "fp_rate", "fp_expected", "memory_bytes", "insert_failures",
]


def build(name: str, logins: list[str]):
    """Build one structure from a list of logins.

    Input: structure name, logins. Output: (structure, insert failures).
    """
    n = len(logins)
    if name == "Linear search":
        return LinearSearch(logins), 0
    if name == "Binary search":
        return BinarySearch(logins), 0
    if name == "Hash table":
        return HashTable(logins), 0
    if name == "Bloom filter":
        return BloomFilter(expected_items=n, fp_rate=0.01, logins=logins), 0
    if name == "Cuckoo filter":
        cuckoo = CuckooFilter(capacity=n)
        failures = sum(1 for login in logins if not cuckoo.add(login))
        return cuckoo, failures
    raise ValueError(f"unknown structure: {name}")


def time_lookups(checker, queries: list[str], repeats: int) -> float:
    """Time contains() over a list of queries.

    Input: structure, queries, number of repeats.
    Output: median time per lookup in microseconds.
    """
    runs = []
    for _ in range(repeats):
        start = time.perf_counter()
        for login in queries:
            checker.contains(login)
        runs.append((time.perf_counter() - start) / len(queries))
    return statistics.median(runs) * 1e6


def memory_bytes(checker) -> int:
    """Estimate memory used by a structure.

    Input: structure. Output: bytes. Filters report their array size;
    exact structures count the containers plus every stored string.
    """
    if hasattr(checker, "memory_bytes"):
        return checker.memory_bytes
    if isinstance(checker, HashTable):
        buckets = checker._buckets
        total = sys.getsizeof(buckets)
        for chain in buckets:
            total += sys.getsizeof(chain) + sum(sys.getsizeof(s) for s in chain)
        return total
    items = checker._items
    return sys.getsizeof(items) + sum(sys.getsizeof(s) for s in items)


def expected_fp(checker) -> float:
    """Theoretical false positive rate. Input: structure. Output: rate (0 if exact)."""
    if isinstance(checker, BloomFilter):
        return checker.expected_fp_rate()
    if isinstance(checker, CuckooFilter):
        return 2 * checker.bucket_size / 2**checker.fingerprint_bits
    return 0.0


def run(sizes, structures, queries_per_kind, linear_queries, repeats, data_dir, out_path):
    """Run every structure at every size and write one CSV row per pair.

    Input: sizes, structure names, queries per kind (taken/new), a smaller
    query count for linear search, timing repeats, data folder, CSV path.
    Output: None.
    """
    max_n = max(sizes)
    print(f"Loading {max_n:,} logins...")
    logins = load_logins(data_dir / "logins.txt", limit=max_n)
    absent = load_logins(data_dir / "absent_logins.txt")
    if len(logins) < max_n:
        sys.exit(f"Only {len(logins):,} logins in dataset; run data/generate_logins.py first.")

    rng = random.Random(520)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for n in sizes:
            subset = logins[:n]
            for name in structures:
                # Linear search is O(n) per lookup, so it gets fewer queries.
                k = linear_queries if name == "Linear search" else queries_per_kind
                taken = rng.sample(subset, min(k, n))
                new = absent[:k]

                start = time.perf_counter()
                checker, failures = build(name, subset)
                build_s = time.perf_counter() - start

                taken_us = time_lookups(checker, taken, repeats)
                new_us = time_lookups(checker, new, repeats)
                # Exact structures never give false positives, so only test the filters.
                if isinstance(checker, (BloomFilter, CuckooFilter)):
                    fp_rate = sum(checker.contains(x) for x in absent) / len(absent)
                else:
                    fp_rate = 0.0

                row = {
                    "structure": name,
                    "n": n,
                    "build_s": build_s,
                    "lookup_us": round((taken_us + new_us) / 2, 4),
                    "lookup_taken_us": round(taken_us, 4),
                    "lookup_new_us": round(new_us, 4),
                    "queries": len(taken) + len(new),
                    "fp_rate": fp_rate,
                    "fp_expected": expected_fp(checker),
                    "memory_bytes": memory_bytes(checker),
                    "insert_failures": failures,
                }
                writer.writerow(row)
                f.flush()
                print(f"n={n:>10,}  {name:<14} build={build_s:8.2f}s  "
                      f"lookup={row['lookup_us']:10.2f}us  fp={fp_rate:.4f}  "
                      f"mem={row['memory_bytes'] / 1e6:8.1f}MB")
                del checker
                gc.collect()
    print(f"Results written to {out_path}")


def main() -> None:
    """Parse arguments and run the benchmark."""
    parser = argparse.ArgumentParser(description="Benchmark the login checkers.")
    parser.add_argument("--sizes", type=int, nargs="+",
                        default=[1_000, 10_000, 100_000, 1_000_000, 10_000_000])
    parser.add_argument("--structures", nargs="+",
                        default=["Linear search", "Binary search", "Hash table",
                                 "Bloom filter", "Cuckoo filter"])
    parser.add_argument("--queries", type=int, default=10_000,
                        help="taken and new queries per structure (each)")
    parser.add_argument("--linear-queries", type=int, default=50,
                        help="taken and new queries for linear search (each)")
    parser.add_argument("--repeats", type=int, default=3, help="timing repeats (median used)")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    parser.add_argument("--out", type=Path, default=ROOT / "results" / "results.csv")
    args = parser.parse_args()
    run(args.sizes, args.structures, args.queries, args.linear_queries,
        args.repeats, args.data_dir, args.out)


if __name__ == "__main__":
    main()
