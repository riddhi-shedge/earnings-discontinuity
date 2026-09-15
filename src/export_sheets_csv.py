"""Emit the Google Sheets dashboard as a single CSV whose cells carry live formulas.

    python -m src.export_sheets_csv   ->  dashboard/earnings_discontinuity_dashboard.csv

Why CSV: Google Drive converts text/csv into a native Google Sheet and evaluates any
cell that starts with "=", so the statistical test can be shipped as formulas without
moving a binary workbook through an API that caps payload size. Bin *counts* are
values exported from the pipeline; the expected count, z-statistic and p-value in
every row are computed by the sheet. SPARKLINE cells render the distributions.

Layout is one sheet, top to bottom: sample facts -> main-test summary (formulas that
reference the tables below) -> four live test tables -> robustness -> exclusion log.
"""

from __future__ import annotations

import csv
import io
from pathlib import Path

import pandas as pd

from .binning import bin_edges, histogram
from .panel import restrict_window

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "dashboard" / "earnings_discontinuity_dashboard.csv"

BLUE, ORANGE = "#2a78d6", "#eb6834"


class Sheet:
    """Row buffer with 1-based row bookkeeping so formulas can reference each other."""

    def __init__(self) -> None:
        self.rows: list[list] = []

    @property
    def next_row(self) -> int:
        return len(self.rows) + 1

    def add(self, *cells) -> int:
        self.rows.append(list(cells))
        return len(self.rows)

    def blank(self, n: int = 1) -> None:
        for _ in range(n):
            self.rows.append([])


def test_table(sh: Sheet, title: str, counts: list[int], edges, width: float) -> dict:
    """Write one live test table; return the row numbers other blocks need."""
    sh.add(title)
    sh.add(f"bin width {width:g}; window |x| <= 0.10; zero on a bin boundary. Counts are pipeline "
           "values; expected, z and p are live formulas: expected = (count above + count below)/2, "
           "z = (count - expected)/sd with the binomial sd used in Burgstahler-Dichev.")
    hdr = sh.add("bin_left", "bin_right", "count", "expected", "z", "p_value", "flag")
    first = hdr + 1
    nb = len(counts)
    last = first + nb - 1
    n_row = last + 1
    N = f"$C${n_row}"
    below_r = above_r = None
    for k in range(nb):
        r = first + k
        left, right = float(edges[k]), float(edges[k + 1])
        flag = ""
        if abs(right) < 1e-12:
            flag, below_r = "just below zero", r
        elif abs(left) < 1e-12:
            flag, above_r = "just above zero", r
        if 0 < k < nb - 1:
            exp = f"=(C{r-1}+C{r+1})/2"
            z = f"=(C{r}-D{r})/SQRT(C{r}*(1-C{r}/{N})+0.25*(C{r-1}+C{r+1})*(1-(C{r-1}+C{r+1})/{N}))"
            p = f"=2*(1-NORMSDIST(ABS(E{r})))"
        else:
            exp = z = p = ""
        sh.add(f"{left:.4f}", f"{right:.4f}", int(counts[k]), exp, z, p, flag)
    sh.add("N in window", "", f"=SUM(C{first}:C{last})")
    spark = sh.add("distribution",
                   f'=SPARKLINE(C{first}:C{last},{{"charttype","column";"color","{BLUE}"}})',
                   "", "", "", "", f"<- {nb} bars; zero is the boundary between bar {nb//2} and {nb//2+1}")
    sh.blank()
    return {"first": first, "last": last, "n_row": n_row, "below": below_r, "above": above_r, "spark": spark}


