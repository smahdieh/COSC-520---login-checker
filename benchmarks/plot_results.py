"""Read results/results.csv and make the comparison plots in results/.

Usage:
  python benchmarks/plot_results.py
"""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

ORDER = ["Linear search", "Binary search", "Hash table", "Bloom filter", "Cuckoo filter"]
# Colorblind-safe palette; each structure keeps the same color and marker in every plot.
# Picks blue, brown, green, orange, purple so no two colors look alike.
_COLORS = sns.color_palette("colorblind")
PALETTE = dict(zip(ORDER, [_COLORS[i] for i in (0, 5, 2, 1, 4)]))
MARKERS = dict(zip(ORDER, ["o", "s", "^", "D", "v"]))


def load(path: Path) -> pd.DataFrame:
    """Read the benchmark CSV. Input: path. Output: DataFrame sorted by n."""
    return pd.read_csv(path).sort_values(["structure", "n"])


def finish(fig, ax, title: str, ylabel: str, out_path: Path) -> None:
    """Add labels, tidy the axes and save.

    Input: figure, axes, title, y label, output file. Output: None (saves a PNG).
    """
    ax.set_title(title, loc="left", fontweight="bold")
    ax.set_xlabel("Number of logins $n$")
    ax.set_ylabel(ylabel)
    ax.set_xscale("log")
    sns.despine(ax=ax)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"Saved {out_path}")


def line_plot(df, field, title, ylabel, out_path, names=None, note=None, log_y=True) -> None:
    """Draw one line per structure against n.

    Input: data, column to plot, title, y label, output file, optional list
    of structures, optional note, log or linear y axis.
    Output: None (saves a PNG).
    """
    names = names or ORDER
    # Zero values (too fast to measure) can't go on a log axis.
    data = df[df["structure"].isin(names) & (df[field] > 0)]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    sns.lineplot(data=data, x="n", y=field, hue="structure", style="structure",
                 hue_order=names, style_order=names, palette=PALETTE, markers=MARKERS,
                 dashes=False, markersize=7, linewidth=2, ax=ax)
    if log_y:
        ax.set_yscale("log")
    else:
        ax.set_ylim(bottom=0)
    ax.legend(title=None, frameon=False, loc="upper left")
    if note:
        ax.text(0.99, 0.02, note, transform=ax.transAxes, ha="right", va="bottom",
                fontsize=9, color="0.35")
    finish(fig, ax, title, ylabel, out_path)


def fp_plot(df, out_path) -> None:
    """Plot measured vs theoretical false positive rate for the two filters.

    Input: data, output file. Output: None (saves a PNG).
    """
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for name in ("Bloom filter", "Cuckoo filter"):
        rows = df[df["structure"] == name]
        color = PALETTE[name]
        ax.plot(rows["n"], rows["fp_rate"] * 100, color=color, marker=MARKERS[name],
                markersize=7, linewidth=2, label=f"{name} (measured)")
        ax.plot(rows["n"], rows["fp_expected"] * 100, color=color, linestyle="--",
                linewidth=1.5, label=f"{name} (theory)")
    ax.set_ylim(bottom=0)
    ax.legend(frameon=False, loc="center right")
    finish(fig, ax, "False positive rate", "False positives (%)", out_path)


def main() -> None:
    """Parse arguments and draw all plots."""
    parser = argparse.ArgumentParser(description="Plot benchmark results.")
    parser.add_argument("--csv", type=Path, default=ROOT / "results" / "results.csv")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "results")
    args = parser.parse_args()

    sns.set_theme(context="paper", style="whitegrid", font_scale=1.3)
    df = load(args.csv)
    out = args.out_dir
    line_plot(df, "lookup_us", "Lookup time per query", "Time per lookup (µs, log scale)",
              out / "lookup_time.png")
    line_plot(df, "lookup_us", "Lookup time per query (fast structures)",
              "Time per lookup (µs)", out / "lookup_time_fast.png",
              names=ORDER[1:], log_y=False)
    line_plot(df, "build_s", "Build time", "Time to insert all $n$ logins (s, log scale)",
              out / "build_time.png")
    line_plot(df, "memory_bytes", "Memory use", "Bytes (log scale)", out / "memory.png",
              note="Linear and binary search store the same strings, so their lines overlap.")
    fp_plot(df, out / "false_positive_rate.png")


if __name__ == "__main__":
    main()
