# Earnings Discontinuity Analysis — Project Guide

### Everything needed to explain and defend this project

---

**The result in one paragraph.** I tested a famous accounting claim on current SEC data:
that companies bend their earnings to avoid reporting a small loss, which should show up as
a gap in the distribution of profits at exactly zero. In 16,018 company-years the gap goes
in the predicted direction at every bin width but is never statistically significant. Two
robustness findings matter more than the headline: the result appears under one scaling
choice and not others, and a placebo test on cash flow — which cannot be managed through
accounting judgment — shows a *larger, opposite-signed* break. So the honest conclusion is
a null, and the interesting contribution is showing how much the classical result depends
on choices usually made in passing.

**How this is organised.** Parts 1–6 are the project in build order. Part 7 covers
limitations and phrasing. Part 8 is the code. Part 9 is 26 anticipated questions with
answers — the section to read if time is short. A numbers cheat sheet and glossary close it
out. Terms are defined the first time they appear, marked like this:

> **Term** — its definition.

---

# PART 1 — BACKGROUND

## 1. What companies report

Three financial statements, published annually.

| Statement | Answers | Covers |
|---|---|---|
| **Income statement** (P&L) | How much did it earn? | A period |
| **Balance sheet** | What does it own and owe? | One instant |
| **Cash flow statement** | How much cash moved? | A period |

Four numbers from them are used here.

> **Net income** — bottom line of the income statement: revenue minus every expense
> including interest and tax. Positive is a profit, negative a loss. *The number at the
> centre of this project.*

> **Total assets** — from the balance sheet: everything the company owns that has value
> (cash, inventory, factories, patents, money owed to it). The standard measure of size.

> **Revenue** — top line of the income statement: money from sales before any costs. A
> company can have huge revenue and still lose money.

> **Cash flow from operations (CFO)** — cash the actual business generated, excluding money
> raised from investors or spent on acquisitions.

One structural fact matters later. A balance sheet always balances:

```
Assets = Liabilities + Shareholders' equity
```

> **Liabilities** — what the company owes: loans, bonds, unpaid bills.

> **Shareholders' equity** (book equity) — assets minus liabilities; what would be left for
> owners after paying every debt.

**Profit flows into equity.** Unpaid-out profit lands in *retained earnings*, inside equity,
inside assets:

```
This year's profit → retained earnings → equity → total assets
```

That chain is why the *timing* of the assets figure is the most important measurement
decision in the project (§11).

> **Fiscal year** — a company's own 12-month reporting period. Need not be the calendar
> year: Apple's ends in September, many retailers' in January. I always compare a company's
> fiscal year to its own prior fiscal year.

## 2. Accruals, and why cash flow is different

> **Accrual accounting** — record revenue when *earned* and expenses when *incurred*,
> regardless of when cash moves. Required for public companies.

Example: a company delivers software in December 2024 and is paid in February 2025. Cash
accounting counts the sale in 2025; accrual accounting counts it in 2024, when the work
happened. Accrual is more informative — but it requires estimates, and estimates require
judgment.

> **Accrual** — an entry recording revenue or expense before the cash moves. The gap between
> profit and cash is made of accruals.

Four places judgment legitimately enters:

- **Bad debt allowance** — some credit customers will never pay. Is the provision 2% or 3%?
- **Warranty reserve** — estimating today what future repairs will cost.
- **Depreciation life** — a $10m machine over 8 years is $1.25m/year; over 12 years it is
  $833k. A $417k annual difference from one judgment.
- **Write-off timing** — when the evidence becomes conclusive enough can fall either side of
  a year end.

None of these are cheating. Auditors sign off on ranges, not single correct answers.

**The contrast that makes this project work:**

| | Net income | Cash flow from operations |
|---|---|---|
| Contains accruals | Yes, substantially | No |
| Movable by revising an estimate | Yes | **No** |
| Movable by real operational action | Yes | Yes, at real cost |

You cannot change the bank balance by revising a warranty estimate. **This asymmetry is the
entire basis of the placebo test in §20.**

## 3. Earnings management, and why zero

> **Earnings management** — using discretion available *within* accounting rules to steer
> reported results. Legal. Not fraud.

| | Earnings management | Fraud |
|---|---|---|
| Within the rules | Yes | No |
| Example | 3% bad-debt provision rather than 2% | Recording a sale that never happened |
| Legal | Yes | No |

Zero has no economic meaning — a company earning $1 is not healthier than one losing $1.
But it has enormous contractual and psychological meaning:

- **Headlines.** "Posts loss" is a story; "posts small profit" is not.
- **Debt covenants.** Loan agreements often require profitability; breaching one can let a
  lender demand immediate repayment.
- **Bonuses.** Many schemes pay out only if the company is profitable.
- **Loss aversion.** People treat losses as worse than equivalent gains.

**The testable chain:** zero matters to managers → accruals give them discretion → some may
use it to cross zero → if enough do, it shows in the shape of the distribution across
thousands of companies. You cannot see one company's decision, but you can ask whether the
aggregate pattern looks natural.

## 4. Distributions and bins

> **Distribution** — the pattern of how often each value occurs across a group.

> **Histogram** — a chart of a distribution: split the range into equal **bins**, count what
> falls in each, draw bars.

> **Bin** — one interval, written `[left, right)`. The left edge belongs to the bin, the
> right edge to the next one. Consequence here: a company reporting *exactly* zero lands in
> the bin **above** zero. Breaking even is not a loss.

**Why we expect smoothness.** Business conditions vary continuously, so the count of
companies earning 0.1% should be close to the count earning 0.2%. A sudden break demands
explanation, because economics does not jump.

**Bin width is a real decision, not a display setting.**

- *Too wide* — the affected companies get mixed with thousands of unaffected ones and the
  signal is averaged away.
- *Too narrow* — each bin holds a handful of companies, so 3 versus 7 looks dramatic when it
  is just noise.

There is no single correct width, so **I run every test at three: 0.0025, 0.005, 0.01, and
always report all three.** That removes the question "did you pick the flattering one?" — and
it turned out to be diagnostic, because in §20 an effect *grows* with bin width, which is
itself evidence about its cause.

**Zero must sit on a bin edge.** A bin running −0.25% to +0.25% would contain both the
deficit below zero and the surplus above, which cancel inside the same bar — destroying the
signal before measuring it. Every bin edge in my code is an integer multiple of the bin
width, so zero is always a boundary. A unit test enforces this, including at awkward widths
like 0.003 where the window does not divide evenly.

---

# PART 2 — THE QUESTION AND THE DEBATE

## 5. The hypothesis

Line every company up by profit as a fraction of its size and count them into bins.

- **If nobody manages anything**, the distribution passes smoothly through zero.
- **If some managers push small losses into small profits**, there is a *deficit* just below
  zero and a *surplus* just above.

> **Notch** (discontinuity) — a sharp break in an otherwise smooth distribution. Here, the
> dip-then-bump at exactly zero.

> **Null hypothesis (H₀)** — the "nothing unusual" default: the distribution is smooth and
> any apparent notch is random variation.

