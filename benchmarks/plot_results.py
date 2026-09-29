"""Read results/results.csv and make the comparison plots in results/.

Usage:
  python benchmarks/plot_results.py
"""

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

# Fixed color + marker per structure, so each one looks the same in every plot
# and can still be told apart when printed in grayscale.
STYLE = {
    "Linear search": ("#2a78d6", "o"),
    "Binary search": ("#eb6834", "s"),
    "Hash table": ("#1baf7a", "^"),
    "Bloom filter": ("#eda100", "D"),
    "Cuckoo filter": ("#e87ba4", "v"),
}
TEXT = "#0b0b0b"
MUTED = "#52514e"
GRID = "#e4e3df"


def load(path: Path) -> dict[str, list[dict]]:
    """Read the CSV. Input: path. Output: {structure: rows sorted by n}."""
    rows = defaultdict(list)
    with path.open() as f:
        for row in csv.DictReader(f):
            for key, value in row.items():
                if key != "structure":
                    row[key] = float(value)
            rows[row["structure"]].append(row)
    for series in rows.values():
        series.sort(key=lambda r: r["n"])
    return rows


def style_axes(ax, title: str, ylabel: str) -> None:
    """Apply shared styling. Input: axes, title, y label. Output: None."""
    ax.set_title(title, loc="left", fontsize=12, color=TEXT, pad=10)
    ax.set_xlabel("Number of logins n", color=MUTED)
    ax.set_ylabel(ylabel, color=MUTED)
    ax.grid(True, which="major", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED)
    ax.tick_params(colors=MUTED)


def line_plot(rows, field, title, ylabel, out_path, names=None, note=None, log_y=True) -> None:
    """Draw one log-log line per structure.

    Input: data, CSV column to plot, title, y label, output file,
    optional list of structures to include, optional note, log or linear y axis.
    Output: None (saves a PNG).
    """
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for name in names or STYLE:
        if name not in rows:
            continue
        color, marker = STYLE[name]
        # Skip zero values (too fast to measure), which can't go on a log axis.
        points = [(r["n"], r[field]) for r in rows[name] if r[field] > 0]
        xs, ys = zip(*points)
        ax.plot(xs, ys, color=color, marker=marker, markersize=6, linewidth=2, label=name)
    ax.set_xscale("log")
    if log_y:
        ax.set_yscale("log")
    else:
        ax.set_ylim(bottom=0)
    style_axes(ax, title, ylabel)
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    if note:
        ax.text(0.99, 0.02, note, transform=ax.transAxes, ha="right", va="bottom",
                fontsize=8, color=MUTED)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    print(f"Saved {out_path}")


def fp_plot(rows, out_path) -> None:
    """Plot measured vs expected false positive rate for the two filters.

    Input: data, output file. Output: None (saves a PNG).
    """
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for name in ("Bloom filter", "Cuckoo filter"):
        if name not in rows:
            continue
        color, marker = STYLE[name]
        xs = [r["n"] for r in rows[name]]
        ax.plot(xs, [r["fp_rate"] * 100 for r in rows[name]], color=color, marker=marker,
                markersize=6, linewidth=2, label=f"{name} (measured)")
        ax.plot(xs, [r["fp_expected"] * 100 for r in rows[name]], color=color,
                linestyle="--", linewidth=2, label=f"{name} (theory)")
    ax.set_xscale("log")
    style_axes(ax, "False positive rate", "False positives (%)")
    ax.set_ylim(bottom=0)
    ax.legend(frameon=False, fontsize=9)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    print(f"Saved {out_path}")


def main() -> None:
    """Parse arguments and draw all plots."""
    parser = argparse.ArgumentParser(description="Plot benchmark results.")
    parser.add_argument("--csv", type=Path, default=ROOT / "results" / "results.csv")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "results")
    args = parser.parse_args()

    rows = load(args.csv)
    out = args.out_dir
    line_plot(rows, "lookup_us", "Lookup time per query", "Time per lookup (µs, log scale)",
              out / "lookup_time.png")
    line_plot(rows, "lookup_us", "Lookup time per query (fast structures)",
              "Time per lookup (µs)", out / "lookup_time_fast.png",
              names=["Binary search", "Hash table", "Bloom filter", "Cuckoo filter"], log_y=False)
    line_plot(rows, "build_s", "Build time", "Time to insert all n logins (s, log scale)",
              out / "build_time.png")
    line_plot(rows, "memory_bytes", "Memory use", "Bytes (log scale)", out / "memory.png",
              note="Linear and binary search store the same strings, so their lines overlap.")
    fp_plot(rows, out / "false_positive_rate.png")


if __name__ == "__main__":
    main()
