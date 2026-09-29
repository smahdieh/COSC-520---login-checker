"""Read results/results.csv and make the comparison plots in results/.

Usage:
  python benchmarks/plot_results.py
"""

import argparse
import shutil
import subprocess
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

ORDER = ["Linear search", "Binary search", "Hash table", "Bloom filter", "Cuckoo filter"]
# Okabe-Ito colorblind-safe colors, chosen so no two lines look alike.
# Each structure keeps the same color and marker in every plot.
PALETTE = {
    "Linear search": "#d55e00",  # vermillion
    "Binary search": "#0072b2",  # blue
    "Hash table": "#009e73",     # green
    "Bloom filter": "#e69f00",   # orange
    "Cuckoo filter": "#cc79a7",  # purple
}
MARKERS = dict(zip(ORDER, ["o", "s", "^", "D", "v"]))

# Sized for one column of the ACM acmsmall template (text width ~5.5 in),
# so 9 pt text here is 9 pt in the report with width=\linewidth.
FIG_SIZE = (5.5, 3.4)
FONT_SIZE = 9
ACM_FONT = "Linux Libertine O"
ACM_FONT_FILES = ["LinLibertine_R.otf", "LinLibertine_RI.otf", "LinLibertine_RB.otf"]


def use_acm_font() -> str:
    """Load Linux Libertine (the ACM body font) from the TeX install if present.

    Input: none. Output: the font family name that will be used.
    """
    kpsewhich = shutil.which("kpsewhich")
    if kpsewhich:
        for name in ACM_FONT_FILES:
            path = subprocess.run([kpsewhich, name], capture_output=True, text=True).stdout.strip()
            if path:
                font_manager.fontManager.addfont(path)
    installed = {f.name for f in font_manager.fontManager.ttflist}
    if ACM_FONT in installed:
        return ACM_FONT
    print("Linux Libertine not found; using a similar serif font instead.")
    return "STIXGeneral"


def set_style() -> None:
    """Apply one font family and one size to every text element. Output: None."""
    family = use_acm_font()
    sns.set_theme(style="whitegrid", rc={
        "font.family": "serif",
        "font.serif": [family, "STIXGeneral", "Times New Roman"],
        "mathtext.fontset": "custom",
        "mathtext.rm": family,
        "mathtext.it": f"{family}:italic",
        "mathtext.bf": f"{family}:bold",
        "font.size": FONT_SIZE,
        "axes.labelsize": FONT_SIZE,
        "xtick.labelsize": FONT_SIZE,
        "ytick.labelsize": FONT_SIZE,
        "legend.fontsize": FONT_SIZE,
        "axes.linewidth": 0.8,
        "grid.linewidth": 0.6,
        "pdf.fonttype": 42,
    })


def load(path: Path) -> pd.DataFrame:
    """Read the benchmark CSV. Input: path. Output: DataFrame sorted by n."""
    return pd.read_csv(path).sort_values(["structure", "n"])


def finish(fig, ax, ylabel: str, out_path: Path) -> None:
    """Add axis labels, tidy the axes and save as PNG and PDF.

    Input: figure, axes, y label, output file (.png). Output: None.
    """
    ax.set_xlabel("Number of logins $n$")
    ax.set_ylabel(ylabel)
    ax.set_xscale("log")
    sns.despine(ax=ax)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    fig.savefig(out_path.with_suffix(".pdf"))
    plt.close(fig)
    print(f"Saved {out_path} and .pdf")


def line_plot(df, field, ylabel, out_path, names=None, note=None, log_y=True) -> None:
    """Draw one line per structure against n.

    Input: data, column to plot, y label, output file, optional list
    of structures, optional note, log or linear y axis.
    Output: None (saves a PNG).
    """
    names = names or ORDER
    # Zero values (too fast to measure) can't go on a log axis.
    data = df[df["structure"].isin(names) & (df[field] > 0)]
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    sns.lineplot(data=data, x="n", y=field, hue="structure", style="structure",
                 hue_order=names, style_order=names, palette=PALETTE, markers=MARKERS,
                 dashes=False, markersize=5, linewidth=1.5, ax=ax)
    if log_y:
        ax.set_yscale("log")
    else:
        ax.set_ylim(bottom=0)
    ax.legend(title=None, frameon=False, loc="upper left")
    if note:
        ax.text(0.99, 0.02, note, transform=ax.transAxes, ha="right", va="bottom",
                color="0.35")
    finish(fig, ax, ylabel, out_path)