def main() -> None:
    panel = pd.read_parquet(DATA / "panel.parquet")
    robustness = pd.read_csv(DATA / "robustness_results.csv")
    drop_log = pd.read_csv(DATA / "drop_log.csv")
    roa, roa_info = restrict_window(panel, "roa")
    cfo, _ = restrict_window(panel, "cfo_at")

    sh = Sheet()
    sh.add("Earnings discontinuity at zero — dashboard")
    sh.add("Do public companies report too few small losses and too many small profits? "
           "Net income scaled by beginning-of-year total assets, SEC 10-K filings, fiscal years "
           f"{int(panel.fiscal_year.min())}-{int(panel.fiscal_year.max())}. "
           "Every expected count, z and p on this sheet is a live formula.")
    sh.blank()

    sh.add("SAMPLE")
    sh.add("Firm-years after filters", len(panel))
    sh.add("Distinct firms", int(panel.firm_id.nunique()))
    sh.add("Fiscal years", f"{int(panel.fiscal_year.min())}-{int(panel.fiscal_year.max())}")
    sh.add("Firm-years inside |ROA| <= 0.10", roa_info["inside_window"])
    sh.add("Median beginning-of-year assets (USD)", round(float(panel.assets_lag.median())))
    sh.add("Median ROA", round(float(panel.roa.median()), 4))
    sh.add("Share of firm-years reporting a loss", round(float((panel.net_income < 0).mean()), 4))
    sh.blank()

    # Reserve the summary block; fill it after the tables exist (needs their row numbers).
    sh.add("MAIN TEST — net income / beginning-of-year total assets (H1: deficit below zero, surplus above)")
    sum_hdr = sh.add("bin width", "N in window", "below: count", "below: expected", "below: z",
                     "below: p", "above: count", "above: expected", "above: z", "above: p")
    sum_rows = [sh.add() for _ in range(3)]
    sh.blank()
    sh.add("PLACEBO — cash flow from operations / beginning-of-year total assets (should show NO notch)")
    sh.add("bin width", "N in window", "below: count", "below: expected", "below: z",
           "below: p", "above: count", "above: expected", "above: z", "above: p")
    placebo_row = sh.add()
    sh.blank()
    sh.add("HOW TO READ: |z| > 1.96 is significant at 5%. The hypothesis needs BOTH a negative z below zero "
           "AND a positive z above zero. Read the two together, never one alone.")
    sh.blank()

    refs = []
    for w in (0.0025, 0.005, 0.01):
        counts = histogram(roa["roa"], w)["count"].tolist()
        refs.append((w, test_table(sh, f"TEST — ROA, bin width {w:g}", counts, bin_edges(w), w)))
    cfo_counts = histogram(cfo["cfo_at"], 0.005)["count"].tolist()
    cfo_ref = test_table(sh, "PLACEBO — CFO / lagged assets, bin width 0.005", cfo_counts, bin_edges(0.005), 0.005)

    def fill(row_idx: int, w: float, ref: dict) -> None:
        b, a = ref["below"], ref["above"]
        sh.rows[row_idx - 1] = [f"{w:g}", f"=C{ref['n_row']}",
                                f"=C{b}", f"=D{b}", f"=E{b}", f"=F{b}",
                                f"=C{a}", f"=D{a}", f"=E{a}", f"=F{a}"]

    for row_idx, (w, ref) in zip(sum_rows, refs):
        fill(row_idx, w, ref)
    fill(placebo_row, 0.005, cfo_ref)

    sh.add("ROBUSTNESS — every check from spec section 6 (values from notebooks/03_robustness.ipynb)")
    cols = ["check", "spec", "bin_width", "n_window", "count_below", "expected_below", "z_below",
            "p_below", "count_above", "expected_above", "z_above", "p_above"]
    sh.add(*cols)
    for r in robustness[cols].itertuples(index=False):
        sh.add(*[round(v, 4) if isinstance(v, float) else v for v in r])
    sh.blank()

    sh.add("EXCLUSION LOG — every sample filter, in order, with its count")
    sh.add("step", "rows_before", "rows_dropped", "rows_after", "firms_after", "rationale")
    for r in drop_log.itertuples(index=False):
        sh.add(r.step, r.rows_before, r.rows_dropped, r.rows_after, r.firms_after, r.rationale)

    buf = io.StringIO()
    csv.writer(buf, lineterminator="\n").writerows(sh.rows)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(buf.getvalue(), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(sh.rows)} rows, {OUT.stat().st_size:,} bytes")
    print("summary rows:", sum_rows, "placebo row:", placebo_row)
    for w, ref in refs:
        print(f"  ROA {w:g}: rows {ref['first']}-{ref['last']}, below r{ref['below']}, above r{ref['above']}")
    print(f"  CFO: rows {cfo_ref['first']}-{cfo_ref['last']}")


if __name__ == "__main__":
    main()
