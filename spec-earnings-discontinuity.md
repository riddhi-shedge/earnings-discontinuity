# Spec: Do Companies Bend Earnings to Avoid Reporting a Loss?

**Type:** Data analysis
**Status:** Not started
**One-line pitch:** Test whether the distribution of scaled net income across public companies shows an unnatural discontinuity at zero — too few small losses, too many small profits — and whether that gap survives robustness checks.

---

## 1. The question

If reported earnings were unmanaged, the distribution of net income across thousands of firms should be smooth. There is no economic reason for a sharp break at exactly zero.

But managers near a small loss have discretion: timing a write-off, recognizing revenue slightly early, adjusting a reserve estimate. If that discretion gets used to cross zero, the distribution should show a **notch** — a deficit of firms just below zero and a surplus just above.

**Hypothesis (H1):** The observed frequency of firms in the bin immediately below zero is lower than predicted by neighboring bins.

**Null (H0):** The distribution is smooth through zero; any apparent notch is within sampling variation.

---

## 2. Background you should read before starting

Two papers frame this entire project. Read both — the second is what makes your version defensible.

- **Burgstahler & Dichev (1997)**, "Earnings management to avoid earnings decreases and losses," *Journal of Accounting and Economics*. The original finding. This is what you are replicating.
- **Durtschi & Easton (2005)**, "Earnings management? The shapes of the frequency distributions of earnings metrics are not evidence ipso facto," *Journal of Accounting Research*. The critique: the discontinuity can arise from **scaling and sample selection artifacts** rather than manipulation.

Verify these citations before quoting them in a writeup — I'm working from memory on the details.

**Why the critique matters to you:** it converts this from "student replicates known result" into "student understands why the known result is contested." That is a much better interview conversation, and the robustness checks in section 6 exist specifically to address it.

---

## 3. Data

**Preferred source:** SEC's structured financial statement data sets, derived from XBRL filings. Flat files, no HTML parsing. Check the current file format and field names on SEC's site before writing loader code — the schema has changed over time and I don't want you building against a stale assumption.

**Fallback / prototype source:** `yfinance`, pulling annual income statements and balance sheets for a list of tickers. Faster to stand up, smaller sample, some gaps. Good enough to see whether the effect appears at all.

**Start with the fallback.** Get a histogram out of 300 tickers in one evening before committing to the larger pipeline.

### Fields needed

| Field | Use |
|---|---|
| Net income (annual) | Numerator |
| Total assets (annual) | Denominator, lagged one year |
| Revenue | Alternate denominator for robustness |
| Market value of equity | Alternate denominator for robustness |
| Cash flow from operations | Placebo test (see 6.4) |
| SIC or sector code | Sample filtering |
| Fiscal year | Panel structure, time-trend checks |

### Sample filters

Apply these and **document each one with its rationale** — filter choices are exactly where the Durtschi–Easton critique bites.

1. Drop financial firms (SIC 6000–6999). Their balance sheets are structurally different and total assets means something else for a bank.
2. Drop utilities (SIC 4900–4949) if you want to follow convention. Optional; note it either way.
3. Drop firm-years with missing or non-positive total assets.
4. Drop firms below a small size floor — but **test sensitivity to this floor**, because tiny-denominator firms produce extreme scaled values and are a known source of artifacts.
5. Restrict the analysis window to |scaled earnings| ≤ 0.10. You are studying behavior near zero, not the tails.
6. Decide and state whether you keep multiple years per firm. Pooling firm-years inflates your N but violates independence; the simplest defensible choice is to pool and acknowledge it.

---

## 4. Variable construction

```
ROA_it = NetIncome_it / TotalAssets_i,t-1
```

**Use lagged (beginning-of-year) total assets.** End-of-year assets already reflect the current year's earnings, which puts the thing you are measuring into the denominator.

---

## 5. Method

### 5.1 Look before you test

Histogram of `ROA` over the ±0.10 window, fine bins. **Plot it and look at it before running any statistics.** If the notch exists you will see it. If you cannot see it, no test will rescue the project — and that is itself a finding worth reporting.

### 5.2 Bin width

Bin width is a real analytical choice, not a plotting detail. Too wide and you smooth the notch away; too narrow and every bin is noise.

Start around **0.005** of lagged assets. Then produce the same test at 0.0025, 0.005, and 0.01 and report all three. A result that only appears at one bin width is not a result.

Make sure zero falls on a **bin boundary**, not inside a bin. If zero sits mid-bin you have blurred the exact thing you are measuring.

### 5.3 The test

For each bin *i*, predict its count from its immediate neighbors:

```
expected_i = (count_{i-1} + count_{i+1}) / 2
```

Then compare observed to expected for the bin just below zero. Under a smoothness null, the difference is approximately normal with variance derivable from a binomial argument; a standardized difference gives you a z-statistic. A chi-square goodness-of-fit across all bins in the window works too and is the more familiar tool from Stats 20.

Report the test statistic for **both** the bin immediately below zero and the bin immediately above. The prediction is a deficit below and a surplus above — finding only one of the two is weaker evidence and worth saying plainly.

---

## 6. Robustness checks

This section is what separates a good version of this project from a mediocre one. Run all four.

### 6.1 Alternate denominators
Rerun with market value of equity and with revenue as the scalar. If the notch survives all three, the scaling-artifact explanation weakens considerably. If it vanishes under one, that is a genuine and reportable finding.

### 6.2 Size subsamples
Split into terciles by total assets and rerun. The artifact story predicts the notch concentrates in small firms; the management story does not make that prediction as strongly.

### 6.3 Size-floor sensitivity
Rerun the main test at several minimum-asset thresholds. Show whether the result depends on including the smallest firms.

### 6.4 Cash-flow placebo
Run the identical test on **cash flow from operations** scaled the same way. CFO is much harder to manipulate through accrual timing. If net income shows a notch and CFO does not, that is meaningful support for the management interpretation. If both show a notch, suspect a scaling artifact.

This placebo is the single highest-value addition to the project. It is a clean identification argument that costs you one extra column.

---

## 7. What a null result looks like

Plan for this now so you are not tempted to torture the data later.

If the notch is absent or fails robustness, the project is still complete. Write it as a **measurement study**: here is the distribution of scaled earnings near zero in [period], here is how it responds to bin width, scaling choice, and sample filters, here is what would have to be true for the classical result to hold in this sample. Explicitly state that you did not find evidence of X, rather than quietly changing the question.

Overclaiming is the way this project goes wrong. A clean null, honestly reported, is a stronger artifact than a p-hacked positive.

---

## 8. Deliverables

1. `data/` — loader scripts and a cached parquet of the cleaned panel (do not commit raw bulk downloads)
2. `notebooks/01_explore.ipynb` — distribution plots, sanity checks
3. `notebooks/02_main_test.ipynb` — the discontinuity test
4. `notebooks/03_robustness.ipynb` — sections 6.1–6.4
5. `figures/` — the main histogram, at publication quality, with zero clearly marked
6. `README.md` — question, data, method, results, limitations, references
7. A short writeup (2–3 pages) suitable for attaching to an application

The main histogram is your headline artifact. Make it good: clear axis labels, the zero boundary marked, bin width stated in the caption, sample size stated.

---

## 9. Build phases

| Phase | Deliverable | Rough effort |
|---|---|---|
| 0 | `yfinance` pull for ~300 tickers, crude histogram | 1 evening |
| 1 | Decide: does the effect look present? Commit to full data source or not | — |
| 2 | Full data pipeline + documented sample filters | 2–3 evenings |
| 3 | Main test, all three bin widths | 1–2 evenings |
| 4 | Robustness checks 6.1–6.4 | 2–3 evenings |
| 5 | Figures + README + writeup | 2 evenings |

---

## 10. Pitfalls

- **Using end-of-year assets as the denominator.** Contaminates the measure. Lag it.
- **Zero falling inside a bin.** Blurs the discontinuity you are testing for.
- **Reporting one bin width.** Looks like you picked the flattering one.
- **Cherry-picking the sample window.** Fix filters before looking at results.
- **Claiming causation.** The test shows a distributional anomaly. "Consistent with earnings management" is the defensible phrasing; "proves managers manipulate earnings" is not.
- **Silently dropping firms.** Every exclusion goes in the README with a count.

---

## 11. Stretch ideas (only after the core ships)

- Time trend: has the notch changed across decades, or around SOX?
- Auditor effects: does the notch differ for Big Four vs non-Big Four clients?
- A second threshold: the same test around **zero earnings change** year-over-year (the other half of the original paper)
- Industry variation

---

## 12. Resume bullets (draft — fill in real numbers after building)

- Tested [N] firm-year observations of scaled net income for a discontinuity at zero, replicating a documented earnings-management result on current SEC filing data and finding [result] at the p < [X] level
- Built the analysis to address a known methodological critique, validating the result across three scaling denominators, three bin widths, and size subsamples, plus a cash-flow-from-operations placebo test
- Constructed and documented the sample from [source], applying industry and size filters with each exclusion reported