> **Alternative (H₁)** — the bin below zero is genuinely thinner than its neighbours predict,
> and the bin above genuinely thicker.

Two commitments this forces, both of which I kept:

1. **Report both sides, every time.** The prediction is a deficit below *and* a surplus
   above. Reporting only the better-looking side would overstate the finding. In my results
   the two sides behave quite differently, so this matters.
2. **The direction is predicted in advance.** A large effect pointing the *wrong* way is not
   support. §20 turns on exactly that distinction.

## 6. The two papers

**Burgstahler & Dichev (1997)**, *Journal of Accounting and Economics* 24(1), 99–126.
Examined US companies 1976–1994, found the notch, read it as earnings management to avoid
losses. One of the most-cited results in empirical accounting. They also tested a second
threshold — zero *change* in earnings year-over-year — which I did not test (§26).

**Durtschi & Easton (2005)**, *Journal of Accounting Research* 43(4), 557–592. The critique,
and the reason this project is more than a replication.

Their argument starts from something unavoidable: you cannot compare raw profit across
companies, because $1m means different things to a corner shop and to Apple. Every study
therefore **divides profit by something**. They showed that the act of dividing, plus the
choice of which companies end up in the sample, **can manufacture a notch with no manager
involved.**

One mechanism, simplified. Small companies are less profitable and more variable than large
ones. Dividing a modest profit by a huge asset base gives a ratio near zero; dividing by a
tiny asset base gives a ratio far from zero. So the region near zero fills with large stable
companies and the tails with small volatile ones. **The sample near zero is a different
population from the sample further out**, and the join between two populations with
different shapes can produce a kink. Sample selection compounds it: requiring complete data
removes companies non-randomly, and if the removal rate differs either side of zero, the
shape shifts.

**This dictates the whole design.** The filters in §9 exist because selection is half the
critique. The four robustness checks in §17–20 each target a specific piece of it.

*Both citations were verified against the publishers, not quoted from memory. A longer 2009
follow-up by the same authors exists; I mention it in the README but do not rely on it,
having not verified its pages.*

---

# PART 3 — DATA AND SAMPLE

## 7. Source and files

> **SEC** — the US regulator of public companies. All filings go to its public **EDGAR**
> database, free to anyone.

> **10-K** — the audited annual report. **10-Q** — the unaudited quarterly report.

> **XBRL** — a tagging standard attaching machine-readable labels to every number in a
> filing. Phased in from ~2009. It is what makes this project possible without a data
> licence — and why my data cannot reach earlier periods (§22).

> **SEC Financial Statement Data Sets** — free quarterly ZIPs flattening every XBRL filing
> into tab-separated text, at
> `sec.gov/files/dera/data/financial-statement-data-sets/{YYYY}q{Q}.zip`.

I used **37 quarterly archives, 2017 Q1 – 2026 Q1**. Chose this over a commercial database
because it is free, primary (no vendor has made undocumented decisions), and fully
reproducible by anyone. The cost is coverage starting in 2009.

Each archive holds two files I use:

- **`sub.txt`** — one row per filing: accession number, **CIK** (the SEC's permanent company
  ID, stable across renames — the key I join on), name, SIC industry code, period end, form
  type, filing date.
- **`num.txt`** — one row per reported number: filing, XBRL tag, date, `qtrs`, unit,
  `segments`, `coreg`, value. ~550 MB uncompressed per quarter.

**Three fields need care:**

- `qtrs = 0` is a point-in-time balance-sheet value; `qtrs = 4` is a full year. Getting this
  wrong would mean treating one quarter of profit as a year's.
- `segments` and `coreg` are non-empty for segment or subsidiary breakdowns. **I keep only
  rows where both are blank**, so every figure is a company-level consolidated total.
  Without this I would be mixing totals with regional subtotals.
- `ddate` is rounded to month end, and 52/53-week fiscal years drift, so dates are matched
  by window rather than exactly (§8).

**Why I parsed by hand rather than with `read_csv`.** Three reasons: 20 GB of text total, and
loading a quarter to then filter to six tags wastes most of the work; the free-text
`footnote` field contains quote characters that break naive CSV parsing silently; and the
usual remedy — skipping malformed lines — would drop data without counting it, which is
backwards in a project whose credibility rests on counting every exclusion. Splitting on
tabs and filtering before materialising anything keeps memory flat. **Result: 113,203,537
rows scanned, zero malformed.**

**Tags extracted.** Several concepts have multiple tags in common use, so I take the first
available in a stated priority order:

| Concept | Tags, in priority order |
|---|---|
| Total assets | `Assets` |
| Net income | `NetIncomeLoss`, `ProfitLoss` |
| Revenue | `Revenues`, `RevenueFromContractWithCustomerExcludingAssessedTax`, + 3 older variants |
| Cash flow from ops | `NetCashProvidedByUsedInOperatingActivities`, + continuing-ops variant |
| Equity | `StockholdersEquity`, + variant including non-controlling interests |

Insisting on one tag would lose every company using a newer concept. **Revenue is the
messiest** — five plausible tags, inconsistently used — which is why the revenue-scaled
sample in §17 is a different set of companies, a caveat I raise there.

## 8. Building the panel

> **Panel** — one row per company per year. Each row is a **firm-year**, the unit of
> analysis. "16,018 observations" means 16,018 company-year combinations, not 16,018
> companies.

**Why 10-Ks only — the key data decision.** To compute my measure I need this year's profit
and the assets the company *started* the year with. The obvious approach is to fetch two
filings and join them, which risks missing years, changed year-ends, and silent mismatches.

But accounting rules require a 10-K to show the **comparative balance sheet**: last year's
figures printed beside this year's, in the same audited document, tagged in the same XBRL
submission. So one filing gives me all three of: net income for the year, end-of-year
assets, and **beginning-of-year assets**. No join, no mismatch risk. Quarterly filings do
not provide this, which is why they were excluded despite the volume lost.

**Date matching.** Current year = within ±20 days of period end. Prior year = 330–400 days
before period end. The window is generous enough to absorb a 53-week year and month-end
rounding, tight enough not to grab a figure from two years ago.

**Deduplication.** Amended and transition-period filings can duplicate a firm-year; I keep
the most recent period end. This removed only 4 rows of 31,244 — a safety net that caught
almost nothing, which is the good outcome.

**Caching.** The cleaned panel is saved as **parquet** (a compressed, typed, column-oriented
format) and *committed to the repository*. Raw archives are gitignored. So anyone can clone
and reproduce every number without downloading 2 GB, and the notebooks never touch the SEC.

## 9. The filters

**Why filter:** a bank's balance sheet is not comparable to a manufacturer's, missing data
cannot be measured, and a company with $50k of assets produces ratios that distort
everything.

**Why filtering is dangerous:** every filter is a chance to p-hack.

> **p-hacking** — trying many analytical choices and keeping the most favourable. Inflates
> apparent significance and causes results that fail to replicate.

Three protections: **(1)** filters were fixed before any result existed; **(2)** every
exclusion is *counted*, not described — `apply_filters()` returns the clean panel *and* a
drop log, and a test verifies each step's "before" equals the previous "after"; **(3)** the
one threshold I chose myself is stress-tested at six values (§19).

