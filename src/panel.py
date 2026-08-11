"""Sample construction: scaled-earnings variables and the section 3 filters.

Two rules this module exists to enforce:

1. **Lagged denominator.** ``ROA_it = NetIncome_it / TotalAssets_i,t-1``. End-of-year
   assets already embed the current year's earnings, which would put the thing being
   measured into the denominator (spec section 4, and the first entry in the pitfall
   list).
2. **No silent drops.** Every filter returns a count. ``apply_filters`` hands back
   ``(clean_panel, drop_log)`` and the drop log is reproduced in full in the README.
   Filter choices are exactly where the Durtschi-Easton critique bites, so each one
   carries a written rationale alongside its count.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

DEFAULT_SIZE_FLOOR = 10_000_000.0  # USD of lagged total assets; sensitivity tested in 6.3

# Columns the discontinuity tests expect downstream, whatever the source.
PANEL_COLUMNS = [
    "firm_id", "name", "sic", "fiscal_year", "period_end",
    "net_income", "revenue", "cfo", "assets", "assets_lag", "equity_lag", "market_equity",
]


@dataclass
class FilterStep:
    step: str
    rationale: str
    rows_before: int
    rows_dropped: int
    rows_after: int
    firms_after: int

    def as_row(self) -> dict:
        return vars(self)


class DropLog:
    """Accumulates one row per filter so nothing leaves the sample uncounted."""

    def __init__(self) -> None:
        self.steps: list[FilterStep] = []

    def record(self, frame_before: pd.DataFrame, frame_after: pd.DataFrame,
               step: str, rationale: str) -> pd.DataFrame:
        self.steps.append(FilterStep(
            step=step,
            rationale=rationale,
            rows_before=len(frame_before),
            rows_dropped=len(frame_before) - len(frame_after),
            rows_after=len(frame_after),
            firms_after=int(frame_after["firm_id"].nunique()) if len(frame_after) else 0,
        ))
        return frame_after

    def to_frame(self) -> pd.DataFrame:
        return pd.DataFrame([s.as_row() for s in self.steps])


def add_scaled_variables(panel: pd.DataFrame) -> pd.DataFrame:
    """Attach every scaled measure used by the main test and the robustness checks.

    ``roa`` is the headline variable. ``cfo_at`` is the section 6.4 placebo and is
    scaled by *the same* lagged-asset denominator on purpose -- if the scaling itself
    manufactures a notch, it will manufacture one here too.
    """
    out = panel.copy()

    def safe_div(num: pd.Series, den: pd.Series, positive_only: bool = True) -> pd.Series:
        den = pd.to_numeric(den, errors="coerce")
        num = pd.to_numeric(num, errors="coerce")
        den = den.where(den > 0) if positive_only else den.where(den != 0)
        return num / den

    out["roa"] = safe_div(out["net_income"], out["assets_lag"])          # headline
    out["ni_revenue"] = safe_div(out["net_income"], out["revenue"])      # 6.1
    out["ni_equity_lag"] = safe_div(out["net_income"], out["equity_lag"])  # 6.1 (book equity)
    out["ni_market_equity"] = safe_div(out["net_income"], out["market_equity"])  # 6.1 (MVE)
    out["cfo_at"] = safe_div(out["cfo"], out["assets_lag"])              # 6.4 placebo
    return out


def apply_filters(panel: pd.DataFrame, *, drop_utilities: bool = True,
                  size_floor: float = DEFAULT_SIZE_FLOOR,
                  require_net_income: bool = True,
                  fiscal_years: tuple[int, int] | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Apply the spec section 3 filters in a fixed order, counting every exclusion.

    The order is fixed *before* looking at any result. Returns the clean panel and the
    drop log. The |scaled earnings| <= 0.10 analysis window is deliberately NOT applied
    here -- it is a windowing choice made per-denominator at test time, and applying it
    to the cached panel would prevent the robustness checks from using their own scales.
    """
    log = DropLog()
    df = panel.copy()
    log.record(df, df, "0. raw firm-years", "All 10-K firm-years assembled from the source.")

    if fiscal_years is not None:
        lo, hi = fiscal_years
        before = df
        df = df[df["fiscal_year"].between(lo, hi)]
        log.record(before, df, f"1. restrict to fiscal years {lo}-{hi}",
                   "Only these fiscal years are fully covered by the downloaded filing "
                   "quarters. Stragglers outside the range are delinquent filers whose "
                   "years are represented by a handful of firms, not a usable cross-section.")

    before = df
    df = df[df["sic"].notna()]
    log.record(before, df, "2. drop missing SIC",
               "Industry filters below cannot be applied without an industry code.")

    before = df
    df = df[~df["sic"].between(6000, 6999)]
    log.record(before, df, "3. drop financial firms (SIC 6000-6999)",
               "Bank and insurer balance sheets are structurally different; total assets "
               "does not mean the same thing, so scaling by it is not comparable.")

    if drop_utilities:
        before = df
        df = df[~df["sic"].between(4900, 4949)]
        log.record(before, df, "4. drop utilities (SIC 4900-4949)",
                   "Rate-regulated returns make utility earnings mechanically smooth near "
                   "a target; conventional in this literature. Optional filter, applied here.")

    if require_net_income:
        before = df
        df = df[df["net_income"].notna()]
        log.record(before, df, "5. drop missing net income",
                   "No numerator, no observation.")

    before = df
    df = df[df["assets_lag"].notna() & (df["assets_lag"] > 0)]
    log.record(before, df, "6. drop missing or non-positive lagged total assets",
               "Denominator must exist and be positive; a non-positive denominator flips "
               "the sign of the scaled measure. Beginning-of-year assets, never end-of-year.")

    before = df
    df = df[df["assets_lag"] >= size_floor]
    log.record(before, df, f"7. size floor: lagged assets >= ${size_floor:,.0f}",
               "Tiny denominators produce extreme scaled values and are the known source of "
               "the scaling artifact in Durtschi-Easton. Sensitivity to this floor is "
               "reported in robustness check 6.3.")

    before = df
    df = df.sort_values("period_end").drop_duplicates(subset=["firm_id", "fiscal_year"], keep="last")
    log.record(before, df, "8. one filing per firm-fiscal-year",
               "Amended and transition-period filings can duplicate a firm-year; the most "
               "recent period end is kept.")

    df = add_scaled_variables(df)
    return df.reset_index(drop=True), log.to_frame()