def fp_plot(df, out_path) -> None:
    """Plot measured vs theoretical false positive rate for the two filters.

    Input: data, output file. Output: None (saves a PNG).
    """
    fig, ax = plt.subplots(figsize=(FIG_SIZE[0], 2.2))
    for name in ("Bloom filter", "Cuckoo filter"):
        rows = df[df["structure"] == name]
        color = PALETTE[name]
        ax.plot(rows["n"], rows["fp_rate"] * 100, color=color, marker=MARKERS[name],
                markersize=5, markeredgecolor="white", linewidth=1.5,
                label=f"{name} (measured)")
        ax.plot(rows["n"], rows["fp_expected"] * 100, color=color, linestyle="--",
                linewidth=1.2, label=f"{name} (theory)")
    ax.set_ylim(bottom=0)
    ax.legend(frameon=False, loc="center right")
    finish(fig, ax, "False positives (%)", out_path)


def pair_plot(df, left, right, out_path) -> None:
    """Draw two panels side by side with one shared legend on top (for the report).

    Input: data, left and right panel settings as (column, y label,
    structures, log y), output file. Output: None (saves PNG and PDF).
    """
    fig, axes = plt.subplots(1, 2, figsize=(FIG_SIZE[0], 2.4))
    for ax, (field, ylabel, names, log_y) in zip(axes, (left, right)):
        for name in names:
            rows = df[(df["structure"] == name) & (df[field] > 0)]
            ax.plot(rows["n"], rows[field], color=PALETTE[name], marker=MARKERS[name],
                    markersize=4, markeredgecolor="white", markeredgewidth=0.6,
                    linewidth=1.3, label=name)
        ax.set_xscale("log")
        if log_y:
            ax.set_yscale("log")
        else:
            ax.set_ylim(bottom=0)
        ax.set_xlabel("Number of logins $n$")
        ax.set_ylabel(ylabel)
        sns.despine(ax=ax)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=len(labels), frameon=False,
               handlelength=1.5, columnspacing=1.0)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig(out_path, dpi=300)
    fig.savefig(out_path.with_suffix(".pdf"))
    plt.close(fig)
    print(f"Saved {out_path} and .pdf")


def main() -> None:
    """Parse arguments and draw all plots."""
    parser = argparse.ArgumentParser(description="Plot benchmark results.")
    parser.add_argument("--csv", type=Path, default=ROOT / "results" / "results.csv")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "results")
    args = parser.parse_args()

    set_style()
    df = load(args.csv)
    out = args.out_dir
    line_plot(df, "lookup_us", "Time per lookup (µs, log scale)", out / "lookup_time.png")
    line_plot(df, "lookup_us", "Time per lookup (µs)", out / "lookup_time_fast.png",
              names=ORDER[1:], log_y=False)
    line_plot(df, "build_s", "Time to insert all $n$ logins (s, log scale)",
              out / "build_time.png")
    line_plot(df, "memory_bytes", "Memory (bytes, log scale)", out / "memory.png",
              note="Linear and binary search store the same strings, so their lines overlap.")
    fp_plot(df, out / "false_positive_rate.png")

    # Two-panel versions used in the report, to save space.
    pair_plot(df, ("lookup_us", "Time per lookup (µs, log)", ORDER, True),
              ("lookup_us", "Time per lookup (µs)", ORDER[1:], False),
              out / "report_lookup.png")
    pair_plot(df, ("build_s", "Build time (s, log)", ORDER, True),
              ("memory_bytes", "Memory (bytes, log)", ORDER, True),
              out / "report_build_memory.png")


if __name__ == "__main__":
    main()
