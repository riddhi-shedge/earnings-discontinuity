"""Headline data source: SEC Financial Statement Data Sets (XBRL-derived flat files).

Source: https://www.sec.gov/data-research/sec-markets-data/financial-statement-data-sets
Quarterly ZIPs at https://www.sec.gov/files/dera/data/financial-statement-data-sets/{YYYY}q{Q}.zip
Coverage as of this build: 2009q1 through 2026q1.

Schema verified against the 2026q1 archive readme.htm on 2026-08-11:

  sub.txt (36 cols)  adsh cik name sic countryba stprba cityba zipba bas1 bas2 baph
                     countryma stprma cityma zipma mas1 mas2 countryinc stprinc ein
                     former changed afs wksi fye form period fy fp filed accepted
                     prevrpt detail instance nciks aciks
  num.txt (10 cols)  adsh tag version ddate qtrs uom segments coreg value footnote

  ddate    period end date, rounded to nearest month end (yyyymmdd)
  qtrs     number of quarters the value spans; 0 = point-in-time (balance sheet),
           4 = a full annual period (income statement / cash flow statement)
  segments non-empty means the fact is a segment/dimension breakdown, not the
           consolidated total -- we keep only blank segments and blank coreg.

Why the numbers come from 10-K filings only: a 10-K carries the *comparative*
balance sheet, so a single submission gives us both current-year and prior-year
total assets. That is where the lagged (beginning-of-year) denominator required by
spec section 4 comes from -- no cross-filing join needed, and the prior-year figure
is the one the filer itself presents as the comparative.
"""

from __future__ import annotations

import os
import warnings
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw_sec"
CACHE_DIR = ROOT / "data" / "cache"

BASE_URL = "https://www.sec.gov/files/dera/data/financial-statement-data-sets"

PLACEHOLDER_EMAIL = "your-email@example.com"


def user_agent() -> str:
    """The User-Agent sent to SEC servers.

    SEC's fair-access policy requires automated requests to identify themselves with a
    descriptive name and a working contact address; requests without one get rate
    limited or blocked. Set ``SEC_CONTACT_EMAIL`` before running any download, so the
    address stays out of the source tree.
    """
    email = os.environ.get("SEC_CONTACT_EMAIL", "").strip()
    if not email:
        warnings.warn(
            "SEC_CONTACT_EMAIL is not set, so requests to sec.gov will carry a "
            f"placeholder contact ({PLACEHOLDER_EMAIL}). SEC may rate-limit or block "
            "these. Export SEC_CONTACT_EMAIL=you@example.com before downloading.",
            RuntimeWarning, stacklevel=2)
        email = PLACEHOLDER_EMAIL
    return f"earnings-discontinuity-study {email}"

NUM_COLS = ["adsh", "tag", "version", "ddate", "qtrs", "uom", "segments", "coreg", "value", "footnote"]

SUB_KEEP = ["adsh", "cik", "name", "sic", "fye", "form", "period", "fy", "fp", "filed", "prevrpt", "detail"]

# us-gaap tags we pull. Several concepts have more than one commonly used tag; the
# panel builder resolves them in the priority order given by ``TAG_PRIORITY``.
TAGS: set[str] = {
    # balance sheet (qtrs = 0)
    "Assets",
    "StockholdersEquity",
    "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
    # income statement (qtrs = 4)
    "NetIncomeLoss",
    "ProfitLoss",
    "Revenues",
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "RevenueFromContractWithCustomerIncludingAssessedTax",
    "SalesRevenueNet",
    "SalesRevenueGoodsNet",
    # cash flow statement (qtrs = 4) -- the section 6.4 placebo
    "NetCashProvidedByUsedInOperatingActivities",
    "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
}

TAG_PRIORITY: dict[str, list[str]] = {
    "assets": ["Assets"],
    "equity": [
        "StockholdersEquity",
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
    ],
    "net_income": ["NetIncomeLoss", "ProfitLoss"],
    "revenue": [
        "Revenues",
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "RevenueFromContractWithCustomerIncludingAssessedTax",
        "SalesRevenueNet",
        "SalesRevenueGoodsNet",
    ],
    "cfo": [
        "NetCashProvidedByUsedInOperatingActivities",
        "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
    ],
}

POINT_IN_TIME = {"assets", "equity"}  # qtrs == 0; the rest are qtrs == 4


