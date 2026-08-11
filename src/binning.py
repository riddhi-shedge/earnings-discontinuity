"""Histogram binning with zero pinned to a bin boundary.

Spec section 5.2 / pitfall list: if zero falls *inside* a bin, the deficit just below
zero and the surplus just above are averaged together inside the same bar and the
discontinuity is blurred away. Every bin edge here is an exact integer multiple of the
bin width, so ``0.0`` is always an edge -- enforced by construction and by
``tests/test_binning.py``, not by convention.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

WINDOW = 0.10  # spec section 3, filter 5: analysis window is |scaled earnings| <= 0.10
BIN_WIDTHS = (0.0025, 0.005, 0.01)  # spec section 5.2: every test runs at all three


def bin_edges(width: float, lo: float = -WINDOW, hi: float = WINDOW) -> np.ndarray:
    """Edges spanning [lo, hi], every edge an integer multiple of ``width``.

    The range is widened outward to the next multiple if ``lo``/``hi`` are not
    themselves multiples, so the zero-on-an-edge guarantee never depends on the
    caller picking a convenient window.
    """
    if width <= 0:
        raise ValueError("width must be positive")
    k_lo = int(np.floor(lo / width + 1e-9))
    k_hi = int(np.ceil(hi / width - 1e-9))
    return np.arange(k_lo, k_hi + 1, dtype=float) * width


def zero_index(edges: np.ndarray) -> int:
    """Index of the edge equal to zero. Raises if zero is not an edge."""
    hits = np.flatnonzero(np.isclose(edges, 0.0, atol=1e-12))
    if len(hits) != 1:
        raise AssertionError(f"zero is not a unique bin edge in {edges!r}")
    return int(hits[0])


def histogram(values: pd.Series | np.ndarray, width: float,
              lo: float = -WINDOW, hi: float = WINDOW) -> pd.DataFrame:
    """Counts per bin over the window.

    Bins are half-open ``[left, right)``, so an observation of exactly zero falls in
    the first bin *above* zero. That is a deliberate, stated convention: exact zeros
    are reported profits (or breakeven), not losses.
    """
    vals = np.asarray(pd.Series(values).dropna(), dtype=float)
    edges = bin_edges(width, lo, hi)
    zero_index(edges)  # fail loudly if the invariant is ever broken
    inside = vals[(vals >= edges[0]) & (vals < edges[-1])]
    counts, _ = np.histogram(inside, bins=edges)
    left = edges[:-1]
    right = edges[1:]
    return pd.DataFrame({
        "bin_index": np.arange(len(counts)),
        "left": left,
        "right": right,
        "mid": (left + right) / 2,
        "count": counts.astype(int),
        # the bin whose left edge is exactly zero is "the bin just above zero"
        "is_just_below_zero": np.isclose(right, 0.0, atol=1e-12),
        "is_just_above_zero": np.isclose(left, 0.0, atol=1e-12),
    })
