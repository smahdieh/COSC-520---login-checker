# Login Checker: Comparing Search Structures, Bloom and Cuckoo Filters

COSC 520 – Assignment 1 (UBC Okanagan, Fall 2026)

Checks whether a new login (username) is already taken using five approaches,
all implemented from scratch:

| Module | Approach | Exact? |
|---|---|---|
| `linear_search.py` | Unsorted list + linear scan | yes |
| `binary_search.py` | Sorted array + binary search | yes |
| `hash_table.py` | Hash table (own implementation) | yes |
| `bloom_filter.py` | Bloom filter | false positives possible |
| `cuckoo_filter.py` | Cuckoo filter | false positives possible |

## Project structure

```
login-checker/
├── src/login_checker/     # data structure implementations
├── data/                  # dataset generator (generated data is not committed)
├── benchmarks/            # timing scripts and plotting
├── results/               # benchmark CSVs and figures
└── tests/                 # unit tests (pytest)
```

## Setup

Requires Python 3.10+.

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running

```bash
# 1. Generate the dataset (10M logins, ~50 s, ~120 MB)
python data/generate_logins.py
#    or a smaller one for a quick try:
python data/generate_logins.py --n 100000

# 2. Run the unit tests
pytest

# 3. Run the benchmarks and make plots
python benchmarks/run_benchmarks.py     # TODO: document arguments
python benchmarks/plot_results.py
```

## Dataset

Download: https://doi.org/10.5281/zenodo.23045991

> Sadatbenis, M. (2026). *Login Dataset for COSC 520 Login Checker* [Dataset]. Zenodo. https://doi.org/10.5281/zenodo.23045991

Or regenerate it exactly with `python data/generate_logins.py` (seed 520).

| File | Contents |
|---|---|
| `logins.txt` | 10,000,000 unique registered logins, one per line (~120 MB) |
| `absent_logins.txt` | 100,000 logins guaranteed not in `logins.txt`, used for "new user" lookups and false-positive rates |

Logins mix three patterns: names (`sara.patel`, `jlee42`), word pairs
(`blue.moon874`) and random strings (`x7kq2pzd`). Average length is 11.6
characters (min 4, max 21).

**Why n = 10 million and not 1 billion:** a Python string takes about 50-60
bytes, so 10^9 logins would need over 50 GB of RAM just for the strings. The
test machine (Apple M1 Pro, 16 GB RAM) handles 10^7 comfortably, which is enough
to see how each structure scales across four orders of magnitude (10^3 to 10^7).

## Use of GenAI

Generated with Claude (Anthropic), then reviewed and tested by me:

- Repository skeleton: folder layout, config files, README outline, `base.py` interface
- Initial versions of all data structures in `src/login_checker/`
  (`hashing.py`, `linear_search.py`, `binary_search.py`, `hash_table.py`,
  `bloom_filter.py`, `cuckoo_filter.py`) and their unit tests in `tests/`

My changes and additions: TODO (list what you modified in each file, and what
you wrote yourself, e.g. dataset generator, benchmarks, plots).

## References

TODO
