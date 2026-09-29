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
# 1. Generate the dataset
python data/generate_logins.py          # TODO: document arguments

# 2. Run the unit tests
pytest

# 3. Run the benchmarks and make plots
python benchmarks/run_benchmarks.py     # TODO: document arguments
python benchmarks/plot_results.py
```

## Dataset

TODO: link to the uploaded dataset (Zenodo / Kaggle / Hugging Face / Drive).

## Use of GenAI

Generated with Claude (Anthropic), then reviewed and tested by me:

- Repository skeleton: folder layout, config files, README outline, `base.py` interface
- `hashing.py`, `linear_search.py`, `binary_search.py` and their tests
  (`test_hashing.py`, `test_linear_search.py`, `test_binary_search.py`)

Written by me: TODO (e.g. `hash_table.py`, `bloom_filter.py`, `cuckoo_filter.py`,
their tests, dataset generator, benchmarks).

## References

TODO
