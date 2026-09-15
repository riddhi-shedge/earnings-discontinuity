"""Build the Excel / Google Sheets dashboard workbook.

    python -m src.export_dashboard

This is a *live model*, not a paste of results. The cleaned panel goes in as data,
the scaled metrics (ROA, NI/revenue, NI/equity, CFO/assets) are Excel formulas, and
every histogram, neighbour expectation and z-statistic is a COUNTIFS / arithmetic
formula over that sheet. Change a number in the panel and every chart moves.

Sheets
  Summary        headline numbers, all cross-referenced by formula
  ROA_0.0025 /   the section 5.3 test at each bin width, with the histogram chart
  ROA_0.005 /
  ROA_0.01
  CFO_0.005      the section 6.4 placebo, same machinery on cash flow
  Robustness     every robustness result (from data/robustness_results.csv)
  Exclusion_log  every sample filter with its count and rationale
  Panel          31,240 firm-years, metrics as formulas
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.chart.series import DataPoint
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from .binning import bin_edges

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "dashboard" / "earnings_discontinuity_dashboard.xlsx"

INK = "0B0B0B"
MUTED = "84837C"
RULE = "E3E2DD"
BLUE = "2A78D6"
ORANGE = "EB6834"
HEAD_FILL = PatternFill("solid", fgColor="F3F2EE")
FOCAL_FILL = PatternFill("solid", fgColor="FDE8DF")
HIT_FILL = PatternFill("solid", fgColor="FFF1CC")
THIN = Side(style="thin", color=RULE)

PANEL_COLS = ["firm_id", "name", "sic", "fiscal_year", "period_end",
              "net_income", "assets_lag", "revenue", "equity_lag", "cfo"]
# formula columns appended after the data columns, in this order
METRIC_COLS = [("ROA", "net_income", "assets_lag"),
               ("NI_over_revenue", "net_income", "revenue"),
               ("NI_over_equity_lag", "net_income", "equity_lag"),
               ("CFO_over_assets_lag", "cfo", "assets_lag")]


def _style_header(ws, row: int, ncols: int) -> None:
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.font = Font(bold=True, color=INK)
        cell.fill = HEAD_FILL
        cell.border = Border(bottom=THIN)
        cell.alignment = Alignment(vertical="center", wrap_text=True)


def _autowidth(ws, widths: dict[int, float] | None = None, default: float = 14) -> None:
    for c in range(1, ws.max_column + 1):
        ws.column_dimensions[get_column_letter(c)].width = (widths or {}).get(c, default)


def build_panel_sheet(wb: Workbook, panel: pd.DataFrame) -> dict[str, str]:
    """Write the data and return {metric: column letter} for the formula columns."""
    ws = wb.create_sheet("Panel")
    headers = PANEL_COLS + [m[0] for m in METRIC_COLS] + ["first_row_for_firm"]
    ws.append(headers)
    _style_header(ws, 1, len(headers))

    col_of = {h: get_column_letter(i + 1) for i, h in enumerate(headers)}
    n = len(panel)
    data = panel[PANEL_COLS].copy()
    data["period_end"] = pd.to_datetime(data["period_end"]).dt.date
    data["sic"] = data["sic"].astype("Int64")
    data["fiscal_year"] = data["fiscal_year"].astype(int)

    for r, row in enumerate(data.itertuples(index=False), start=2):
        vals = [None if (isinstance(v, float) and np.isnan(v)) or v is pd.NA else v for v in row]
        for c, v in enumerate(vals, start=1):
            ws.cell(row=r, column=c, value=v)
        for j, (_name, num, den) in enumerate(METRIC_COLS):
            c = len(PANEL_COLS) + 1 + j
            ncol, dcol = col_of[num], col_of[den]
            # positive denominators only, matching src/panel.py::add_scaled_variables
            ws.cell(row=r, column=c,
                    value=f'=IF(AND(ISNUMBER({ncol}{r}),ISNUMBER({dcol}{r}),{dcol}{r}>0),{ncol}{r}/{dcol}{r},"")')
        # portable distinct-count helper (array idioms differ across Excel / Sheets / Numbers)
        ws.cell(row=r, column=len(headers),
                value=f"=IF(COUNTIF($A$2:A{r},A{r})=1,1,0)")

    for c in range(len(PANEL_COLS) + 1, len(headers)):
        for r in range(2, n + 2):
            ws.cell(row=r, column=c).number_format = "0.0000"
    for name in ("net_income", "assets_lag", "revenue", "equity_lag", "cfo"):
        for r in range(2, n + 2):
            ws[f"{col_of[name]}{r}"].number_format = "#,##0"
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}{n + 1}"
    _autowidth(ws, {2: 34, 5: 12}, default=15)
    return col_of | {"_last_row": str(n + 1)}


def build_hist_sheet(wb: Workbook, title: str, metric_col: str | None, last_row: str | None,
                     width: float, label: str, counts: list[int] | None = None) -> str:
    """One bin-width test as live formulas plus a chart. Returns the sheet name.

    With ``counts`` given, the bin counts are written as values (the Google Sheets
    edition, which cannot carry the 31k-row panel through the upload route) and the
    expectation / variance / z / p-value formulas run on top of them. Without it, the
    counts are COUNTIFS over the Panel sheet (the full Excel model).
    """
    ws = wb.create_sheet(title)
    edges = bin_edges(width)
    rng = None if counts is not None else f"Panel!${metric_col}$2:${metric_col}${last_row}"

    ws["A1"] = f"{label} — bin width {width:g}, window |x| ≤ 0.10, zero on a bin boundary"
    ws["A1"].font = Font(bold=True, size=13, color=INK)
    ws["A3"] = ("Bin counts are values exported from the Python pipeline; everything to their right is a live formula."
                if counts is not None else
                "Bin counts are COUNTIFS over the Panel sheet; everything is a live formula.")
    ws["A3"].font = Font(italic=True, color=MUTED, size=9)
    ws["A2"] = ("expected_i = (count_i-1 + count_i+1) / 2;  "
                "sd_i = sqrt( N·p_i·(1-p_i) + ¼·N·(p_i-1+p_i+1)·(1-p_i-1-p_i+1) );  z = (count - expected) / sd")
    ws["A2"].font = Font(italic=True, color=MUTED, size=9)

    hdr_row = 4
    headers = ["bin_left", "bin_right", "bin_mid", "count", "expected", "p_i", "variance", "z", "p_value (two-sided)", "flag"]
    for i, h in enumerate(headers, start=1):
        ws.cell(row=hdr_row, column=i, value=h)
    _style_header(ws, hdr_row, len(headers))

    first = hdr_row + 1
    nb = len(edges) - 1
    last = first + nb - 1
    n_cell = f"$D${last + 2}"

    for k in range(nb):
        r = first + k
        left, right = float(edges[k]), float(edges[k + 1])
        ws.cell(row=r, column=1, value=left)
        ws.cell(row=r, column=2, value=right)
        ws.cell(row=r, column=3, value=f"=(A{r}+B{r})/2")
        if counts is not None:
            ws.cell(row=r, column=4, value=int(counts[k]))
        else:
            ws.cell(row=r, column=4, value=f'=COUNTIFS({rng},">="&A{r},{rng},"<"&B{r})')
        if 0 < k < nb - 1:
            ws.cell(row=r, column=5, value=f"=(D{r-1}+D{r+1})/2")
            ws.cell(row=r, column=6, value=f"=D{r}/{n_cell}")
            ws.cell(row=r, column=7,
                    value=f"={n_cell}*F{r}*(1-F{r})+0.25*{n_cell}*(F{r-1}+F{r+1})*(1-F{r-1}-F{r+1})")
            ws.cell(row=r, column=8, value=f'=IF(G{r}>0,(D{r}-E{r})/SQRT(G{r}),"")')
            ws.cell(row=r, column=9, value=f'=IF(H{r}="","",2*(1-NORMSDIST(ABS(H{r}))))')
        else:
            ws.cell(row=r, column=6, value=f"=D{r}/{n_cell}")
        is_below = abs(right) < 1e-12
        is_above = abs(left) < 1e-12
        flag = "just below zero" if is_below else ("just above zero" if is_above else "")
        ws.cell(row=r, column=10, value=flag)
        if flag:
            for c in range(1, len(headers) + 1):
                ws.cell(row=r, column=c).fill = FOCAL_FILL
                ws.cell(row=r, column=c).font = Font(bold=True)
        for c, fmt in ((1, "0.0000"), (2, "0.0000"), (3, "0.0000"), (5, "0.0"),
                       (6, "0.0000"), (7, "0.0"), (8, "0.00"), (9, "0.000")):
            ws.cell(row=r, column=c).number_format = fmt

    ws.cell(row=last + 2, column=3, value="N in window").font = Font(bold=True)
    ws.cell(row=last + 2, column=4, value=f"=SUM(D{first}:D{last})").font = Font(bold=True)
    ws.cell(row=last + 2, column=4).number_format = "#,##0"

    # headline cells other sheets can reference
    below_r = next(first + k for k in range(nb) if abs(float(edges[k + 1])) < 1e-12)
    above_r = below_r + 1
    ws.cell(row=last + 4, column=3, value="bin just below zero").font = Font(bold=True)
    ws.cell(row=last + 4, column=4, value=f"=D{below_r}")
    ws.cell(row=last + 4, column=5, value=f"=E{below_r}")
    ws.cell(row=last + 4, column=8, value=f"=H{below_r}")
    ws.cell(row=last + 4, column=9, value=f"=I{below_r}")
    ws.cell(row=last + 5, column=3, value="bin just above zero").font = Font(bold=True)
    ws.cell(row=last + 5, column=4, value=f"=D{above_r}")
    ws.cell(row=last + 5, column=5, value=f"=E{above_r}")
    ws.cell(row=last + 5, column=8, value=f"=H{above_r}")
    ws.cell(row=last + 5, column=9, value=f"=I{above_r}")
    for r in (last + 4, last + 5):
        ws.cell(row=r, column=5).number_format = "0.0"
        ws.cell(row=r, column=8).number_format = "0.00"
        ws.cell(row=r, column=9).number_format = "0.000"

    ws.conditional_formatting.add(f"H{first}:H{last}", CellIsRule(operator="greaterThan", formula=["1.96"], fill=HIT_FILL))
    ws.conditional_formatting.add(f"H{first}:H{last}", CellIsRule(operator="lessThan", formula=["-1.96"], fill=HIT_FILL))

    chart = BarChart()
    chart.type = "col"
    chart.title = f"{label}: firm-years per bin (width {width:g})"
    chart.y_axis.title = "firm-years"
    chart.x_axis.title = "scaled value (bin midpoint)"
    chart.gapWidth = 8
    chart.legend = None
    chart.height, chart.width = 9.5, 22
    vals = Reference(ws, min_col=4, min_row=hdr_row, max_row=last)
    cats = Reference(ws, min_col=3, min_row=first, max_row=last)
    chart.add_data(vals, titles_from_data=True)
    chart.set_categories(cats)
    s = chart.series[0]
    s.graphicalProperties.solidFill = BLUE
    s.graphicalProperties.line.solidFill = "FCFCFB"
    for idx in (below_r - first, above_r - first):
        pt = DataPoint(idx=idx)
        pt.graphicalProperties.solidFill = ORANGE
        pt.graphicalProperties.line.solidFill = "FCFCFB"
        s.dPt.append(pt)
    chart.x_axis.number_format = "0.000"
    chart.x_axis.tickLblSkip = max(1, nb // 10)
    ws.add_chart(chart, "L4")

    ws.freeze_panes = f"A{first}"
    _autowidth(ws, {1: 11, 2: 11, 3: 11, 4: 9, 5: 10, 6: 9, 7: 11, 8: 9, 9: 18, 10: 16})
    ws.sheet_properties.tabColor = ORANGE if "CFO" in title else BLUE
    ws._focal = (last + 4, last + 5)  # noqa: SLF001 -- used by the summary sheet
    return title


def build_table_sheet(wb: Workbook, title: str, frame: pd.DataFrame, note: str,
                      z_cols: tuple[str, ...] = ()) -> None:
    ws = wb.create_sheet(title)
    ws["A1"] = note
    ws["A1"].font = Font(italic=True, color=MUTED, size=9)
    ws.append([])
    ws.append(list(frame.columns))
    _style_header(ws, 3, len(frame.columns))
    for row in frame.itertuples(index=False):
        ws.append([None if (isinstance(v, float) and np.isnan(v)) else v for v in row])
    for name in z_cols:
        if name in frame.columns:
            c = get_column_letter(list(frame.columns).index(name) + 1)
            rng = f"{c}4:{c}{len(frame) + 3}"
            ws.conditional_formatting.add(rng, CellIsRule(operator="greaterThan", formula=["1.96"], fill=HIT_FILL))
            ws.conditional_formatting.add(rng, CellIsRule(operator="lessThan", formula=["-1.96"], fill=HIT_FILL))
            for r in range(4, len(frame) + 4):
                ws[f"{c}{r}"].number_format = "0.00"
    for name in frame.columns:
        if name.startswith("p_") or name.startswith("expected"):
            c = get_column_letter(list(frame.columns).index(name) + 1)
            for r in range(4, len(frame) + 4):
                ws[f"{c}{r}"].number_format = "0.000" if name.startswith("p_") else "0.0"
    ws.freeze_panes = "A4"
    widths = {i + 1: (min(60, max(12, frame[c].astype(str).str.len().max() + 2)) if frame[c].dtype == object else 12)
              for i, c in enumerate(frame.columns)}
    _autowidth(ws, widths)


def build_summary(wb: Workbook, hist_sheets: list[tuple[str, float, tuple[int, int]]],
                  panel: pd.DataFrame, last_row: str | None) -> None:
    ws = wb.create_sheet("Summary", 0)
    ws.sheet_properties.tabColor = INK
    ws["A1"] = "Earnings discontinuity at zero — dashboard"
    ws["A1"].font = Font(bold=True, size=16, color=INK)
    ws["A2"] = ("Do public companies report too few small losses and too many small profits? "
                "Every number below is a live formula over the Panel sheet.")
    ws["A2"].font = Font(color=MUTED, size=10)

    ws["A4"] = "Sample"; ws["A4"].font = Font(bold=True, size=12)
    if last_row is not None:
        rows = [
            ("Firm-years after filters", f"=COUNTA(Panel!A2:A{last_row})", "#,##0"),
            ("Distinct firms", f"=SUM(Panel!O2:O{last_row})", "#,##0"),
            ("First fiscal year", f"=MIN(Panel!D2:D{last_row})", "0"),
            ("Last fiscal year", f"=MAX(Panel!D2:D{last_row})", "0"),
            ("Firm-years inside |ROA| ≤ 0.10", "='ROA_0.005'!D" + str(hist_sheets[1][2][0] - 2), "#,##0"),
            ("Median lagged assets (USD)", f"=MEDIAN(Panel!G2:G{last_row})", "#,##0"),
            ("Median ROA", f"=MEDIAN(Panel!K2:K{last_row})", "0.0000"),
            ("Share of firm-years with a loss", f'=COUNTIF(Panel!F2:F{last_row},"<0")/COUNT(Panel!F2:F{last_row})', "0.0%"),
        ]
    else:  # Sheets edition: sample facts as values from the pipeline
        loss_share = float((panel["net_income"] < 0).mean())
        rows = [
            ("Firm-years after filters", len(panel), "#,##0"),
            ("Distinct firms", int(panel["firm_id"].nunique()), "#,##0"),
            ("First fiscal year", int(panel["fiscal_year"].min()), "0"),
            ("Last fiscal year", int(panel["fiscal_year"].max()), "0"),
            ("Firm-years inside |ROA| ≤ 0.10", "='ROA_0.005'!D" + str(hist_sheets[1][2][0] - 2), "#,##0"),
            ("Median lagged assets (USD)", float(panel["assets_lag"].median()), "#,##0"),
            ("Median ROA", float(panel["roa"].median()), "0.0000"),
            ("Share of firm-years with a loss", loss_share, "0.0%"),
        ]
    for i, (label, formula, fmt) in enumerate(rows, start=5):
        ws.cell(row=i, column=1, value=label)
        ws.cell(row=i, column=2, value=formula).number_format = fmt

    r0 = 5 + len(rows) + 1
    ws.cell(row=r0, column=1, value="Main test — net income / beginning-of-year total assets").font = Font(bold=True, size=12)
    hdr = ["bin width", "N in window", "below zero: count", "below: expected", "below: z", "below: p",
           "above zero: count", "above: expected", "above: z", "above: p"]
    for i, h in enumerate(hdr, start=1):
        ws.cell(row=r0 + 1, column=i, value=h)
    _style_header(ws, r0 + 1, len(hdr))
    for k, (name, width, (b, a)) in enumerate(hist_sheets[:3]):
        r = r0 + 2 + k
        q = f"'{name}'"
        ws.cell(row=r, column=1, value=width).number_format = "0.0000"
        ws.cell(row=r, column=2, value=f"={q}!D{b - 2}").number_format = "#,##0"
        ws.cell(row=r, column=3, value=f"={q}!D{b}")
        ws.cell(row=r, column=4, value=f"={q}!E{b}").number_format = "0.0"
        ws.cell(row=r, column=5, value=f"={q}!H{b}").number_format = "0.00"
        ws.cell(row=r, column=6, value=f"={q}!I{b}").number_format = "0.000"
        ws.cell(row=r, column=7, value=f"={q}!D{a}")
        ws.cell(row=r, column=8, value=f"={q}!E{a}").number_format = "0.0"
        ws.cell(row=r, column=9, value=f"={q}!H{a}").number_format = "0.00"
        ws.cell(row=r, column=10, value=f"={q}!I{a}").number_format = "0.000"
    for c in ("E", "I"):
        rng = f"{c}{r0 + 2}:{c}{r0 + 4}"
        ws.conditional_formatting.add(rng, CellIsRule(operator="greaterThan", formula=["1.96"], fill=HIT_FILL))
        ws.conditional_formatting.add(rng, CellIsRule(operator="lessThan", formula=["-1.96"], fill=HIT_FILL))

    r1 = r0 + 6
    ws.cell(row=r1, column=1, value="Placebo — cash flow from operations, same denominator").font = Font(bold=True, size=12)
    for i, h in enumerate(hdr, start=1):
        ws.cell(row=r1 + 1, column=i, value=h)
    _style_header(ws, r1 + 1, len(hdr))
    name, width, (b, a) = hist_sheets[3]
    q = f"'{name}'"
    r = r1 + 2
    ws.cell(row=r, column=1, value=width).number_format = "0.0000"
    ws.cell(row=r, column=2, value=f"={q}!D{b - 2}").number_format = "#,##0"
    ws.cell(row=r, column=3, value=f"={q}!D{b}")
    ws.cell(row=r, column=4, value=f"={q}!E{b}").number_format = "0.0"
    ws.cell(row=r, column=5, value=f"={q}!H{b}").number_format = "0.00"
    ws.cell(row=r, column=6, value=f"={q}!I{b}").number_format = "0.000"
    ws.cell(row=r, column=7, value=f"={q}!D{a}")
    ws.cell(row=r, column=8, value=f"={q}!E{a}").number_format = "0.0"
    ws.cell(row=r, column=9, value=f"={q}!H{a}").number_format = "0.00"
    ws.cell(row=r, column=10, value=f"={q}!I{a}").number_format = "0.000"
    for c in ("E", "I"):
        ws.conditional_formatting.add(f"{c}{r}", CellIsRule(operator="greaterThan", formula=["1.96"], fill=HIT_FILL))
        ws.conditional_formatting.add(f"{c}{r}", CellIsRule(operator="lessThan", formula=["-1.96"], fill=HIT_FILL))

    r2 = r1 + 4
    ws.cell(row=r2, column=1, value="How to read this").font = Font(bold=True, size=12)
    notes = [
        "The hypothesis predicts a DEFICIT just below zero (negative z) and a SURPLUS just above (positive z).",
        "Cells shaded yellow are |z| > 1.96, i.e. significant at the 5% level. Read both sides together, never one alone.",
        ("Every histogram sheet recomputes from the Panel sheet with COUNTIFS. Edit the panel and the charts move."
         if last_row is not None else
         "Bin counts are exported from the Python pipeline; expected counts, variances, z and p are computed here."),
        "Zero always sits on a bin edge: every edge is an integer multiple of the bin width.",
        "The Robustness sheet holds the denominator, size-tercile and size-floor checks from the notebooks.",
    ]
    for i, t in enumerate(notes, start=r2 + 1):
        ws.cell(row=i, column=1, value="•  " + t).font = Font(color=INK, size=10)
    ws.column_dimensions["A"].width = 44
    for c in "BCDEFGHIJ":
        ws.column_dimensions[c].width = 15


def main() -> None:
    panel = pd.read_parquet(DATA / "panel.parquet")
    robustness = pd.read_csv(DATA / "robustness_results.csv")
    drop_log = pd.read_csv(DATA / "drop_log.csv")

    wb = Workbook()
    wb.remove(wb.active)

    cols = build_panel_sheet(wb, panel)
    last_row = cols["_last_row"]

    hist_sheets = []
    for width in (0.0025, 0.005, 0.01):
        name = build_hist_sheet(wb, f"ROA_{width:g}", cols["ROA"], last_row, width,
                                "Net income / beginning-of-year total assets")
        hist_sheets.append((name, width, wb[name]._focal))
    name = build_hist_sheet(wb, "CFO_0.005", cols["CFO_over_assets_lag"], last_row, 0.005,
                            "Placebo: cash flow from operations / beginning-of-year total assets")
    hist_sheets.append((name, 0.005, wb[name]._focal))

    build_table_sheet(wb, "Robustness", robustness,
                      "All four robustness checks (spec section 6). Yellow = |z| > 1.96. Source: data/robustness_results.csv",
                      z_cols=("z_below", "z_above"))
    build_table_sheet(wb, "Exclusion_log", drop_log,
                      "Every sample filter, in the order applied, with the rows it removed. Source: data/drop_log.csv")

    build_summary(wb, hist_sheets, panel, last_row)

    # Panel goes last in tab order; it is the engine, not the front page.
    wb.move_sheet("Panel", offset=len(wb.sheetnames))
    OUT.parent.mkdir(exist_ok=True)
    wb.save(OUT)
    print(f"wrote {OUT.relative_to(ROOT)}  sheets={wb.sheetnames}")


SHEETS_OUT = ROOT / "dashboard" / "earnings_discontinuity_dashboard_sheets.xlsx"


def main_sheets_edition() -> None:
    """Compact workbook for Google Sheets: counts as values, statistics as formulas."""
    from .binning import histogram
    from .panel import restrict_window

    panel = pd.read_parquet(DATA / "panel.parquet")
    robustness = pd.read_csv(DATA / "robustness_results.csv")
    drop_log = pd.read_csv(DATA / "drop_log.csv")

    wb = Workbook()
    wb.remove(wb.active)
    hist_sheets = []
    roa, _ = restrict_window(panel, "roa")
    for width in (0.0025, 0.005, 0.01):
        counts = histogram(roa["roa"], width)["count"].tolist()
        name = build_hist_sheet(wb, f"ROA_{width:g}", None, None, width,
                                "Net income / beginning-of-year total assets", counts=counts)
        hist_sheets.append((name, width, wb[name]._focal))
    cfo, _ = restrict_window(panel, "cfo_at")
    counts = histogram(cfo["cfo_at"], 0.005)["count"].tolist()
    name = build_hist_sheet(wb, "CFO_0.005", None, None, 0.005,
                            "Placebo: cash flow from operations / beginning-of-year total assets", counts=counts)
    hist_sheets.append((name, 0.005, wb[name]._focal))

    build_table_sheet(wb, "Robustness", robustness,
                      "All four robustness checks (spec section 6). Yellow = |z| > 1.96. Source: data/robustness_results.csv",
                      z_cols=("z_below", "z_above"))
    build_table_sheet(wb, "Exclusion_log", drop_log,
                      "Every sample filter, in the order applied, with the rows it removed. Source: data/drop_log.csv")
    build_summary(wb, hist_sheets, panel, None)
    SHEETS_OUT.parent.mkdir(exist_ok=True)
    wb.save(SHEETS_OUT)
    print(f"wrote {SHEETS_OUT.relative_to(ROOT)}  sheets={wb.sheetnames}  "
          f"{SHEETS_OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    import sys
    if "--sheets" in sys.argv:
        main_sheets_edition()
    else:
        main()
