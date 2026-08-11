"""The denominator must be beginning-of-year assets, and no firm may leave silently."""

import numpy as np
import pandas as pd
import pytest

from src.panel import add_scaled_variables, apply_filters, build_yf_panel, restrict_window


def _yf_frame(rows):
    return pd.DataFrame(rows, columns=["ticker", "period_end", "net_income", "total_assets",
                                       "book_equity", "revenue", "cfo", "market_equity"])


def test_lag_uses_prior_year_assets_not_current_year():
    raw = _yf_frame([
        ("AAA", "2021-12-31", 10.0, 100.0, 50.0, 200.0, 12.0, 500.0),
        ("AAA", "2022-12-31", 20.0, 400.0, 60.0, 250.0, 22.0, 600.0),
    ])
    panel = add_scaled_variables(build_yf_panel(raw))
    row = panel[panel["fiscal_year"] == 2022].iloc[0]
    assert row["assets_lag"] == 100.0                    # beginning of year, not 400
    assert row["roa"] == pytest.approx(20.0 / 100.0)     # 0.20, not 20/400 = 0.05


def test_first_observation_of_a_firm_has_no_lag():
    raw = _yf_frame([("AAA", "2021-12-31", 10.0, 100.0, 50.0, 200.0, 12.0, 500.0)])
    panel = build_yf_panel(raw)
    assert panel["assets_lag"].isna().all()


def test_gap_year_does_not_become_a_lag():
    """A missing year must not silently be treated as the prior year."""
    raw = _yf_frame([
        ("AAA", "2019-12-31", 10.0, 100.0, 50.0, 200.0, 12.0, 500.0),
        ("AAA", "2023-12-31", 20.0, 400.0, 60.0, 250.0, 22.0, 600.0),
    ])
    panel = build_yf_panel(raw)
    assert panel["assets_lag"].isna().all()


def test_lag_is_per_firm_never_across_firms():
    raw = _yf_frame([
        ("AAA", "2021-12-31", 10.0, 100.0, 50.0, 200.0, 12.0, 500.0),
        ("BBB", "2022-12-31", 20.0, 400.0, 60.0, 250.0, 22.0, 600.0),
    ])
    panel = build_yf_panel(raw)
    assert panel["assets_lag"].isna().all()


def _sec_frame(rows):
    return pd.DataFrame(rows, columns=["firm_id", "name", "sic", "fiscal_year", "period_end",
                                       "net_income", "revenue", "cfo", "assets", "assets_lag",
                                       "equity_lag", "market_equity"])


BASE = ("X", "X Corp", 3500.0, 2022, pd.Timestamp("2022-12-31"),
        5.0, 100.0, 8.0, 60e6, 50e6, 20e6, np.nan)


def _row(**kw):
    row = dict(zip(_sec_frame([]).columns, BASE))
    row.update(kw)
    return row


def test_filters_drop_financials_utilities_and_bad_denominators_with_counts():
    frame = _sec_frame([])
    frame = pd.DataFrame([
        _row(firm_id="ok", sic=3500.0),
        _row(firm_id="bank", sic=6021.0),
        _row(firm_id="util", sic=4911.0),
        _row(firm_id="nosic", sic=np.nan),
        _row(firm_id="negassets", assets_lag=-5e6),
        _row(firm_id="tiny", assets_lag=1e5),
        _row(firm_id="noni", net_income=np.nan),
    ])
    clean, log = apply_filters(frame, size_floor=10e6)

    assert set(clean["firm_id"]) == {"ok"}
    # every exclusion is accounted for, none vanish between steps
    assert log["rows_dropped"].sum() == len(frame) - len(clean)
    for i in range(1, len(log)):
        assert log.loc[i, "rows_before"] == log.loc[i - 1, "rows_after"]
    assert log.loc[log["step"].str.contains("financial"), "rows_dropped"].iloc[0] == 1
    assert log.loc[log["step"].str.contains("utilities"), "rows_dropped"].iloc[0] == 1
    assert log.loc[log["step"].str.contains("size floor"), "rows_dropped"].iloc[0] == 1


def test_utilities_kept_when_flag_is_off():
    frame = pd.DataFrame([_row(firm_id="util", sic=4911.0)])
    clean, log = apply_filters(frame, drop_utilities=False)
    assert len(clean) == 1
    assert not log["step"].str.contains("utilities").any()


def test_duplicate_firm_years_collapse_to_one():
    frame = pd.DataFrame([
        _row(firm_id="X", period_end=pd.Timestamp("2022-12-31")),
        _row(firm_id="X", period_end=pd.Timestamp("2022-12-31")),
    ])
    clean, _ = apply_filters(frame)
    assert len(clean) == 1


def test_scaled_variables_reject_non_positive_denominators():
    frame = pd.DataFrame([_row(revenue=0.0, equity_lag=-3e6)])
    scaled = add_scaled_variables(frame)
    assert np.isnan(scaled["ni_revenue"].iloc[0])      # zero revenue, not an infinity
    assert np.isnan(scaled["ni_equity_lag"].iloc[0])   # negative book equity flips sign


def test_cfo_placebo_uses_the_same_denominator_as_roa():
    frame = pd.DataFrame([_row(net_income=5.0, cfo=8.0, assets_lag=100.0)])
    scaled = add_scaled_variables(frame)
    assert scaled["roa"].iloc[0] == pytest.approx(0.05)
    assert scaled["cfo_at"].iloc[0] == pytest.approx(0.08)


def test_restrict_window_reports_what_it_removed():
    frame = pd.DataFrame({"roa": [0.05, -0.05, 0.5, np.nan]})
    inside, info = restrict_window(frame, "roa", window=0.10)
    assert len(inside) == 2
    assert info == {"column": "roa", "with_measure": 3, "inside_window": 2,
                    "outside_window": 1, "missing_measure": 1}