| Step | Dropped | Remaining | Firms |
|---|---:|---:|---:|
| 0. All 10-K firm-years | — | 57,407 | 10,304 |
| 1. Fiscal years 2016–2025 only | 141 | 57,266 | 10,276 |
| 2. Drop missing industry code | 550 | 56,716 | 10,078 |
| 3. Drop financial firms (SIC 6000–6999) | 14,590 | 42,126 | 7,251 |
| 4. Drop utilities (SIC 4900–4949) | 1,404 | 40,722 | 7,034 |
| 5. Drop missing net income | 703 | 40,019 | 6,979 |
| 6. Drop missing / non-positive lagged assets | 764 | 39,255 | 6,882 |
| 7. Size floor: lagged assets ≥ $10m | 8,011 | 31,244 | 5,366 |
| 8. One filing per firm-year | 4 | **31,240** | **5,366** |

**1. Fiscal-year range.** My download window only fully covers 2016–2025. Outside it are
delinquent filers catching up — fiscal 2014 appears exactly once. One company is not a
cross-section.

**2. Missing SIC.** Needed for the next two filters.

> **SIC code** — a four-digit industry classification. 2834 is pharmaceuticals, 6021 is
> commercial banks.

**3. Financial firms — the largest cut, a quarter of the data.** "Total assets" means
something structurally different for a bank: its assets are its *loan book*, not the
factories and inventory it uses to make money. A bank might hold $100 of assets per $1 of
annual profit; a software company $2. Both are healthy, but the ratio is not comparable.
Critically, per §6, mixing populations with different natural scales is exactly what can
manufacture a shape artifact — so including banks would mean any kink was partly my own
construction. Standard practice, and the count is in the log.

**4. Utilities.** Rate regulation means a regulator effectively sets the return, making
earnings mechanically smooth near a target for reasons unrelated to discretion. Conventional
but genuinely optional; it is a flag in my code and logged either way.

**5. Missing net income.** No numerator, no observation.

**6. Missing or non-positive lagged assets.** Zero assets gives infinity. *Negative* assets
flip the sign — a company with a $5m loss and −$10m of assets computes to +0.5, landing on
the profit side of zero. In a study about which side of zero companies fall on, that is not
a small problem.

**7. Size floor of $10m.** Very small denominators produce extreme ratios ($50k of assets,
$30k loss → −60%), and these are precisely the companies Durtschi and Easton identify as the
artifact source. $10m is small enough to keep genuine small-caps, large enough to remove
shells. **This is the only threshold I chose myself, so §19 re-runs everything at six floors
from $0 to $500m.**

**8. One filing per firm-year.** §8.

## 10. The window, and pooling

**The analysis window.** At test time I restrict to scaled profit within **±10%**: 16,018
firm-years inside, 15,222 outside.

This is *not* a data-quality filter — it states **what is being studied**. A company on
track for a 40% return is not weighing whether to cross into profit. It is reported
separately in the drop log for that reason. It was fixed in advance and is conventional. It
also matters less than it looks: the neighbour test depends only on the *three bins around
zero*, which are identical regardless of where the window ends.

**Pooling.** 31,240 firm-years from 5,366 companies is **5.82 years per company**.

> **Pooling** — treating every firm-year as a separate observation. Violates independence,
> because a company profitable last year is likely profitable this year.

Consequence: **my p-values are somewhat too small** — results look more certain than they
are. I pooled anyway because it is standard in this literature (both framing papers do it),
because keeping one year per company would cut the sample to ~5,400 and destroy the power to
detect anything, and because **the bias runs toward significance while my finding is a null**
— correcting for it would make the null *more* null, not less.

I raise this before being asked, because stating a limitation you could have concealed is
what makes the ones you did not state credible.

---

# PART 4 — MEASUREMENT

## 11. Scaling, and the lagged denominator

**Why divide at all.** Two companies each report $1m of profit: a restaurant chain with $3m
of assets, and Walmart with $250bn. Same number, opposite meanings. Raw profit cannot be
compared, so every study scales.

> **Scaling** — dividing by a measure of size so companies of different sizes are comparable.

> **ROA (return on assets)** — net income ÷ total assets. My main measure.

**Which total assets — the single most important decision in the project.**

The intuitive answer is end-of-year, because that is the headline figure. **That is wrong.**
Recall from §1: `profit → retained earnings → equity → assets`. **End-of-year assets already
contain this year's profit.** Dividing by them puts the measured quantity into its own
denominator.

Watch what that does. A good year means high profit, which inflates the denominator, which
shrinks the ratio. A bad year shrinks assets, which inflates the (negative) ratio. **Both
directions get pulled toward the middle — the distribution is compressed toward zero.** That
is catastrophic for a test about a sharp feature *at* zero: it acts as a smoothing filter
applied exactly where I am looking, and I could not tell a genuinely absent notch from one I
erased myself.

**The fix:** use the assets the company *started* the year with.

```
ROA = net income during year t  ÷  total assets at end of year t−1
```

> **Lagged** — taken from the previous period. Lagged assets = last year's closing balance
> sheet = this year's opening one.

That figure was finalised before this year's profit existed, so it cannot contain it. It
also asks a cleaner question: how much profit came from the resources available at the
start.

**How much it matters, measured rather than assumed:**

| Check | Result |
|---|---|
| Firm-years where beginning = ending assets | **0.02%** |
| Median absolute difference in resulting ROA | **0.0093** |

0.0093 is nearly **two bins wide** at my main width of 0.005. Not a rounding difference — it
would move many companies across the bins the entire test depends on.

**Three protections.** The comparative balance sheet (§8) puts the right number at hand. A
unit test uses a synthetic company with $100 of assets in year 1, $400 in year 2, earning
$20 in year 2, and asserts ROA is 0.20 not 0.05 — so switching to the end-of-year figure
fails immediately. Companion tests confirm a first year has no lag, a *gap* year does not
silently become the lag, and lags never cross between companies.

## 12. The other scalars

| Scalar | Formula | Weakness |
|---|---|---|
| **Revenue** | net income ÷ revenue (profit margin) | Messiest XBRL concept; 28,332 firm-years have it vs 31,240 with assets, so a different company set |
| **Book equity** | net income ÷ lagged equity (ROE) | Equity can be negative, flipping the sign — smallest sample, 7,177 in window |
| **Market value of equity** | net income ÷ (price × shares) | **Not available** — SEC filing data contains no share prices |

Market value is arguably the *best* scalar, because it is the only size measure not produced
by the same accounting system whose output I am testing. But the SEC files have no prices.
I used book equity on the main sample, tested market value on my 300-ticker prototype and got
only 237 in-window observations — too few to inform anything — and **reported it as a
documented gap** rather than quietly dropping the check.

**The placebo variable:**

```
cash flow from operations ÷ total assets at the start of the year
```

Note the denominator is **identical** to the main measure. Only the numerator changes. That
is deliberate: if the scaling manufactures a notch, it will manufacture one here too.

---

# PART 5 — THE STATISTICS

## 13. Hypothesis testing

