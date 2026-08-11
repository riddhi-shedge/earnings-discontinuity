"""Export every figure as a vector PDF, plus one combined PDF of all figures.

Figures are re-rendered from the data rather than converted from PNG, so the output
is true vector art -- text stays selectable and the plots stay sharp at any zoom.

    python -m src.export_pdf
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402

from .binning import BIN_WIDTHS  # noqa: E402
from .discontinuity import run_all_widths  # noqa: E402
from .panel import apply_filters, build_sec_panel, restrict_window  # noqa: E402
from .plotting import (bin_width_panel, headline_histogram, placebo_panel,  # noqa: E402
                       z_comparison)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FIGS = ROOT / "figures"
PDF_DIR = FIGS / "pdf"

SOURCE = "SEC Financial Statement Data Sets (10-K filings)"


def build_all() -> list[tuple[str, plt.Figure]]:
    """Every figure in the report, in the order they appear in the README."""
    panel = pd.read_parquet(DATA / "panel.parquet")
    window, _ = restrict_window(panel, "roa")
    period = f"fiscal years {int(window.fiscal_year.min())}-{int(window.fiscal_year.max())}"
    n_firms = window["firm_id"].nunique()

    figures: list[tuple[str, plt.Figure]] = []

    fig, _ = headline_histogram(
        window["roa"], 0.005, source=SOURCE, n_firms=n_firms, period=period,
        title="Distribution of scaled net income around zero")
    figures.append(("headline_histogram", fig))

    figures.append(("bin_width_panel",
                    bin_width_panel(window["roa"], BIN_WIDTHS, source=SOURCE)))

    # 6.1 alternate denominators
    rows = []
    for label, col in [("net income / lagged assets", "roa"),
                       ("net income / revenue", "ni_revenue"),
                       ("net income / lagged book equity", "ni_equity_lag")]:
        sub, _ = restrict_window(panel, col)
        res = run_all_widths(sub[col], label=label)
        res["denominator"] = label
        rows.append(res)
    denom = pd.concat(rows, ignore_index=True)
    figures.append(("robustness_denominators",
                    z_comparison(denom[denom.bin_width == 0.005], label_col="denominator",
                                 title="6.1  Does the notch survive a change of scalar?",
                                 subtitle=f"Bin width 0.005. Source: {SOURCE}")))

    # 6.2 size terciles
    terciles = window.copy()
    terciles["tercile"] = pd.qcut(terciles["assets_lag"], 3,
                                  labels=["small", "medium", "large"])
    rows = []
    for name in ["small", "medium", "large"]:
        res = run_all_widths(terciles[terciles.tercile == name]["roa"], label=name)
        res["tercile"] = name
        rows.append(res)
    size = pd.concat(rows, ignore_index=True)
    figures.append(("robustness_size_terciles",
                    z_comparison(size[size.bin_width == 0.005], label_col="tercile",
                                 title="6.2  Is the notch concentrated in small firms?",
                                 subtitle="Terciles of beginning-of-year total assets. Bin width 0.005.")))

    # 6.3 size-floor sensitivity
    base = build_sec_panel(pd.read_parquet(DATA / "sec_raw_panel.parquet"))
    rows = []
    for floor in [0, 1e6, 10e6, 50e6, 100e6, 500e6]:
        clean, _ = apply_filters(base, size_floor=floor, fiscal_years=(2016, 2025))
        sub, _ = restrict_window(clean, "roa")
        res = run_all_widths(sub["roa"], label=f"${floor:,.0f}")
        res["size_floor"] = f"assets >= ${floor / 1e6:,.0f}m"
        rows.append(res)
    floors = pd.concat(rows, ignore_index=True)
    figures.append(("robustness_size_floor",
                    z_comparison(floors[floors.bin_width == 0.005], label_col="size_floor",
                                 title="6.3  Does the result depend on including the smallest firms?",
                                 subtitle="Full filter chain re-run at each floor. Bin width 0.005.")))

    # 6.4 cash-flow placebo
    cfo_win, _ = restrict_window(panel, "cfo_at")
    figures.append(("cfo_placebo",
                    placebo_panel(window["roa"], cfo_win["cfo_at"], 0.005, source=SOURCE)))

    placebo = pd.concat([
        run_all_widths(window["roa"], label="net income").assign(measure="net income"),
        run_all_widths(cfo_win["cfo_at"], label="CFO").assign(measure="cash flow from operations"),
    ], ignore_index=True)
    figures.append(("robustness_placebo_z",
                    z_comparison(placebo[placebo.bin_width == 0.005], label_col="measure",
                                 title="6.4  Cash-flow placebo",
                                 subtitle="Identical test, identical denominator. Bin width 0.005.")))

    # Phase 0 prototype, if the yfinance pull exists
    yf_path = DATA / "panel_yfinance.parquet"
    if yf_path.exists():
        yf_panel = pd.read_parquet(yf_path)
        yf_window, _ = restrict_window(yf_panel, "roa")
        fig, _ = headline_histogram(
            yf_window["roa"], 0.005,
            source="yfinance (300-ticker prototype sample)",
            n_firms=yf_window["firm_id"].nunique(),
            period=f"fiscal years {int(yf_window.fiscal_year.min())}-{int(yf_window.fiscal_year.max())}",
            title="Phase 0 prototype: scaled net income, 300-ticker yfinance sample")
        figures.append(("phase0_yfinance_histogram", fig))

    return figures


def main() -> None:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    figures = build_all()

    for name, fig in figures:
        fig.savefig(PDF_DIR / f"{name}.pdf", bbox_inches="tight")
        print(f"wrote figures/pdf/{name}.pdf")

    combined = FIGS / "all_figures.pdf"
    with PdfPages(combined) as pdf:
        for _, fig in figures:
            pdf.savefig(fig, bbox_inches="tight")
        meta = pdf.infodict()
        meta["Title"] = "Earnings discontinuity at zero -- all figures"
        meta["Subject"] = ("Discontinuity test on 16,018 SEC firm-years, "
                           "fiscal years 2016-2025")
    print(f"wrote {combined.relative_to(ROOT)} ({len(figures)} pages)")

    for _, fig in figures:
        plt.close(fig)


if __name__ == "__main__":
    main()