@dataclass
class QuarterStats:
    quarter: str
    submissions_total: int = 0
    submissions_10k: int = 0
    num_lines: int = 0
    num_kept: int = 0
    num_malformed: int = 0
    extras: dict = field(default_factory=dict)


def quarters(start: str, end: str) -> list[str]:
    """Inclusive list of 'YYYYqQ' labels."""
    sy, sq = int(start[:4]), int(start[5])
    ey, eq = int(end[:4]), int(end[5])
    out = []
    y, q = sy, sq
    while (y, q) <= (ey, eq):
        out.append(f"{y}q{q}")
        q += 1
        if q == 5:
            y, q = y + 1, 1
    return out


def download_quarter(quarter: str, raw_dir: Path = RAW_DIR, timeout: int = 180) -> Path:
    """Download one quarterly ZIP (skipped if already present). Never committed."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    dest = raw_dir / f"{quarter}.zip"
    if dest.exists() and dest.stat().st_size > 1_000_000:
        return dest
    resp = requests.get(f"{BASE_URL}/{quarter}.zip", headers={"User-Agent": user_agent()},
                        timeout=timeout, stream=True)
    resp.raise_for_status()
    tmp = dest.with_suffix(".zip.part")
    with tmp.open("wb") as fh:
        for chunk in resp.iter_content(chunk_size=1 << 20):
            fh.write(chunk)
    tmp.rename(dest)
    return dest


def _read_sub(zf: zipfile.ZipFile) -> pd.DataFrame:
    with zf.open("sub.txt") as fh:
        sub = pd.read_csv(fh, sep="\t", dtype=str, usecols=SUB_KEEP,
                          quoting=3, on_bad_lines="skip", low_memory=False)
    return sub


def _read_num(zf: zipfile.ZipFile, adsh_keep: set[str], stats: QuarterStats) -> pd.DataFrame:
    """Stream num.txt, keeping only consolidated USD facts for our tags and filings.

    Parsed by hand rather than with ``read_csv``: num.txt is ~550 MB per quarter and
    its free-text ``footnote`` field breaks naive quoting. Splitting on tabs and
    filtering before materialising anything keeps memory flat and lets us count
    malformed lines exactly instead of dropping them silently.
    """
    rows: list[tuple] = []
    with zf.open("num.txt") as fh:
        header = fh.readline().decode("utf-8", "replace").rstrip("\r\n").split("\t")
        if header[:9] != NUM_COLS[:9]:
            raise RuntimeError(f"num.txt schema changed: {header}")
        for raw in fh:
            stats.num_lines += 1
            parts = raw.decode("utf-8", "replace").rstrip("\r\n").split("\t")
            if len(parts) < 9:
                stats.num_malformed += 1
                continue
            adsh, tag, _ver, ddate, qtrs, uom, segments, coreg, value = parts[:9]
            if tag not in TAGS or segments or coreg or uom != "USD":
                continue
            if adsh not in adsh_keep:
                continue
            rows.append((adsh, tag, ddate, qtrs, value))
    stats.num_kept = len(rows)
    num = pd.DataFrame(rows, columns=["adsh", "tag", "ddate", "qtrs", "value"])
    num["ddate"] = pd.to_datetime(num["ddate"], format="%Y%m%d", errors="coerce")
    num["qtrs"] = pd.to_numeric(num["qtrs"], errors="coerce")
    num["value"] = pd.to_numeric(num["value"], errors="coerce")
    clean = num.dropna(subset=["ddate", "qtrs", "value"])
    stats.extras["num_unparseable_values"] = len(num) - len(clean)
    return clean


def extract_quarter(quarter: str, raw_dir: Path = RAW_DIR,
                    cache_dir: Path = CACHE_DIR) -> tuple[pd.DataFrame, pd.DataFrame, QuarterStats]:
    """Download (if needed) and reduce one quarter to (sub_10k, num_facts, stats)."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    sub_path = cache_dir / f"sub_{quarter}.parquet"
    num_path = cache_dir / f"num_{quarter}.parquet"
    stats = QuarterStats(quarter=quarter)

    if sub_path.exists() and num_path.exists():
        stats.extras["from_cache"] = True
        return pd.read_parquet(sub_path), pd.read_parquet(num_path), stats

    zip_path = download_quarter(quarter, raw_dir)
    with zipfile.ZipFile(zip_path) as zf:
        sub = _read_sub(zf)
        stats.submissions_total = len(sub)
        sub = sub[sub["form"] == "10-K"].copy()
        stats.submissions_10k = len(sub)
        num = _read_num(zf, set(sub["adsh"]), stats)

    sub["cik"] = pd.to_numeric(sub["cik"], errors="coerce")
    sub["sic"] = pd.to_numeric(sub["sic"], errors="coerce")
    sub["fy"] = pd.to_numeric(sub["fy"], errors="coerce")
    sub["period"] = pd.to_datetime(sub["period"], format="%Y%m%d", errors="coerce")
    sub["filed"] = pd.to_datetime(sub["filed"], format="%Y%m%d", errors="coerce")
    sub["source_quarter"] = quarter

    sub.to_parquet(sub_path, index=False)
    num.to_parquet(num_path, index=False)
    return sub, num, stats