I observe 459 companies in the bin below zero and expected about 480. Is 21 fewer
meaningful? You cannot tell by looking, because counts always vary.

> **Sampling variation** — the wobble in any measurement from a limited number of
> observations, present even when nothing underneath is changing.

The procedure assumes the null is true and rejects it only if the data would be very
unlikely under it — like assuming innocence and requiring strong evidence to convict. The
asymmetry is intentional: it makes accidental "discoveries" hard.

> **p-value** — the probability of a result at least this extreme *if the null were true*.
> p = 0.43 means a gap this big happens 43% of the time by chance. p = 0.001 means once in a
> thousand.

> **Significance level** — the conventional threshold, 0.05.

**What a p-value is not:** the probability the hypothesis is true, or that you are wrong. It
is only a statement about compatibility with the null. This matters here, where two of my
p-values land at 0.051 and 0.057 — just the wrong side of a line that is itself arbitrary.

> **Type I error (false positive)** — concluding something is happening when nothing is.
> **Type II error (false negative)** — missing a real effect, usually from too little data.

Both are live. My null could be a false negative if the effect is real and small. My one
significant result could be a false positive, since running many specifications raises the
chance one crosses the line by luck.

**Significance is not importance.** With a large enough sample, a trivial effect becomes
detectable. Even the significant revenue-scaled notch is a shortfall of ~69 companies out of
13,452.

## 14. The test

**The idea:** predict each bin's count from its two neighbours.

```
expected count in bin i = (count in bin i−1 + count in bin i+1) ÷ 2
```

This makes one minimal assumption — that over a short stretch the distribution is roughly
straight — rather than requiring me to choose a functional form for the whole curve and risk
inventing the answer. It is a *local* assumption, which is its strength and, per §20, also
its weakness.

**Worked through with the real numbers,** bin width 0.005, the bin just below zero:

| Bin | ROA range | Count |
|---|---|---:|
| The one before | −0.010 to −0.005 | 409 |
| **Being tested** | **−0.005 to 0** | **459** |
| The one after | 0 to +0.005 | 550 |

```
expected = (409 + 550) ÷ 2 = 479.5
gap      = 459 − 479.5     = −20.5
```

Negative — the predicted direction. Is −20.5 a lot?

> **Standard error** — the typical amount a statistic varies from randomness alone; the
> yardstick a gap is measured against.

**Where it comes from.** Each company either lands in this bin or does not — a yes/no
outcome across N companies.

> **Binomial distribution** — the count of successes in N independent yes/no trials, with
> variance N·p·(1−p).

> **Variance** — the square of the standard deviation. Variances of independent quantities
> add, which is why the derivation works in variance units and takes a square root at the end.

The bin's own count contributes `N·pᵢ·(1−pᵢ)`. The prediction is built from two random
neighbour counts, so it wobbles too, contributing
`N·(pᵢ₋₁+pᵢ₊₁)·(1−pᵢ₋₁−pᵢ₊₁)` — but I use their *average*, and halving a quantity quarters
its variance since (½)² = ¼. Adding:

```
variance       = N·pᵢ·(1−pᵢ) + ¼·N·(pᵢ₋₁+pᵢ₊₁)·(1−pᵢ₋₁−pᵢ₊₁)
standard error = √variance = 25.9
```

> **z-score** — how many standard errors an observation sits from its expected value.

```
z = −20.5 ÷ 25.9 = −0.79
```

| \|z\| | Reading | ≈ p |
|---|---|---|
| under 1 | Completely ordinary | above 0.32 |
| 1 – 1.96 | Notable, not significant | 0.05 – 0.32 |
| **1.96** | **The 5% threshold** | **0.05** |
| over 2.58 | Strong | under 0.01 |
| over 3.29 | Very strong | under 0.001 |

**z = −0.79: right direction, unremarkable size.** The same calculation for the bin above
zero gives observed 550, expected 496, **z = +1.95** — close to the threshold. The two sides
behave differently, which is precisely why I report both.

## 15. A second test, and the three guardrails

**The held-out fit.** The neighbour method assumes local straightness, which is doing real
work. So a second test gets its expectation differently: fit a degree-4 polynomial across the
window **with the two zero-adjacent bins removed**, then test those two bins against the fit.

> **Goodness-of-fit test** — compares observed counts to a model's predictions across many
> bins at once.

> **Chi-square statistic** — sums (observed − expected)² ÷ expected across bins. Large values
> mean poor fit. Its **degrees of freedom** determine how large counts as surprising.

Because the curve never saw the tested bins, this is a genuine out-of-sample comparison with
2 interpretable degrees of freedom. It rejects smoothness at all three widths (p = 0.0009,
0.0052, 0.0044) — **but decomposing it, almost all of the rejection comes from the surplus
*above* zero, not a deficit below.** Two methods, different routes, compatible conclusion:
whatever is happening near zero is on the profit side.

**The three guardrails**, all fixed in code before any result existed:

1. **Zero on a bin edge.** §4. Edges are generated as integer multiples of the width rather
   than by stepping from the left, because stepping accumulates floating-point error and
   after forty steps "zero" might be 0.0000000001. Tested at all three widths plus awkward
   ones, and for the exact-zero and −1e-9 edge cases.
2. **Three bin widths, all reported.** §4. Became a diagnostic tool in §20.
3. **Both sides of zero, always.** §5. My two sides behave differently; reporting only the
   above-zero side would have made this look like a positive result.

All three are the same principle: **make the decision before you can see which answer it
produces.**

---

# PART 6 — RESULTS

## 16. The main result

Net income ÷ beginning-of-year assets. N = 16,018 firm-years, 3,582 companies, FY2016–2025.

| Bin width | Below zero (obs / exp) | z | p | Above zero (obs / exp) | z | p |
|---|---|---:|---:|---|---:|---:|
| 0.0025 | 246 / 252.0 | −0.31 | 0.753 | 291 / 252.5 | +1.91 | 0.057 |
| 0.005 | 459 / 479.5 | −0.79 | 0.429 | 550 / 496.0 | +1.95 | 0.051 |
| 0.01 | 868 / 898.5 | −0.87 | 0.383 | 1,083 / 1,017.0 | +1.73 | 0.083 |

**Encouraging:** the sign is correct at every width — negative below, positive above. Pure
noise would scatter the signs.

**Not encouraging:** the deficit below zero is nowhere near significant (p = 0.75, 0.43,
0.38 — gaps that size occur 40–75% of the time by chance). The surplus above zero sits
*exactly* on the threshold (0.057, 0.051, 0.083).

That is the most uncomfortable place for a result to land. A result at p = 0.051 and one at
0.049 are the same evidence; only one gets a label. Treating 0.051 as a discovery is exactly
the reasoning that fills literatures with findings that do not replicate. **So I call it
marginal and let the robustness checks decide how much weight it carries.**

**Summary: weak, directionally consistent, not significant.** A less thorough project would
have stopped here and said "there is a hint of something on the profit side."

> **Robustness check** — re-running an analysis under different reasonable choices to see
> whether the conclusion survives. If a finding holds only under one exact combination, it
> is a property of your choices rather than the world.

## 17. Robustness 1: does the divisor drive it?

