"""Turn raw source pulls into the cached analysis panels.

Run once (``python src/build_panel.py``); after that every notebook reads the parquet
and no notebook ever re-downloads anything. Outputs:

    data/panel.parquet             headline SEC 10-K panel, filters applied
    data/drop_log.csv              one counted row per exclusion, reproduced in the README
    data/panel_yfinance.parquet    Phase 0 prototype panel
    data/drop_log_yfinance.csv     its exclusion log
"""

from __future__ import annotations

import glob
from pathlib import Path

import pandas as pd

from .panel import apply_filters, build_sec_panel, build_yf_panel

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

# Fiscal years fully covered by the downloaded filing quarters (2017q1-2026q1).
SEC_FISCAL_YEARS = (2016, 2025)


def sec_sic_map() -> dict[int, float]:
    """CIK -> SIC, taken from the cached SEC submission files."""
    files = sorted(glob.glob(str(DATA / "cache" / "sub_*.parquet")))
    if not files:
        return {}
    subs = pd.concat([pd.read_parquet(f, columns=["cik", "sic"]) for f in files])
    subs = subs.dropna().drop_duplicates("cik")
    return dict(zip(subs["cik"], subs["sic"]))


def ticker_sic_map() -> dict[str, float]:
    """Ticker -> SIC, by way of EDGAR's ticker/CIK mapping."""
    from .yf_loader import sec_ticker_universe

    universe = sec_ticker_universe()
    cik_to_sic = sec_sic_map()
    pairs = zip(universe["ticker"].str.upper(), universe["cik"])
    return {t: cik_to_sic[c] for t, c in pairs if c in cik_to_sic}


def build_sec() -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = pd.read_parquet(DATA / "sec_raw_panel.parquet")
    panel, log = apply_filters(build_sec_panel(raw), fiscal_years=SEC_FISCAL_YEARS)
    panel.to_parquet(DATA / "panel.parquet", index=False)
    log.to_csv(DATA / "drop_log.csv", index=False)
    return panel, log


def build_yfinance() -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = pd.read_parquet(DATA / "yf_raw_panel.parquet")
    panel, log = apply_filters(build_yf_panel(raw, ticker_sic_map()))
    panel.to_parquet(DATA / "panel_yfinance.parquet", index=False)
    log.to_csv(DATA / "drop_log_yfinance.csv", index=False)
    return panel, log


if __name__ == "__main__":
    for name, builder in (("SEC 10-K", build_sec), ("yfinance prototype", build_yfinance)):
        try:
            panel, log = builder()
        except FileNotFoundError as exc:
            print(f"{name}: skipped, missing raw pull ({exc.filename})")
            continue
        print(f"\n=== {name} ===")
        print(log.drop(columns=["rationale"]).to_string(index=False))
        print(f"final: {len(panel):,} firm-years, {panel['firm_id'].nunique():,} firms, "
              f"fiscal years {int(panel['fiscal_year'].min())}-{int(panel['fiscal_year'].max())}")