def build_raw_panel(quarter_list: list[str], verbose: bool = True) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Assemble one row per 10-K filing with current and prior-year figures.

    Returns ``(panel, quarter_log)``. The panel is *raw* -- sample filters live in
    ``src/panel.py`` so that every exclusion is applied and counted in one place.
    """
    subs, nums, logs = [], [], []
    for quarter in quarter_list:
        sub, num, stats = extract_quarter(quarter)
        subs.append(sub)
        nums.append(num)
        logs.append(vars(stats) | {"sub_rows": len(sub), "num_rows": len(num)})
        if verbose:
            print(f"{quarter}: 10-K subs={len(sub):,} facts={len(num):,}")

    sub_all = pd.concat(subs, ignore_index=True)
    num_all = pd.concat(nums, ignore_index=True)
    quarter_log = pd.DataFrame(logs)

    # One filing per (cik, fiscal period end): keep the most recently filed.
    sub_all = (sub_all.sort_values("filed")
               .drop_duplicates(subset=["cik", "period"], keep="last"))

    panel = _assemble(sub_all, num_all)
    return panel, quarter_log


def _pick(frame: pd.DataFrame, tags: list[str]) -> pd.DataFrame:
    """Collapse alternative tags to one value per filing, first available wins."""
    order = {tag: i for i, tag in enumerate(tags)}
    sel = frame[frame["tag"].isin(order)].copy()
    sel["_rank"] = sel["tag"].map(order)
    sel = sel.sort_values("_rank").drop_duplicates(subset=["adsh"], keep="first")
    return sel[["adsh", "value"]]


def _assemble(sub: pd.DataFrame, num: pd.DataFrame) -> pd.DataFrame:
    """Join facts onto filings at the current and prior fiscal-year end dates."""
    period = sub.set_index("adsh")["period"]
    num = num[num["adsh"].isin(period.index)].copy()
    num["period"] = num["adsh"].map(period)
    offset = (num["ddate"] - num["period"]).dt.days

    # ddate is rounded to month end, and fiscal years vary in length (52/53-week
    # filers), so match on windows rather than exact dates.
    is_current = offset.between(-20, 20)
    is_prior = offset.between(-400, -330)

    out = sub.copy()
    for concept, tags in TAG_PRIORITY.items():
        qtrs = 0 if concept in POINT_IN_TIME else 4
        base = num[num["qtrs"] == qtrs]
        cur = _pick(base[is_current.loc[base.index]], tags).rename(columns={"value": concept})
        out = out.merge(cur, on="adsh", how="left")
        if concept in POINT_IN_TIME:
            lag = _pick(base[is_prior.loc[base.index]], tags).rename(columns={"value": f"{concept}_lag"})
            out = out.merge(lag, on="adsh", how="left")

    out = out.rename(columns={"period": "period_end"})
    out["fiscal_year"] = out["period_end"].dt.year.where(
        out["period_end"].dt.month >= 6, out["period_end"].dt.year - 1)
    return out


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Build the raw SEC 10-K panel")
    ap.add_argument("--start", default="2017q1")
    ap.add_argument("--end", default="2026q1")
    args = ap.parse_args()

    qs = quarters(args.start, args.end)
    print(f"{len(qs)} quarters: {qs[0]} .. {qs[-1]}")
    raw, qlog = build_raw_panel(qs)
    dest = ROOT / "data" / "sec_raw_panel.parquet"
    raw.to_parquet(dest, index=False)
    qlog.to_csv(ROOT / "data" / "sec_quarter_log.csv", index=False)
    print(f"raw panel rows={len(raw):,} ciks={raw['cik'].nunique():,} -> {dest}")
