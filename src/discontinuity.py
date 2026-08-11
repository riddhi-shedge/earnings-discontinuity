"""The section 5.3 discontinuity test.

For each bin the count is predicted from its immediate neighbours::

    expected_i = (count_{i-1} + count_{i+1}) / 2

Under a smoothness null the difference is approximately normal. The standard
deviation follows the binomial argument used in this literature: with ``N``
observations and bin probabilities ``p``, the observed count in bin ``i`` is
Binomial(N, p_i) and the neighbour average has variance
``(1/4) * N * (p_{i-1} + p_{i+1}) * (1 - p_{i-1} - p_{i+1})``, giving

    sd_i = sqrt( N p_i (1 - p_i) + (1/4) N (p_{i-1}+p_{i+1}) (1 - p_{i-1} - p_{i+1}) )

Both the bin immediately below zero and the bin immediately above are always
reported. The prediction is a deficit below *and* a surplus above; finding only one
of the two is weaker evidence and is stated as such rather than glossed over.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from .binning import BIN_WIDTHS, WINDOW, histogram


def neighbor_expected(counts: np.ndarray) -> np.ndarray:
    """(count_{i-1} + count_{i+1}) / 2, NaN at the two end bins."""
    counts = np.asarray(counts, dtype=float)
    exp = np.full(counts.shape, np.nan)
    exp[1:-1] = (counts[:-2] + counts[2:]) / 2.0
    return exp


def standardized_difference(counts: np.ndarray) -> np.ndarray:
    """z = (observed - neighbour-predicted) / sd, NaN at the end bins."""
    counts = np.asarray(counts, dtype=float)
    n_total = counts.sum()
    if n_total == 0:
        return np.full(counts.shape, np.nan)

    p = counts / n_total
    exp = neighbor_expected(counts)
    z = np.full(counts.shape, np.nan)

    p_prev = np.full(counts.shape, np.nan)
    p_next = np.full(counts.shape, np.nan)
    p_prev[1:-1] = p[:-2]
    p_next[1:-1] = p[2:]

    p_pair = p_prev + p_next
    var = n_total * p * (1 - p) + 0.25 * n_total * p_pair * (1 - p_pair)
    sd = np.sqrt(var)
    ok = np.isfinite(exp) & np.isfinite(sd) & (sd > 0)
    z[ok] = (counts[ok] - exp[ok]) / sd[ok]
    return z


def chi_square_neighbor(counts: np.ndarray) -> dict:
    """Spec section 5.3 chi-square: observed vs neighbour-predicted across the window.

    Caveat carried into the writeup: the expectation is built from the same data, so
    the interior-bin terms are not independent and the degrees of freedom are
    approximate. Treated as a descriptive smoothness statistic, with
    ``chi_square_smooth_fit`` as the better-behaved complement.
    """
    counts = np.asarray(counts, dtype=float)
    exp = neighbor_expected(counts)
    ok = np.isfinite(exp) & (exp > 0)
    chi2 = float(np.sum((counts[ok] - exp[ok]) ** 2 / exp[ok]))
    df = int(ok.sum() - 1)
    return {"chi2": chi2, "df": df, "p_value": float(stats.chi2.sf(chi2, df)) if df > 0 else np.nan,
            "bins_used": int(ok.sum()), "note": "approximate df; expectation is data-derived"}


def chi_square_smooth_fit(table: pd.DataFrame, degree: int = 4) -> dict:
    """Complementary GOF test whose expectation ignores the bins under test.

    A degree-``d`` polynomial is fitted to the bin counts across the window with the
    two zero-adjacent bins held out, then observed counts in those two held-out bins
    are compared to the fit. Because the expectation never sees the bins being tested,
    the two-degree-of-freedom joint statistic is interpretable in the usual way.
    """
    counts = table["count"].to_numpy(dtype=float)
    mids = table["mid"].to_numpy(dtype=float)
    held_out = (table["is_just_below_zero"] | table["is_just_above_zero"]).to_numpy()
    fit_mask = ~held_out & (counts > 0)
    if fit_mask.sum() <= degree + 1:
        return {"chi2": np.nan, "df": 0, "p_value": np.nan, "degree": degree}

    weights = 1.0 / np.sqrt(np.maximum(counts[fit_mask], 1.0))
    coef = np.polyfit(mids[fit_mask], counts[fit_mask], degree, w=weights)
    fitted = np.polyval(coef, mids)
    fitted = np.maximum(fitted, 1e-9)

    chi2 = float(np.sum((counts[held_out] - fitted[held_out]) ** 2 / fitted[held_out]))
    df = int(held_out.sum())
    return {
        "chi2": chi2, "df": df, "p_value": float(stats.chi2.sf(chi2, df)),
        "degree": degree,
        "expected_below": float(fitted[table["is_just_below_zero"].to_numpy()][0]),
        "expected_above": float(fitted[table["is_just_above_zero"].to_numpy()][0]),
    }


def discontinuity_table(values, width: float, window: float = WINDOW) -> pd.DataFrame:
    """Per-bin counts, neighbour expectations, z statistics and two-sided p-values."""
    table = histogram(values, width, -window, window)
    counts = table["count"].to_numpy(dtype=float)
    table["expected"] = neighbor_expected(counts)
    table["z"] = standardized_difference(counts)
    table["p_value"] = 2 * stats.norm.sf(np.abs(table["z"]))
    return table


def run_test(values, width: float, window: float = WINDOW, label: str = "") -> dict:
    """One complete test at one bin width. Always reports below-zero *and* above-zero."""
    table = discontinuity_table(values, width, window)
    below = table[table["is_just_below_zero"]].iloc[0]
    above = table[table["is_just_above_zero"]].iloc[0]
    n_window = int(table["count"].sum())

    return {
        "label": label,
        "bin_width": width,
        "n_window": n_window,
        "n_bins": len(table),
        "count_below": int(below["count"]),
        "expected_below": float(below["expected"]),
        "z_below": float(below["z"]),
        "p_below": float(below["p_value"]),
        "count_above": int(above["count"]),
        "expected_above": float(above["expected"]),
        "z_above": float(above["z"]),
        "p_above": float(above["p_value"]),
        "chi2_neighbor": chi_square_neighbor(table["count"].to_numpy())["chi2"],
        "chi2_neighbor_p": chi_square_neighbor(table["count"].to_numpy())["p_value"],
        "chi2_smooth_p": chi_square_smooth_fit(table)["p_value"],
        "_table": table,
    }


def run_all_widths(values, widths=BIN_WIDTHS, window: float = WINDOW,
                   label: str = "") -> pd.DataFrame:
    """The same test at every bin width. Reporting one width alone is not a result."""
    rows = [run_test(values, w, window, label) for w in widths]
    return pd.DataFrame([{k: v for k, v in r.items() if k != "_table"} for r in rows])


def summarize(results: pd.DataFrame) -> str:
    """One-line-per-width plain-language summary, used in notebooks and the writeup."""
    lines = []
    for _, r in results.iterrows():
        direction_below = "deficit" if r["z_below"] < 0 else "surplus"
        direction_above = "surplus" if r["z_above"] > 0 else "deficit"
        lines.append(
            f"width={r['bin_width']:.4f}  N={int(r['n_window']):,}  "
            f"below zero: {int(r['count_below']):,} vs {r['expected_below']:.1f} expected "
            f"({direction_below}, z={r['z_below']:+.2f}, p={r['p_below']:.3g})  |  "
            f"above zero: {int(r['count_above']):,} vs {r['expected_above']:.1f} expected "
            f"({direction_above}, z={r['z_above']:+.2f}, p={r['p_above']:.3g})"
        )
    return "\n".join(lines)