Same companies, same years, same code, same widths. **Only the denominator changes** — so any
difference cannot be a period, filter, or method effect.

| Profit divided by | N | z below | p | z above | p |
|---|---:|---:|---:|---:|---:|
| Beginning-of-year assets | 16,018 | −0.79 | 0.43 | +1.95 | 0.051 |
| **Revenue** | 13,452 | **−2.97** | **0.003** | **+4.62** | **<0.001** |
| Beginning-of-year book equity | 7,177 | −1.20 | 0.23 | +1.61 | 0.11 |

Revenue holds across widths, ruling out a single-binning fluke: z below = −3.31 / −2.97 /
−3.25, all p ≤ 0.003.

**Same firms. Same net income. Three divisors. Three different answers.** This is the
Durtschi–Easton argument arriving as an empirical fact in 2016–2025 data. The presence of a
detectable notch is partly a property of the scaling choice. It also means a researcher who
ran only the revenue specification would report a strong finding that does not hold under
two equally reasonable alternatives.

**The caveat I volunteer.** Two explanations, and **I cannot separate them.** (A) Revenue
genuinely behaves differently as a divisor. (B) The revenue sample is a different set of
companies — 13,452 versus 16,018, because revenue is the messiest XBRL concept (§7) and
companies without clean tagging drop out. Both are consistent with the critique, which names
scaling *and* selection, but they are different mechanisms. Separating them needs a matched
sample restricted to companies with all three denominators. That is the first thing I would
run with more time.

## 18. Robustness 2: is it a small-company artifact?

Durtschi and Easton make a falsifiable prediction: **if the notch is an artifact, it should
be strongest among small firms.**

> **Tercile** — one of three equal groups formed by sorting.

| Tercile | Median assets | N | z below | z above |
|---|---:|---:|---:|---:|
| Small | $196m | 5,340 | −0.25 | +1.38 |
| Medium | $1.5bn | 5,339 | −0.26 | +1.23 |
| Large | $9.6bn | 5,339 | −0.91 | +0.73 |

**No concentration in small firms** — if anything the mild deficit is largest among the
*biggest*. That cuts against this specific mechanism.

> **Statistical power** — the probability of detecting an effect that is genuinely there.
> Smaller samples have less.

Honest limitation: splitting into thirds cuts power, and with nothing significant in any
tercile this is *weak* evidence against the small-firm story, not strong. I would not lean
on it.

## 19. Robustness 3: does my own threshold matter?

The $10m floor is the only parameter I chose myself, so it is the obvious place to suspect
tuning. The answer is not an argument but a table — produced by re-running the **entire
filter chain and test** at six floors.

| Floor | Panel N | Window N | z below | z above |
|---|---:|---:|---:|---:|
| $0 | 39,242 | 16,480 | −0.72 | +1.93 |
| $1m | 34,941 | 16,386 | −0.82 | +1.95 |
| **$10m (headline)** | 31,240 | 16,018 | −0.79 | +1.95 |
| $50m | 26,315 | 14,929 | −1.09 | +2.08 |
| $100m | 23,782 | 14,193 | −0.74 | +1.85 |
| $500m | 16,572 | 11,384 | −0.75 | +1.46 |

**Flat.** Across a fifty-fold range, z below stays between −0.72 and −1.09. The largest floor
removes more than half the panel and moves the statistic ~0.3 standard errors. My chosen
threshold is doing no work.

**One cell worth flagging rather than promoting:** at the $50m floor, z above reaches +2.08,
crossing 1.96. If I were hunting significance I could report that specification. I will not
— it is one cell of eighteen, and picking it is precisely the p-hacking described in §9. The
honest reading is that the above-zero statistic hovers near 1.9 and occasionally tips over by
chance. **Reporting the full table is what makes that reading possible.**

## 20. Robustness 4: the cash-flow placebo

The most important result in the project.

> **Placebo test** — running the same analysis on something the hypothesis says should show
> *no* effect. If an effect appears anyway, the method is suspect. (From medicine: if the
> sugar pill works too, the improvement is not from the drug.)

Per §2, cash flow contains no accruals, so it cannot be moved by revising an estimate. Run
the identical test with the identical denominator, changing only the numerator. Two expected
outcomes:

| Outcome | Meaning |
|---|---|
| Notch in net income, none in cash flow | Effect is specific to accruals — supports management |
| Notch in both, same direction | Something common produces it — suspect the scaling |

**Neither happened.**

| Measure | Width | z below | p | z above | p |
|---|---|---:|---:|---:|---:|
| Net income | 0.0025 | −0.31 | 0.75 | +1.91 | 0.057 |
| Net income | 0.005 | −0.79 | 0.43 | +1.95 | 0.051 |
| Net income | 0.01 | −0.87 | 0.38 | +1.73 | 0.083 |
| Cash flow | 0.0025 | +0.45 | 0.65 | −0.58 | 0.56 |
| **Cash flow** | 0.005 | **+2.04** | **0.042** | −1.79 | 0.074 |
| **Cash flow** | 0.01 | **+3.55** | **<0.001** | **−3.59** | **<0.001** |

Cash flow shows a break **larger than net income's and pointing the opposite way** — a
surplus just below zero, a deficit just above. At the widest width, highly significant in
both directions.

**This is not the shared-artifact result.** A common scaling artifact would push both the
same way, since the denominator is identical. The signs are opposite.

**What it actually means, which is worse.** Cash flow cannot have been managed into an
opposite-signed break at zero — there is no accrual mechanism, and no reason to target zero
cash flow. Yet the test reports one, significantly. **So the test's core assumption of local
smoothness fails — and it is the same machinery, same window, same denominator, that
produced the marginal z-scores for net income.** The placebo does not merely fail to
confirm; it undermines confidence in the instrument.

**The clue in the bin-width pattern.** The cash-flow effect grows monotonically:
`+0.45 → +2.04 → +3.55`. A genuine knife-edge discontinuity would behave the *opposite* way,
weakening as wider bins dilute a narrow feature with unaffected neighbours. Something that
strengthens with width is consistent with **curvature** being mistaken for a break: the
neighbour method assumes straightness, and wider bins reach further into regions where the
curve bends more, so the miss grows. **This is the payoff from guardrail 2** — with one bin
width I would have had a number and no way to interpret it.

**What I cannot claim.** I have not *proven* the net income result spurious — I have shown
the method produces false positives on a related measure, which is grounds for caution, not
a demonstration. I have not identified precisely what creates the cash-flow break; curvature
is my best explanation and the width pattern supports it, but I have not modelled the density
to confirm. What I can say is narrower: **the smoothness null is not safe on this data, and
any result resting on it deserves less weight than its p-value suggests.**

## 21. Conclusion

**Four findings.** (1) The main test is weak and directionally consistent — right sign at
every width, deficit below never significant, surplus above on the 0.05 line. (2) The result
depends on the divisor: revenue gives a clean significant notch, assets and equity give
nothing. (3) It is not a small-company artifact — no tercile concentration, flat across size
floors. (4) The placebo breaks the test.

**The conclusion: I did not find statistically significant evidence that companies bend
earnings to avoid reporting a loss, in recent SEC filing data.**

