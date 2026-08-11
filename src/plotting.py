"""Figures. The headline histogram is the deliverable the whole project is judged on.

Design decisions, so they are not re-litigated per chart:
  * One series, so no legend box -- the title names what is plotted. The two bins
    adjacent to zero are emphasised in a second hue *and* directly labelled, so their
    identity never rests on colour alone.
  * Palette slots 1 and 2 of the reference categorical palette (blue / orange).
    Validated: worst-pair CVD deltaE 24.7, normal-vision 33.6, both >= 3:1 on the
    surface. Light-mode only on purpose -- these are print figures for a PDF writeup.
  * Zero is drawn as a boundary line between bars, never through the middle of one,
    which is the whole point of the binning module.
  * Neighbour-predicted counts for the two focal bins are drawn as short rules, so
    the reader can see the test rather than take the z-statistic on faith.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .discontinuity import discontinuity_table

SURFACE = "#fcfcfb"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
TEXT_MUTED = "#84837c"
SERIES_1 = "#2a78d6"   # bars
SERIES_2 = "#eb6834"   # the two bins adjacent to zero
GRID = "#e3e2dd"

FIG_DIR = Path(__file__).resolve().parents[1] / "figures"


def use_house_style() -> None:
    mpl.rcParams.update({
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "axes.edgecolor": GRID,
        "axes.labelcolor": TEXT_SECONDARY,
        "axes.titlecolor": TEXT_PRIMARY,
        "text.color": TEXT_PRIMARY,
        "xtick.color": TEXT_SECONDARY,
        "ytick.color": TEXT_SECONDARY,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "axes.labelsize": 10.5,
        "axes.titlesize": 13,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "font.family": "DejaVu Sans",
        "figure.dpi": 110,
    })


def _draw_hist(ax, table: pd.DataFrame, width: float, *, show_expected: bool = True,
               annotate: bool = True) -> None:
    focal = (table["is_just_below_zero"] | table["is_just_above_zero"]).to_numpy()
    colors = np.where(focal, SERIES_2, SERIES_1)

    ax.bar(table["left"], table["count"], width=width, align="edge",
           color=colors, edgecolor=SURFACE, linewidth=0.9, zorder=3)

    ax.axvline(0.0, color=TEXT_PRIMARY, linewidth=1.4, zorder=5)
    ax.set_axisbelow(True)
    ax.grid(axis="y", zorder=0)
    ax.set_xlim(table["left"].min(), table["right"].max())

    if show_expected:
        for _, row in table[focal].iterrows():
            if np.isfinite(row["expected"]):
                ax.hlines(row["expected"], row["left"], row["right"],
                          color=TEXT_PRIMARY, linewidth=1.6, linestyle=(0, (3, 2)), zorder=6)

    if annotate:
        below = table[table["is_just_below_zero"]].iloc[0]
        above = table[table["is_just_above_zero"]].iloc[0]
        top = table["count"].max()
        left_edge = table["left"].min()
        right_edge = table["right"].max()
        span = right_edge - left_edge

        # All annotation lives in reserved headroom above the tallest bar, so leader
        # lines never cross a bar and text never sits on top of the data.
        ax.set_ylim(0, top * 1.46)
        text_y = top * 1.30

        ax.annotate(
            f"bin just below zero\n{int(below['count']):,} observed"
            f"\nvs {below['expected']:,.0f} predicted",
            xy=(below["mid"], below["count"]), xytext=(left_edge + span * 0.02, text_y),
            fontsize=8.5, color=TEXT_SECONDARY, ha="left", va="top",
            arrowprops=dict(arrowstyle="-", color=TEXT_MUTED, linewidth=0.9,
                            shrinkB=3, connectionstyle="arc3,rad=0.18"))
        ax.annotate(
            f"bin just above zero\n{int(above['count']):,} observed"
            f"\nvs {above['expected']:,.0f} predicted",
            xy=(above["mid"], above["count"]), xytext=(right_edge - span * 0.02, text_y),
            fontsize=8.5, color=TEXT_SECONDARY, ha="right", va="top",
            arrowprops=dict(arrowstyle="-", color=TEXT_MUTED, linewidth=0.9,
                            shrinkB=3, connectionstyle="arc3,rad=-0.18"))

        label_y = top * 1.38
        ax.text(0.0, label_y, "zero", fontsize=9, color=TEXT_PRIMARY,
                ha="center", va="bottom", fontweight="bold")
        ax.text(-span * 0.085, label_y, "◀ losses", fontsize=8.5, color=TEXT_MUTED,
                ha="center", va="bottom")
        ax.text(span * 0.085, label_y, "profits ▶", fontsize=8.5, color=TEXT_MUTED,
                ha="center", va="bottom")


def headline_histogram(values, width: float, *, source: str, n_firms: int | None = None,
                       measure: str = "Net income / beginning-of-year total assets",
                       title: str = "Distribution of scaled net income around zero",
                       period: str = "", out: Path | None = None,
                       dashed_note: bool = True):
    """The publication figure: labelled axes, zero on a boundary, bin width and N stated."""
    use_house_style()
    table = discontinuity_table(values, width)
    n = int(table["count"].sum())

    fig, ax = plt.subplots(figsize=(9.2, 5.6))
    _draw_hist(ax, table, width)

    ax.set_xlabel(measure)
    ax.set_ylabel("Number of firm-years")
    ax.set_title(title, pad=34, loc="left", fontweight="bold")

    parts = [f"N = {n:,} firm-years"]
    if n_firms:
        parts.append(f"{n_firms:,} distinct firms")
    if period:
        parts.append(period)
    caption = (f"Bin width {width:g} of beginning-of-year total assets; zero falls on a bin "
               f"boundary, not inside one. {'; '.join(parts)}. Source: {source}. "
               f"Window restricted to |scaled earnings| ≤ 0.10.")
    if dashed_note:
        caption += ("\nDashed rules mark each focal bin's count predicted from its two "
                    "neighbours, (countᵢ₋₁ + countᵢ₊₁) / 2.")
    fig.text(0.055, -0.015, caption, fontsize=8.4, color=TEXT_MUTED, ha="left", va="top", wrap=True)

    fig.tight_layout(rect=(0, 0.06, 1, 1))
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out, dpi=300, bbox_inches="tight")
        fig.savefig(out.with_suffix(".svg"), bbox_inches="tight")
    return fig, table


def bin_width_panel(values, widths, *, source: str, out: Path | None = None,
                    measure: str = "Net income / beginning-of-year total assets"):
    """Same data, three bin widths, side by side. Guards against the one-width result."""
    use_house_style()
    fig, axes = plt.subplots(1, len(widths), figsize=(4.6 * len(widths), 4.4), sharey=False)
    for ax, width in zip(np.atleast_1d(axes), widths):
        table = discontinuity_table(values, width)
        _draw_hist(ax, table, width, annotate=False)
        below = table[table["is_just_below_zero"]].iloc[0]
        above = table[table["is_just_above_zero"]].iloc[0]
        ax.set_title(f"bin width {width:g}\nz below = {below['z']:+.2f}   "
                     f"z above = {above['z']:+.2f}", fontsize=10.5, loc="left")
        ax.set_xlabel(measure, fontsize=9)
    np.atleast_1d(axes)[0].set_ylabel("Number of firm-years")
    fig.suptitle("The same test at three bin widths", x=0.02, ha="left",
                 fontweight="bold", fontsize=13)
    fig.text(0.02, -0.02, f"Source: {source}. Orange bars are the bins adjacent to zero; "
                          f"dashed rules are the neighbour-predicted counts.",
             fontsize=8.4, color=TEXT_MUTED, ha="left", va="top")
    fig.tight_layout(rect=(0, 0.04, 1, 0.93))
    if out:
        fig.savefig(out, dpi=300, bbox_inches="tight")
    return fig


def placebo_panel(ni_values, cfo_values, width: float, *, source: str, out: Path | None = None):
    """Net income beside cash flow from operations, scaled identically (spec 6.4)."""
    use_house_style()
    fig, axes = plt.subplots(1, 2, figsize=(11.6, 4.8))
    specs = [
        (ni_values, "Net income / lagged assets", "Net income (the test)"),
        (cfo_values, "Cash flow from operations / lagged assets", "Cash flow from operations (placebo)"),
    ]
    for ax, (vals, xlabel, title) in zip(axes, specs):
        table = discontinuity_table(vals, width)
        _draw_hist(ax, table, width, annotate=False)
        below = table[table["is_just_below_zero"]].iloc[0]
        above = table[table["is_just_above_zero"]].iloc[0]
        ax.set_title(f"{title}\nN = {int(table['count'].sum()):,}   "
                     f"z below = {below['z']:+.2f}   z above = {above['z']:+.2f}",
                     fontsize=10.5, loc="left")
        ax.set_xlabel(xlabel, fontsize=9.5)
    axes[0].set_ylabel("Number of firm-years")
    fig.suptitle("Cash-flow placebo: is the notch specific to accrual earnings?",
                 x=0.02, ha="left", fontweight="bold", fontsize=13)
    fig.text(0.02, -0.02, f"Bin width {width:g}. Both measures scaled by the same "
                          f"beginning-of-year total assets. Source: {source}.",
             fontsize=8.4, color=TEXT_MUTED, ha="left", va="top")
    fig.tight_layout(rect=(0, 0.04, 1, 0.92))
    if out:
        fig.savefig(out, dpi=300, bbox_inches="tight")
    return fig


def z_comparison(results: pd.DataFrame, *, label_col: str, title: str,
                 out: Path | None = None, subtitle: str = ""):
    """Dot plot of z below / z above across specifications, with the +-1.96 band shown."""
    use_house_style()
    labels = results[label_col].astype(str).tolist()
    y = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(9.0, 0.52 * len(labels) + 2.6))

    ax.axvspan(-1.96, 1.96, color=GRID, alpha=0.6, zorder=0)
    ax.axvline(0, color=TEXT_MUTED, linewidth=1.0, zorder=1)
    ax.scatter(results["z_below"], y - 0.14, s=64, color=SERIES_1, zorder=3,
               label="bin just below zero")
    ax.scatter(results["z_above"], y + 0.14, s=64, color=SERIES_2, marker="D", zorder=3,
               label="bin just above zero")

    ax.set_yticks(y, labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("standardized difference (z)")
    ax.grid(axis="x")
    ax.set_axisbelow(True)
    ax.set_title(title, loc="left", fontweight="bold", pad=26)
    ax.legend(frameon=False, fontsize=9, loc="upper left", bbox_to_anchor=(0, 1.10), ncols=2)
    note = "Shaded band is |z| < 1.96. " + subtitle
    fig.text(0.02, -0.02, note, fontsize=8.4, color=TEXT_MUTED, ha="left", va="top")
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    if out:
        fig.savefig(out, dpi=300, bbox_inches="tight")
    return fig
