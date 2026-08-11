"""The test must find an injected notch and must not invent one in smooth data."""

import numpy as np
import pytest

from src.discontinuity import (neighbor_expected, run_all_widths, run_test,
                               standardized_difference)


def test_neighbor_expectation_is_the_average_of_the_two_neighbours():
    exp = neighbor_expected([10.0, 20.0, 30.0, 40.0])
    assert np.isnan(exp[0]) and np.isnan(exp[-1])
    assert exp[1] == pytest.approx(20.0)   # (10 + 30) / 2
    assert exp[2] == pytest.approx(30.0)   # (20 + 40) / 2


def test_flat_distribution_gives_z_near_zero():
    z = standardized_difference(np.full(20, 500.0))
    assert np.nanmax(np.abs(z)) < 1e-8


def test_smooth_sample_produces_no_significant_notch():
    rng = np.random.default_rng(20250811)
    vals = rng.normal(0.02, 0.05, 200_000)
    result = run_test(vals, width=0.005)
    assert abs(result["z_below"]) < 3
    assert abs(result["z_above"]) < 3


def test_injected_notch_is_detected_in_both_directions():
    """Move mass from the bin just below zero into the bin just above it."""
    rng = np.random.default_rng(7)
    vals = rng.normal(0.0, 0.05, 200_000)
    just_below = (vals >= -0.005) & (vals < 0.0)
    moved = np.flatnonzero(just_below)[: int(just_below.sum() * 0.5)]
    vals[moved] += 0.005

    result = run_test(vals, width=0.005)
    assert result["z_below"] < -5      # deficit below zero
    assert result["z_above"] > 5       # surplus above zero
    assert result["count_below"] < result["expected_below"]
    assert result["count_above"] > result["expected_above"]


def test_all_three_bin_widths_are_reported():
    rng = np.random.default_rng(1)
    vals = rng.normal(0.01, 0.04, 50_000)
    results = run_all_widths(vals)
    assert list(results["bin_width"]) == [0.0025, 0.005, 0.01]
    assert results[["z_below", "z_above", "count_below", "count_above"]].notna().all().all()


def test_n_window_counts_only_observations_inside_the_window():
    vals = np.concatenate([np.full(100, 0.05), np.full(50, 0.5)])
    result = run_test(vals, width=0.005)
    assert result["n_window"] == 100


def test_empty_input_does_not_crash():
    result = run_test([], width=0.005)
    assert result["n_window"] == 0
    assert np.isnan(result["z_below"])