**Why this is a contribution rather than a failure.** Read as a *measurement study*, the
project answers a real question: how much does the classical result depend on choices usually
made in passing? A great deal. The scalar changes whether you find anything; the statistical
null fails on a control variable. Both are things anyone building on this literature would
want to know, and neither is visible if you run one specification.

There is also a structural point: I designed the project so a null would still be complete —
the plan was always "here is the distribution near zero, here is how it responds to bin
width, scaling and filters, here is what would have to be true for the classical result to
hold." That produces finished work either way. A design that is only interesting if the
answer is yes creates quiet pressure to find a yes.

**What would have changed my mind** — worth stating, because a hypothesis you cannot imagine
rejecting is not being tested. All three of: a deficit below zero significant at all three
widths, surviving all three denominators, and **absent** from the placebo. I got none of the
three. I would also have wanted the effect not to grow with bin width.

---

# PART 7 — LIMITATIONS AND PHRASING

## 22. Limitations

- **Observations are not independent.** 5.82 years per company; p-values somewhat too small
  (§10). The bias runs toward significance and my finding is a null, so correcting would make
  it more null.
- **The period is 2016–2025 only.** The original used 1976–1994. If **Sarbanes-Oxley** (2002
  legislation after Enron, requiring executives to personally certify financial statements
  and strengthening auditor independence) made earnings management riskier, the notch may
  genuinely have faded — in which case **a null today is *compatible* with the 1997 paper,
  not a refutation.** I cannot test this: SEC structured data begins in 2009, so I cannot
  reach the pre-SOX period at all. It would need a different data source.
- **The null hypothesis is the weak link.** My own placebo showed neighbour-averaging failing.
  A better design would fit a flexible model to the whole density and test a break against it
  — which would also give a *confidence interval* on the notch size rather than only a test
  against zero. My held-out polynomial test is a step toward that, but only a step.
- **Survivorship.** XBRL-era filers only; companies that went bankrupt or deregistered before
  2017 never appear. Loss-makers are likelier to disappear, so the region just below zero is
  probably affected more than above — which would push *toward* an apparent notch. I cannot
  measure the size of this.
- **Revenue tagging is inconsistent** (§17), so I cannot separate scalar effects from sample
  effects.
- **Market value of equity untested at scale** (§12).
- **10-K only; amendments excluded** rather than merged. An amendment sometimes corrects a
  material number, so in principle the amended figure is better; merging correctly is fiddly
  and I judged the gain small against the risk. A simplification, stated as one.