def restrict_window(panel: pd.DataFrame, column: str, window: float = 0.10) -> tuple[pd.DataFrame, dict]:
    """Restrict to |scaled earnings| <= window and report what that costs.

    Reported separately from the sample filters because it is an analysis-window
    choice, not a sample-quality one (spec section 3, filter 5).
    """
    present = panel[panel[column].notna()]
    inside = present[present[column].abs() <= window]
    return inside, {
        "column": column,
        "with_measure": len(present),
        "inside_window": len(inside),
        "outside_window": len(present) - len(inside),
        "missing_measure": len(panel) - len(present),
    }


def build_sec_panel(raw: pd.DataFrame) -> pd.DataFrame:
    """Map the raw SEC 10-K frame onto the shared panel schema."""
    out = raw.rename(columns={"cik": "firm_id"}).copy()
    out["market_equity"] = np.nan  # not available in the SEC flat files; see README
    for col in PANEL_COLUMNS:
        if col not in out.columns:
            out[col] = np.nan
    return out[PANEL_COLUMNS + [c for c in ("source_quarter", "adsh", "filed") if c in out.columns]]


def build_yf_panel(raw: pd.DataFrame, sic_map: dict[str, float] | None = None) -> pd.DataFrame:
    """Map the raw yfinance frame onto the shared panel schema.

    Lagged assets come from the firm's own previous annual observation, so the first
    year of every ticker is necessarily dropped -- that is the correct behaviour, not a
    bug: there is no beginning-of-year balance sheet for it.
    """
    out = raw.copy()
    out["period_end"] = pd.to_datetime(out["period_end"])
    out = out.sort_values(["ticker", "period_end"])

    prior = out.groupby("ticker", observed=True)["period_end"].shift(1)
    gap = (out["period_end"] - prior).dt.days
    # Only treat the previous row as "beginning of year" if it really is ~one year back.
    valid_lag = gap.between(300, 430)
    out["assets_lag"] = out.groupby("ticker", observed=True)["total_assets"].shift(1).where(valid_lag)
    out["equity_lag"] = out.groupby("ticker", observed=True)["book_equity"].shift(1).where(valid_lag)

    out["firm_id"] = out["ticker"]
    out["name"] = out["ticker"]
    out["fiscal_year"] = np.where(out["period_end"].dt.month >= 6,
                                  out["period_end"].dt.year, out["period_end"].dt.year - 1)
    out["sic"] = out["ticker"].map(sic_map) if sic_map else np.nan
    out["assets"] = out["total_assets"]
    for col in PANEL_COLUMNS:
        if col not in out.columns:
            out[col] = np.nan
    return out[PANEL_COLUMNS + ["ticker"]]
