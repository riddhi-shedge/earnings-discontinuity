"""Phase 0 data source: annual fundamentals for a ticker sample via yfinance.

This is the *prototype* sample (spec section 3, "fallback / prototype source"). It is
thin, survivorship-biased (yfinance only serves currently-listed tickers), and is used
as a sanity check, not as the headline result. The headline sample is the SEC
Financial Statement Data Sets loader in ``src/sec_loader.py``.

Design notes:
  * Every successful ticker is cached to its own parquet file, so the pull is
    resumable -- rerunning skips whatever is already on disk.
  * Failures are recorded (not raised) so one dead ticker cannot kill the run.
  * Requests are spaced out; yfinance is rate-limited and flaky.
"""

from __future__ import annotations

import json
import random
import time
from pathlib import Path

import pandas as pd
import requests

# SEC asks for a descriptive User-Agent with contact info on all automated requests;
# the address comes from SEC_CONTACT_EMAIL rather than being hardcoded here.
from .sec_loader import user_agent

SEC_TICKER_URL = "https://www.sec.gov/files/company_tickers.json"

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw" / "yfinance"

# yfinance row labels differ across statement versions; try these in order.
NI_KEYS = ["Net Income", "Net Income Common Stockholders", "Net Income From Continuing Operation Net Minority Interest"]
REV_KEYS = ["Total Revenue", "Operating Revenue"]
ASSET_KEYS = ["Total Assets"]
EQUITY_KEYS = ["Stockholders Equity", "Total Equity Gross Minority Interest"]
CFO_KEYS = ["Operating Cash Flow", "Cash Flow From Continuing Operating Activities"]
SHARE_KEYS = ["Diluted Average Shares", "Basic Average Shares"]


def sec_ticker_universe(timeout: int = 30) -> pd.DataFrame:
    """All exchange-listed tickers known to SEC EDGAR (cik, ticker, title)."""
    resp = requests.get(SEC_TICKER_URL, headers={"User-Agent": user_agent()}, timeout=timeout)
    resp.raise_for_status()
    rows = list(json.loads(resp.text).values())
    return pd.DataFrame(rows).rename(columns={"cik_str": "cik", "title": "name"})


def sample_tickers(n: int, seed: int = 42) -> list[str]:
    """A reproducible random draw from the EDGAR ticker universe.

    Random sampling (rather than, say, the S&P 500) matters here: an index of large
    profitable firms would contain almost no observations near zero earnings, which is
    the entire region of interest.
    """
    universe = sec_ticker_universe()
    # <=4 alphabetic characters keeps common stock and drops the 5-letter Nasdaq
    # class suffixes (W warrants, U units, R rights), which have no fundamentals.
    tickers = sorted({
        t.upper() for t in universe["ticker"]
        if isinstance(t, str) and t.isalpha() and len(t) <= 4
    })
    rng = random.Random(seed)
    return rng.sample(tickers, min(n, len(tickers)))


def _first_row(frame: pd.DataFrame, keys: list[str]) -> pd.Series | None:
    if frame is None or frame.empty:
        return None
    for key in keys:
        if key in frame.index:
            return frame.loc[key]
    return None


def fetch_one(ticker: str) -> pd.DataFrame | None:
    """Annual fundamentals for one ticker. Returns None when data is unusable."""
    import yfinance as yf

    tk = yf.Ticker(ticker)
    income = tk.income_stmt
    balance = tk.balance_sheet
    cashflow = tk.cashflow
    if income is None or balance is None or income.empty or balance.empty:
        return None

    fields = {
        "net_income": _first_row(income, NI_KEYS),
        "revenue": _first_row(income, REV_KEYS),
        "shares": _first_row(income, SHARE_KEYS),
        "total_assets": _first_row(balance, ASSET_KEYS),
        "book_equity": _first_row(balance, EQUITY_KEYS),
        "cfo": _first_row(cashflow, CFO_KEYS),
    }
    if fields["net_income"] is None or fields["total_assets"] is None:
        return None

    out = pd.DataFrame({k: v for k, v in fields.items() if v is not None})
    out.index = pd.to_datetime(out.index)
    out = out.sort_index()
    out.index.name = "period_end"
    out = out.reset_index()
    out.insert(0, "ticker", ticker)

    # Month-end closing price nearest each fiscal year end -> market value of equity.
    try:
        px = tk.history(period="10y", interval="1mo", auto_adjust=False)["Close"]
        if len(px):
            px.index = pd.to_datetime(px.index).tz_localize(None)
            out["price"] = [
                px.iloc[px.index.get_indexer([d], method="nearest")[0]]
                if abs((px.index[px.index.get_indexer([d], method="nearest")[0]] - d).days) <= 45
                else pd.NA
                for d in out["period_end"]
            ]
    except Exception:
        out["price"] = pd.NA

    for col in ("net_income", "revenue", "shares", "total_assets", "book_equity", "cfo", "price"):
        if col not in out.columns:
            out[col] = pd.NA
        out[col] = pd.to_numeric(out[col], errors="coerce")

    out["market_equity"] = out["price"] * out["shares"]
    return out


def pull(tickers: list[str], out_dir: Path = RAW_DIR, pause: float = 0.4,
         target: int | None = None, verbose: bool = True) -> tuple[pd.DataFrame, dict]:
    """Fetch (resumably) and return the stacked raw annual panel plus a status log."""
    out_dir.mkdir(parents=True, exist_ok=True)
    log = {"requested": len(tickers), "cached": 0, "fetched": 0, "no_data": 0, "errors": 0}
    frames: list[pd.DataFrame] = []

    for i, ticker in enumerate(tickers):
        path = out_dir / f"{ticker}.parquet"
        if path.exists():
            frames.append(pd.read_parquet(path))
            log["cached"] += 1
        else:
            try:
                frame = fetch_one(ticker)
            except Exception as exc:  # noqa: BLE001 - a bad ticker must not kill the pull
                log["errors"] += 1
                if verbose:
                    print(f"[{i + 1}/{len(tickers)}] {ticker}: error {type(exc).__name__}")
                time.sleep(pause)
                continue
            if frame is None or frame.empty:
                log["no_data"] += 1
                time.sleep(pause)
                continue
            frame.to_parquet(path, index=False)
            frames.append(frame)
            log["fetched"] += 1
            time.sleep(pause)

        if verbose and (i + 1) % 25 == 0:
            print(f"[{i + 1}/{len(tickers)}] usable={len(frames)} {log}")
        if target is not None and len(frames) >= target:
            break

    log["usable_tickers"] = len(frames)
    panel = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    return panel, log


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Phase 0 yfinance pull")
    ap.add_argument("--draw", type=int, default=900, help="tickers to draw from EDGAR universe")
    ap.add_argument("--target", type=int, default=300, help="stop once this many usable tickers are cached")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    sample = sample_tickers(args.draw, seed=args.seed)
    panel, status = pull(sample, target=args.target)
    dest = RAW_DIR.parent.parent / "yf_raw_panel.parquet"
    panel.to_parquet(dest, index=False)
    print(status)
    print(f"rows={len(panel)} tickers={panel['ticker'].nunique() if len(panel) else 0} -> {dest}")
