"""Zero must sit on a bin boundary. This file is the enforcement."""

import numpy as np
import pytest

from src.binning import BIN_WIDTHS, bin_edges, histogram, zero_index


@pytest.mark.parametrize("width", list(BIN_WIDTHS) + [0.003, 0.007, 0.02, 0.0001])
def test_zero_is_always_a_bin_edge(width):
    edges = bin_edges(width)
    assert np.isclose(edges, 0.0, atol=1e-12).sum() == 1
    zero_index(edges)  # raises if not


@pytest.mark.parametrize("width", BIN_WIDTHS)
def test_edges_are_integer_multiples_of_width(width):
    edges = bin_edges(width)
    assert np.allclose(edges / width, np.round(edges / width))


def test_window_widened_when_not_a_multiple_of_width():
    # 0.10 / 0.003 is not an integer, so the range must widen outward, not clip.
    edges = bin_edges(0.003, -0.10, 0.10)
    assert edges[0] <= -0.10 and edges[-1] >= 0.10
    zero_index(edges)


def test_exact_zero_lands_in_the_bin_above_zero():
    """Bins are [left, right): an exactly-zero report is a breakeven/profit, not a loss."""
    table = histogram([0.0], width=0.005)
    assert table.loc[table["is_just_above_zero"], "count"].iloc[0] == 1
    assert table.loc[table["is_just_below_zero"], "count"].iloc[0] == 0


def test_tiny_negative_lands_in_the_bin_below_zero():
    table = histogram([-1e-9], width=0.005)
    assert table.loc[table["is_just_below_zero"], "count"].iloc[0] == 1
    assert table.loc[table["is_just_above_zero"], "count"].iloc[0] == 0


def test_exactly_one_bin_flagged_on_each_side():
    for width in BIN_WIDTHS:
        table = histogram([0.01, -0.01], width=width)
        assert table["is_just_below_zero"].sum() == 1
        assert table["is_just_above_zero"].sum() == 1
        below = table[table["is_just_below_zero"]].iloc[0]
        above = table[table["is_just_above_zero"]].iloc[0]
        assert np.isclose(below["right"], 0.0)
        assert np.isclose(above["left"], 0.0)
        assert above["bin_index"] == below["bin_index"] + 1


def test_values_outside_the_window_are_excluded_not_clipped():
    table = histogram([0.5, -0.5, 0.02], width=0.005)
    assert table["count"].sum() == 1


def test_counts_match_input_inside_window():
    rng = np.random.default_rng(0)
    vals = rng.normal(0, 0.03, 5000)
    table = histogram(vals, width=0.005)
    assert table["count"].sum() == int(((vals >= -0.10) & (vals < 0.10)).sum())


def test_nan_values_are_dropped():
    table = histogram([0.01, np.nan, -0.01], width=0.005)
    assert table["count"].sum() == 2


def test_invalid_width_raises():
    with pytest.raises(ValueError):
        bin_edges(0.0)
    with pytest.raises(ValueError):
        bin_edges(-0.005)
