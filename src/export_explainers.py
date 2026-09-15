"""Explainer graphics for the presentation (not analysis figures -- teaching aids).

    python -m src.export_explainers

  figures/explain_notch.png        what a "notch" at zero would look like, vs smooth
  figures/explain_funnel.png       how 57,407 filings become 16,018 tested firm-years
  figures/explain_neighbor_test.png how one bin is judged against its two neighbours
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from .plotting import (GRID, SERIES_1, SERIES_2, SURFACE, TEXT_MUTED,  # noqa: E402
                       TEXT_PRIMARY, TEXT_SECONDARY, use_house_style)

ROOT = Path(__file__).resolve().parents[1]
FIGS = ROOT / "figures"


def notch_explainer(out: Path) -> None:
    use_house_style()
    width = 0.005
    left = np.arange(-0.10, 0.10 - 1e-9, width)          # left edges: zero is an edge, never inside a bin
    mid = left + width / 2
    base = 600 * np.exp(-((mid - 0.03) ** 2) / (2 * 0.045 ** 2))
    notched = base.copy()
    i_below = int(np.argmin(np.abs(left - (-width))))     # bin [-0.005, 0)
    i_above = int(np.argmin(np.abs(left - 0.0)))          # bin [0, 0.005)
    moved = 0.35 * notched[i_below]
    notched[i_below] -= moved
    notched[i_above] += moved

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), sharey=True)
    for ax, y, title, sub in (
        (axes[0], base, "If nobody touched the numbers",
         "the curve passes smoothly through zero"),
        (axes[1], notched, "If some firms nudge a small loss into a small profit",
         "a dip just left of zero, a bump just right of it"),
    ):
        colors = [SERIES_1] * len(left)
        colors[i_below] = SERIES_2
        colors[i_above] = SERIES_2
        ax.bar(left, y, width=width, align="edge", color=colors, edgecolor=SURFACE, linewidth=0.9, zorder=3)
        ax.axvline(0, color=TEXT_PRIMARY, linewidth=1.6, zorder=5)
        ax.set_title(title, loc="left", fontweight="bold", fontsize=13, pad=22)
        ax.text(0.0, 1.02, sub, transform=ax.transAxes, ha="left", va="bottom",
                fontsize=10.5, color=TEXT_SECONDARY)
        ax.set_xlabel("scaled net income   (losses  ←  zero  →  profits)")
        ax.set_xticks([-0.10, -0.05, 0, 0.05, 0.10])
        ax.set_ylim(0, 800)
        ax.grid(axis="y")
        ax.set_axisbelow(True)
        ax.text(0, 785, "zero", ha="center", va="top", fontsize=10, fontweight="bold")
    axes[0].set_ylabel("number of companies")
    axes[1].annotate("too few here", xy=(left[i_below] + width / 2, notched[i_below]),
                     xytext=(-0.085, 560), fontsize=11.5, color=SERIES_2, fontweight="bold",
                     arrowprops=dict(arrowstyle="->", color=SERIES_2, lw=1.4))
    axes[1].annotate("too many here", xy=(left[i_above] + width / 2, notched[i_above]),
                     xytext=(0.035, 730), fontsize=11.5, color=SERIES_2, fontweight="bold",
                     arrowprops=dict(arrowstyle="->", color=SERIES_2, lw=1.4))
    fig.text(0.01, -0.02, "Illustration only, not data. Orange = the two bins that touch zero. "
             "Zero sits on a bin edge, never inside a bin.", fontsize=9, color=TEXT_MUTED)
    fig.tight_layout()
    fig.savefig(out, dpi=220, bbox_inches="tight")
    plt.close(fig)


def funnel(out: Path) -> None:
    use_house_style()
    log = pd.read_csv(ROOT / "data" / "drop_log.csv")
    steps = [
        ("All 10-K filings pulled\n(37 quarterly SEC archives)", 57407),
        ("Fiscal years 2016–2025, with an industry code", 56716),
        ("Not a bank, insurer or utility", 40722),
        ("Net income and prior-year assets both present", 39255),
        ("At least $10m of assets to start the year", 31240),
        ("Scaled income within ±10% (the test window)", 16018),
    ]
    labels = [s[0] for s in steps][::-1]
    vals = [s[1] for s in steps][::-1]
    fig, ax = plt.subplots(figsize=(11.5, 5.2))
    colors = [SERIES_1] * len(vals)
    colors[0] = SERIES_2
    bars = ax.barh(labels, vals, color=colors, height=0.62, zorder=3)
    for b, v in zip(bars, vals):
        ax.text(v + 600, b.get_y() + b.get_height() / 2, f"{v:,}", va="center", fontsize=11,
                color=TEXT_PRIMARY, fontweight="bold")
    ax.set_xlim(0, 66000)
    ax.set_xlabel("firm-years")
    ax.grid(axis="x")
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", labelsize=11)
    ax.set_title("How 57,407 filings become 16,018 tested firm-years", loc="left",
                 fontweight="bold", pad=14)
    fig.text(0.01, -0.02, "Every step is counted in data/drop_log.csv. The largest single cut is "
             "financial firms (14,590), whose balance sheets don't compare.",
             fontsize=9, color=TEXT_MUTED)
    fig.tight_layout()
    fig.savefig(out, dpi=220, bbox_inches="tight")
    plt.close(fig)


def neighbor_test(out: Path) -> None:
    use_house_style()
    table = pd.read_csv(ROOT / "data" / "headline_bin_table.csv")
    mid = table.index[table["is_just_below_zero"]][0]
    sub = table.iloc[mid - 1: mid + 2]
    counts = sub["count"].to_numpy()
    exp = (counts[0] + counts[2]) / 2
    gap = counts[1] - exp

    fig, ax = plt.subplots(figsize=(10.4, 5.0))
    x = np.arange(3)
    ax.bar(x, counts, color=[SERIES_1, SERIES_2, SERIES_1], width=0.6, zorder=3)
    ax.hlines(exp, 0.7, 1.3, color=TEXT_PRIMARY, linestyle=(0, (4, 2)), linewidth=2.2, zorder=6)
    for i, c in enumerate(counts):
        ax.text(i, c - 14, f"{int(c):,}", ha="center", va="top", fontsize=12, fontweight="bold", color="white")
    for i, lbl in enumerate(["the bin before\n(−0.010 to −0.005)", "the bin we are testing\n(−0.005 to 0)",
                             "the bin after\n(0 to +0.005)"]):
        ax.text(i, -60, lbl, ha="center", va="top", fontsize=10, color=TEXT_SECONDARY)

    ax.text(2.42, exp, f"expected if the curve were smooth\n= average of the neighbours\n"
            f"= ({int(counts[0])} + {int(counts[2])}) / 2 = {exp:,.1f}",
            ha="left", va="center", fontsize=10.5, color=TEXT_PRIMARY)
    ax.text(-0.3, 720, f"observed = {int(counts[1]):,}     expected = {exp:,.1f}     gap = {gap:+.1f}\n"
            "z = gap ÷ its standard error  →  here z = −0.79, which is not unusual",
            ha="left", va="top", fontsize=11, color=SERIES_2, fontweight="bold")
    ax.set_xlim(-0.5, 4.3)
    ax.set_ylim(0, 760)
    ax.set_xticks([])
    ax.set_ylabel("number of firm-years")
    ax.grid(axis="y")
    ax.set_axisbelow(True)
    ax.set_title("One bin, judged against its two neighbours", loc="left", fontweight="bold", pad=12)
    fig.text(0.01, -0.06, "Real numbers from the headline histogram (bin width 0.005): the bin just below "
             "zero and its neighbours.", fontsize=9, color=TEXT_MUTED)
    fig.tight_layout()
    fig.savefig(out, dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    notch_explainer(FIGS / "explain_notch.png")
    funnel(FIGS / "explain_funnel.png")
    neighbor_test(FIGS / "explain_neighbor_test.png")
    print("wrote explain_notch.png, explain_funnel.png, explain_neighbor_test.png")


if __name__ == "__main__":
    main()
