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
├── tests/                 # unit tests (pytest)
└── demo.py                # short demo of all five structures
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

# 3. Quick demo (5 structures on 100K logins, a few seconds)
python demo.py

# 4. Run the benchmarks (n = 1e3 .. 1e7, about 10-15 min) and make plots
python benchmarks/run_benchmarks.py
python benchmarks/plot_results.py
```

Benchmark options:

| Option | Default | Meaning |
|---|---|---|
| `--sizes` | `1000 10000 100000 1000000 10000000` | values of n to test |
| `--structures` | all five | e.g. `--structures "Hash table" "Bloom filter"` |
| `--queries` | `10000` | taken and new lookups per structure (each) |
| `--linear-queries` | `50` | fewer lookups for linear search, since it is O(n) |
| `--repeats` | `3` | timing repeats; the median is reported |

For each n, every structure is built from the first n logins, then timed on
lookups of logins that are taken (sampled from those n) and new (from
`absent_logins.txt`). False positive rates for the filters use all 100,000
absent logins. Output: `results/results.csv` and the plots in `results/`:

| Plot | Shows |
|---|---|
| `lookup_time.png` | time per lookup vs n, all five structures |
| `lookup_time_fast.png` | same, without linear search |
| `build_time.png` | time to insert all n logins |
| `memory.png` | bytes used vs n |
| `false_positive_rate.png` | Bloom and Cuckoo: measured vs theoretical |

## Dataset

Download: https://doi.org/10.5281/zenodo.23045991

> Sadatbenis, M. (2026). *Login Dataset for COSC 520 Login Checker* [Dataset]. Zenodo. https://doi.org/10.5281/zenodo.23045991

**Access is restricted:** the Zenodo record is public, but the files are
available on request only. Use "Request access" on the Zenodo page, or
regenerate the identical dataset with `python data/generate_logins.py` (seed 520).

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
- Dataset generator (`dataset.py`, `data/generate_logins.py`, `test_dataset.py`)
- Benchmark and plotting scripts (`benchmarks/`) and `demo.py`

My changes and additions: TODO (list what you modified in each file, and what
you wrote yourself, e.g. dataset generator, benchmarks, plots).

## References

1. T. H. Cormen, C. E. Leiserson, R. L. Rivest, C. Stein. *Introduction to Algorithms*, 4th ed. MIT Press, 2022.
2. B. H. Bloom. Space/time trade-offs in hash coding with allowable errors. *Communications of the ACM* 13(7), 1970.
3. A. Broder, M. Mitzenmacher. Network applications of Bloom filters: A survey. *Internet Mathematics* 1(4), 2004.
4. A. Kirsch, M. Mitzenmacher. Less hashing, same performance: Building a better Bloom filter. *ESA*, 2006.
5. B. Fan, D. G. Andersen, M. Kaminsky, M. Mitzenmacher. Cuckoo filter: Practically better than Bloom. *CoNEXT*, 2014.