**What I am *not* limited by:** sample size is adequate (16,018 is comparable to the original
paper's); the data is primary, not a vendor's cleaned version; every exclusion is counted;
and the result is fully reproducible from the committed panel.

## 23. Phrasing discipline

**Allowed: "consistent with earnings management."** The test detects an anomaly in the shape
of a distribution. It never sees a manager, a decision, or a journal entry. If a notch
exists, management is *one* explanation among several — including the scaling effects of §6,
the survivorship of §22, and whatever produces the cash-flow break in §20, which is
definitely not management.

**Banned: "proves managers manipulate earnings."** Three errors in five words. *Proves* —
statistics quantifies compatibility, it does not prove. *Manipulate* — implies wrongdoing,
but earnings management is legal discretion inside the rules. *Managers* — attributes an
aggregate pattern to individual intent.

**The same restraint applies to my own null.** My result is "I did not find evidence," not
"there is no effect." Absence of evidence is not evidence of absence, particularly with a
marginal result and acknowledged limitations.

**Written out properly:** *In 16,018 firm-years of SEC data from FY2016–2025, net income
scaled by beginning-of-year assets shows a deficit immediately below zero and a surplus
immediately above at all three bin widths. Neither is statistically significant under the
headline specification. The pattern is consistent with earnings management to avoid losses,
and also with several alternatives the robustness checks cannot rule out. A cash-flow placebo
shows the method producing significant breaks in a measure that cannot plausibly be managed,
which reduces the weight the headline result can carry.*

---

# PART 8 — THE CODE

## 24. How it is built

Python 3.13 (pandas, numpy, scipy, matplotlib, pyarrow). ~3,200 lines across `src/` and
`tests/`; 35 unit tests. Repo: `github.com/riddhi-shedge/earnings-discontinuity`.

```
src/   sec_loader     download and reduce 37 quarterly archives
       panel          filters, drop log, scaled variables
       binning        bin edges — enforces zero-on-a-boundary
       discontinuity  neighbour test, z-statistics, chi-square
       plotting       publication figures
       build_panel    one command to rebuild the cached panel
notebooks/  01_explore · 02_main_test · 03_robustness
data/  panel.parquet (committed), drop_log.csv, result tables
tests/ 35 unit tests
```

Loading, filtering, binning and testing are separated so binning can be unit-tested without
touching SEC files and a test re-run does not re-parse 20 GB.

**The drop log is a first-class object.** `apply_filters()` returns `(clean_panel, drop_log)`
— a table with one row per filter recording name, written rationale, rows before, dropped,
after, and firms remaining. Three consequences: the README table is *generated* from it so
documentation cannot drift from code; a test verifies each step's "before" equals the
previous "after"; and adding a filter without a rationale is awkward because the signature
requires one. **The structure enforces the discipline rather than relying on memory.**

**What the 35 tests protect** — tests that only confirm code runs are not worth much:

- **Zero-on-a-boundary**, across all three widths plus awkward ones (0.003, 0.0001) where the
  window does not divide evenly; that exactly one bin is flagged each side; that exactly 0.0
  lands above and −1e-9 lands below.
- **The lagged denominator** — the $100/$400/$20 synthetic case asserting ROA = 0.20 not
  0.05, plus no-lag-on-first-year, gap-years, and no cross-company leakage.
- **Drop-log arithmetic.**
- **Does the test actually work?** I generate 200,000 smooth random observations, move half
  the bin below zero into the bin above — injecting a notch of *known* size — and assert
  detection in both directions (z < −5, z > +5). **And the mirror:** on smooth data with no
  injected notch, |z| must stay under 3. Together these are the closest thing to a proof the
  implementation is correct: it finds what is there and stays quiet when nothing is.

**Reproducibility:** the cleaned panel is committed so notebooks run offline; raw archives
are gitignored; seeds are fixed (42 for the ticker draw); versions pinned against the
environment the analysis actually ran in.

**Also produced:** publication figures in PNG/SVG/vector PDF, a 4-page writeup, a 19-slide
deck with speaker notes, an Excel workbook where histograms are live `COUNTIFS` over the
panel, and a Google Sheets edition with the statistics as live formulas verified to match
Python to three decimals.

---

# PART 9 — ANTICIPATED QUESTIONS

## 25. Questions and answers

Written to be said out loud.

### The result

**"So did you find anything?"**
Not a significant result, and that is the honest headline. The direction matched at every bin
width — fewer small losses, more small profits — but the deficit below zero was never
significant and the surplus above was borderline, around p = 0.05. What I did find is more
interesting: the result depends heavily on what you divide profit by, and a placebo test on
cash flow showed the method itself producing false breaks. So my conclusion is a measurement
one rather than a behavioural one.

**"Isn't a null result a failure?"**
It would be if I had designed the project to only work if the answer was yes. I planned for
the null from the start, because the alternative is being tempted to torture the data. What I
ended up with is a complete measurement study: here is the distribution, here is how it
responds to every choice, here is what would have to be true for the classical result to hold.
And the two findings that came out of it — denominator dependence and the placebo failure —
are more useful than a marginal confirmation would have been.

**"Why didn't you find it when the 1997 paper did?"**
Three candidates and I cannot fully distinguish them. Period: they used 1976–1994, I used
2016–2025, and the notch may have faded after Sarbanes-Oxley raised the cost. Method: my
placebo suggests the smoothness test is unreliable on this data, which raises a question
about the original too. Sample: XBRL-era filers are a different population from the Compustat
universe of the 1980s. The time-trend split is the check I would run first, but SEC structured
data does not reach before 2009.

**"Which finding are you most confident in?"**
The denominator sensitivity. It is a within-sample comparison — same companies, same years,
same code, only the divisor changes — so it is not confounded by period or sample construction
the way a comparison to a 1997 paper is. And it reproduces at all three widths. The caveat I
add unprompted is that the revenue sample is not quite the same set of companies.

**"Your surplus above zero is p = 0.051. Isn't that basically significant?"**
It is basically *nothing*, and that is the point. A result at 0.051 and one at 0.049 are the
same evidence; only one gets a label. Treating 0.051 as a discovery is the borderline
reasoning that fills literatures with findings that do not replicate. What makes me
comfortable calling it marginal is the context: the other side of zero shows nothing, and the
placebo shows the method generating false positives.

### The method

**"Explain the test to someone non-technical."**
Line every company up by profit as a percentage of its size and count how many fall in each
narrow band. For any band ask: if the pattern were smooth, how many should be here? The
natural answer is the average of the two bands either side. Compare that to what is actually
there. If a band is much emptier than its neighbours suggest, something unusual is happening.
The z-score measures "much" in units of the random variation you would expect anyway.

**"Why three bin widths?"**
Because bin width changes the answer, and reporting one invites "did you pick the flattering
one?" Too wide smooths the notch away, too narrow makes every bin noise. It also turned out
diagnostic: the cash-flow effect *grew* with bin width, which is the signature of curvature
rather than a genuine discontinuity. I would never have spotted that from a single width.

**"Why must zero be on a bin edge?"**
Because the hypothesis is about a break at exactly zero. A bin from −0.0025 to +0.0025 would
contain both the missing losses and the extra profits, which average each other out. I would
be deleting the signal before measuring it. My edges are integer multiples of the width, and
a test fails if that changes.

**"Where does the standard error come from?"**
Each observation either lands in a bin or not, so counts are binomial with variance N·p·(1−p).
The prediction is built from two neighbouring counts which are also random, so their variance
adds — and because I use their average rather than sum, that term carries a factor of one
quarter. Add the two and take the square root. I also ran a second test that does not depend
on the neighbour assumption: fit a smooth curve with the two zero-adjacent bins held out, then
test those bins against it.

**"How do you know your test works?"**
I tested it where I know the answer. I take smooth random data, move half the bin below zero
into the bin above — injecting a notch of known size — and assert strong detection in both
directions. Then the mirror: on smooth data with no notch it must not fire. Both are unit
tests that run on every change.

**"What would have convinced you the effect was real?"**
A deficit below zero significant at all three widths, surviving all three denominators, and
absent from the placebo. I got none of the three. I would also have wanted the effect not to
grow monotonically with bin width.

### The data

**"Why SEC data rather than a commercial database?"**
Free, primary, and reproducible by anyone without a licence — which matters for a project
someone might check. The trade-off is coverage starting in 2009, XBRL-era filers only, which
is a real limitation and one candidate explanation for my null.

**"How did you handle the volume?"**
113 million rows across 37 archives. I parse the numbers file by hand rather than with
read_csv, because the files are ~550 MB each with a free-text footnote field that breaks
naive quoting. Splitting on tabs and filtering to six tags before materialising anything keeps
memory flat and lets me count malformed lines exactly rather than silently skipping them. Zero
malformed across all 37 quarters — a verified fact, not an assumption.

**"Why 10-Ks only? Didn't that throw away data?"**
It threw away quarterly filings, but bought the thing I most needed. A 10-K shows last year's
balance sheet beside this year's, so one filing gives both the profit and the beginning-of-year
assets I divide by, from the same audited document. No cross-filing join, no risk of
mismatching a company to the wrong prior year. Given the lagged denominator is the most
important measurement decision, that was worth the trade.

**"You dropped banks — a quarter of your data."**
Because total assets does not mean the same thing for them. A bank's assets are its loan book;
an insurer's its investment portfolio. Both are an order of magnitude larger relative to
earnings than a manufacturer's factories, so ROA is not comparable across that boundary.
Including them means the distribution is a mixture of two populations with different natural
scales, and a kink at the join would be my own construction. Standard in the literature, and
in the drop log with a count so nobody takes my word for it.

**"What about survivorship bias?"**
Real, and I cannot measure it. Only companies filing with XBRL tags between 2017 and 2026
appear, so anything that went bankrupt or deregistered before 2017 never does. Loss-makers are
likelier to disappear, so the region just below zero is probably affected more than above,
which would push toward an apparent notch. I flag it rather than pretending the sample is
complete.

### The critique

**"What's the Durtschi–Easton critique in one sentence?"**
That a discontinuity in scaled earnings can be produced by the scaling and by sample selection
rather than by managers, so the shape of the distribution is not evidence of manipulation by
itself.

**"How did your design respond to it?"**
Four ways, mapping onto the four robustness checks. Alternate denominators test the scaling
directly. Size terciles test their specific prediction that the effect concentrates in small
firms. Size-floor sensitivity tests whether my own cutoff does work. The placebo tests whether
whatever produces the break could plausibly be earnings management at all. Three of four came
back pointing away from a management interpretation.

**"Did your results support the critique?"**
Partly, and not as I expected. The denominator sensitivity supports it directly. But the size
checks cut *against* the specific small-firm mechanism they emphasise. And the placebo found
something neither paper predicts: a significant opposite-signed break in cash flow, suggesting
the smoothness assumption itself is unreliable, independent of scaling.

**"If the method is unreliable, does that invalidate the 1997 paper?"**
I would not go that far. What I showed is that this method produces a significant break in a
control variable on *my* data, in *my* period, with *my* filters. That is grounds for caution
about results resting on the same assumption, including mine. It is not a demonstration the
original was wrong — different period, different sample, much larger effect. The honest
statement is that the null deserves more scrutiny than it usually gets, and I would want the
placebo run on their data before saying anything stronger.

### Judgment and process

**"What was the hardest decision?"**
Which denominator to make the headline. Revenue gives the significant, publishable-looking
result. Assets is the convention, what the original paper used, and what I had committed to
before seeing output. I went with assets and reported revenue as a robustness finding. Flipping
that after seeing results would have made the project p-hacking with extra steps — and what
makes the denominator finding interesting is precisely that I did not choose the flattering one.

**"What would you do differently?"**
Model the density properly — the neighbour-averaging null is the weak link and my own placebo
showed it. I would fit a smooth model to the whole distribution and test a break against it,
which would also give a confidence interval on the notch size rather than only a test against
zero. Second, build a matched sample with all three denominators available, to separate the
scalar effect from the sample effect. Third, try harder on market value of equity by joining
company IDs to a price source.

**"How long did it take, and in what order?"**
Phases with a gate at each. A crude 300-ticker prototype first, to see whether the effect was
visible before committing — not conclusive, but that was the point of doing it cheaply. Then
the modules and unit tests. Then the SEC pipeline and documented sample. Then the main test at
all three widths. Then robustness. Then the writeup and figures. The order matters: filters and
guardrails were committed to code before any result existed.

**"What are you most proud of?"**
That it is honest under pressure. Every exclusion counted, every specification reported, the
phrasing never exceeding the evidence — and when the placebo came back pointing the wrong way I
wrote it up as the most interesting finding instead of burying it. The code enforces the
discipline too: the zero-on-a-boundary rule and the lagged denominator are protected by tests
rather than by my memory.

**"Given a week, what else would you look at?"**
The other threshold from the original paper — zero *change* in earnings year over year, the
second place managers are said to avoid crossing. Same machinery, different variable, so it is
cheap and a genuinely independent test. If the notch appeared there but not at zero profit,
that would be interesting; if neither, that strengthens the null. Then the time trend, if I
could find a source reaching past 2009.

**"What did you learn?"**
Three things. Decide your filters before you look — it is the difference between a study and a
fishing trip. Plan for a null, so a clean "no" is still complete work. And build the placebo
early: cash flow was one extra column of data and it changed how I read everything else.

---

## Cheat sheet

**Pipeline** — 37 quarterly SEC archives (2017 Q1 – 2026 Q1) · 113,203,537 fact rows scanned,
0 malformed · 244,697 submissions, 53,156 annual 10-Ks used · ~3,200 lines of Python · 35
tests passing

**Sample** — 57,407 raw firm-years → **31,240** after filters, **5,366** companies ·
**16,018** firm-years from **3,582** companies in the ±10% window · FY2016–2025 · 5.82 years
per company · median lagged assets $615m · 50.0% of firm-years report a loss · largest
exclusion: financial firms, 14,590

**Main test — net income ÷ lagged assets**

| Width | Below zero | z | p | Above zero | z | p |
|---|---|---:|---:|---|---:|---:|
| 0.0025 | 246 vs 252 | −0.31 | 0.75 | 291 vs 253 | +1.91 | 0.057 |
| 0.005 | 459 vs 480 | −0.79 | 0.43 | 550 vs 496 | +1.95 | 0.051 |
| 0.01 | 868 vs 899 | −0.87 | 0.38 | 1,083 vs 1,017 | +1.73 | 0.083 |

Held-out χ² p: 0.0009 / 0.0052 / 0.0044 — driven by the surplus above zero.

**Robustness at width 0.005**

| Check | z below | z above | Verdict |
|---|---:|---:|---|
| Revenue scaling | **−2.97** (p .003) | **+4.62** (p <.001) | significant at all widths |
| Book equity scaling | −1.20 | +1.61 | not significant |
| Size terciles (S/M/L) | −0.25 / −0.26 / −0.91 | — | no small-firm concentration |
| Size floors $0 → $500m | −0.72 to −1.09 | +1.46 to +2.08 | flat across 50× range |
| **CFO placebo** | **+2.04** (p .042) | **−1.79** | opposite sign |
| **CFO placebo, width 0.01** | **+3.55** (p <.001) | **−3.59** (p <.001) | grows with width |

**Measurement** — lagged vs end-of-year assets identical in 0.02% of firm-years · median
absolute difference in ROA 0.0093 (≈ 2 bins at width 0.005)

**Citations, verified against publishers** — Burgstahler & Dichev (1997), *J. Accounting and
Economics* 24(1), 99–126 · Durtschi & Easton (2005), *J. Accounting Research* 43(4), 557–592

---

## Glossary

**Accrual** — entry recording revenue/expense before the cash moves. **Accrual accounting** —
recording when earned/incurred rather than when cash moves; required for public companies.
**Audited** — examined by an independent firm that issued an opinion. **Balance sheet** — what
a company owns and owes at one instant. **Bin** — one histogram interval, `[left, right)`.
**Binomial distribution** — count of successes in N yes/no trials; variance N·p·(1−p). **Book
equity** — assets minus liabilities. **Cash flow from operations (CFO)** — cash the business
generated; contains no accruals. **Chi-square** — goodness-of-fit statistic summing
(obs−exp)²/exp. **CIK** — the SEC's permanent company identifier. **Debt covenant** — a loan
condition, e.g. staying profitable; breaching one can trigger repayment. **Degrees of
freedom** — independent pieces of information in a test. **Discontinuity / notch** — a sharp
break in a smooth distribution. **Distribution** — how often each value occurs across a group.
**Earnings management** — steering reported results using discretion within the rules; legal.
**EDGAR** — the SEC's public filings database. **Firm-year** — one company, one fiscal year;
the unit of analysis. **Fiscal year** — a company's own 12-month reporting period.
**Goodness-of-fit test** — compares observed counts to a model across many bins. **Histogram**
— a chart of a distribution. **Income statement** — what a company earned over a period.
**Lagged** — from the previous period; lagged assets = last year's closing balance sheet.
**Liabilities** — what a company owes. **Net income** — bottom-line profit after all expenses
and tax. **Null hypothesis (H₀)** — the "nothing unusual" default. **Panel** — one row per
company per year. **Parquet** — compressed, typed, column-oriented file format. **p-hacking** —
trying many choices and keeping the most favourable. **Placebo test** — the same analysis on
something that should show no effect. **Pooling** — treating every firm-year as independent.
**p-value** — probability of a result this extreme if the null were true. **Revenue** — sales
before costs. **ROA** — net income ÷ total assets (here, always lagged). **ROE** — net income ÷
equity. **Sampling variation** — wobble from a limited number of observations. **Sarbanes-Oxley
(2002)** — post-Enron law requiring executive certification of financial statements. **Scaling**
— dividing by a size measure for comparability. **Shareholders' equity** — assets minus
liabilities. **SIC code** — four-digit industry classification. **Significance level** — the
threshold for calling a result significant, conventionally 0.05. **Standard error** — typical
variation of a statistic from randomness alone. **Statistical power** — probability of detecting
a real effect. **Survivorship bias** — distortion from studying only what survived. **Tercile** —
one of three equal groups. **Total assets** — everything a company owns of value. **Type I /
Type II error** — false positive / false negative. **Variance** — square of the standard
deviation; variances of independent quantities add. **XBRL** — tagging standard making filings
machine-readable. **z-score** — standard errors from the expected value; |z| > 1.96 is the 5%
threshold.

---

*Riddhi Shedge · UCLA, Statistics and Data Science*
*Code, data and figures: github.com/riddhi-shedge/earnings-discontinuity*
