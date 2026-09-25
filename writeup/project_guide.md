# Earnings Discontinuity Analysis — Complete Project Guide

### Everything I did, why I did it, and how to talk about it

---

## How to use this document

This is my own reference for the project — not the writeup I hand to someone, but the one that makes me
fluent enough to answer any question about it.

- **Parts 1–11** walk through the project in the order I actually built it, in plain language.
- **Part 12** covers how the code is organised, for a more technical conversation.
- **Part 13** is the largest section: questions I expect to be asked, with answers. If I only have ten
  minutes to prepare, I read Part 13 and the cheat sheet.
- **Part 14** is every number on one page.
- A glossary is at the end for the accounting and statistics terms.

**The single most important thing to remember:** the result is a *null*. I did not find convincing evidence
that companies bend earnings to avoid a loss. That is not a failed project — the checks that produced the
null are the most interesting part, and being able to explain *why* the answer is "not clearly" is a
stronger position than claiming a result I can't defend.

---

## The answer at three lengths

**Thirty seconds.** I tested a famous accounting result on current SEC data — the claim that companies
manage their earnings to avoid reporting a small loss, which should show up as a gap in the distribution
of profits right at zero. In 16,018 company-years I found the gap goes in the predicted direction but
isn't statistically significant. More interestingly, when I re-ran the test on cash flow — which is much
harder to manipulate — it showed a *bigger* break than earnings did. That tells me the test itself is
picking up something other than manipulation, which is exactly what a well-known 2005 critique of this
literature argued.

**Two minutes.** Add: where the data came from (SEC Financial Statement Data Sets, 37 quarterly archives,
113 million rows scanned), the one measurement decision that matters most (scale profit by the assets the
company *started* the year with, not ended it with), and the three robustness findings — the result is
denominator-dependent, it isn't concentrated in small firms, and the cash-flow placebo breaks the test's
own assumption.

**Five minutes.** Walk the funnel from 57,407 filings to 16,018 tested company-years, explain the
neighbour-averaging test with the three-bar picture, show the headline histogram, then spend most of the
time on the four robustness checks and what each one rules in or out. End on the phrasing: this test
detects a distributional anomaly, so "consistent with earnings management" is the ceiling of what anyone
can claim from it.

---

## Part 1 — The question, in plain language

Companies report a profit or a loss every year. Zero is a psychologically loaded line: a loss, even a tiny
one, is a headline, a covenant trigger, a bad look for a bonus target.

Managers have legitimate discretion over some of the numbers. When to book a write-off. How to estimate a
warranty reserve or a bad-debt allowance. Whether a sale closes this quarter or next. None of that is
fraud — it is ordinary judgment inside accounting rules.

**The hypothesis:** if some managers use that discretion to push a tiny loss over the line into a tiny
profit, you should see it in the shape of the distribution across thousands of companies. Specifically:

- **Too few companies just below zero** (small losses that got converted)
- **Too many companies just above zero** (where they landed)

That dip-and-bump pattern is called a **notch** or **discontinuity**. The logic is that there's no economic
reason for a sharp break at exactly zero. Business conditions vary smoothly; a company earning +0.1% is
not fundamentally different from one earning −0.1%. So a sharp break is evidence that something
non-economic — a human decision — is operating right at that line.

**The null hypothesis** is that the distribution is smooth through zero and any apparent notch is just
random variation in the counts.

---

## Part 2 — Why this question is contested

Two papers define the debate, and knowing both is what makes this project more than a replication.

**Burgstahler & Dichev (1997)**, *Journal of Accounting and Economics* 24(1), 99–126.
They looked at US companies from 1976 to 1994, found exactly this dip-and-bump, and read it as evidence of
earnings management to avoid losses. It became one of the most-cited results in empirical accounting.

**Durtschi & Easton (2005)**, *Journal of Accounting Research* 43(4), 557–592.
They pushed back. Their argument, in plain terms: nobody looks at raw dollars of profit, because $1m means
something completely different for a startup than for Apple. You have to divide by something — assets,
revenue, market value — to compare companies. And they showed that **the act of dividing, plus the choice
of which companies end up in your sample, can manufacture a notch even when no manager did anything.**
Their title says it: the shapes of these distributions "are not evidence ipso facto."

I verified both citations against the publishers rather than quoting from memory, because getting a
citation wrong in a writeup is an unforced error.

**Why this framing matters for the project:** replicating the notch is a small task. Finding out whether it
survives contact with the critique is the real one. Every design decision I made downstream is about making
the test hard to fool — and the robustness checks in Part 9 exist specifically to address Durtschi and
Easton.

---

## Part 3 — The data

**Source: SEC Financial Statement Data Sets.** These are free, public flat files the SEC builds from every
XBRL-tagged filing. No authentication, no scraping, no vendor licence. The URL pattern is:

```
https://www.sec.gov/files/dera/data/financial-statement-data-sets/{YYYY}q{Q}.zip
```

**What I pulled.** 37 quarterly archives, 2017 Q1 through 2026 Q1. Each zip contains four tab-separated
files; I used two of them:

- `sub.txt` — one row per submission: accession number, company ID (CIK), name, SIC industry code, fiscal
  period end, form type, filing date.
- `num.txt` — one row per reported number: submission, XBRL tag, the date it refers to, how many quarters
  it spans, the unit, and the value. This is the big one, around 550 MB uncompressed per quarter.

Across all 37 quarters I scanned **113,203,537 fact rows with zero malformed lines**, filtering down to
the handful of line items I needed: net income, total assets, revenue, cash flow from operations, and
shareholders' equity.

**I verified the file format against the live 2026 Q1 archive before writing any loader code.** The schema
has changed over the years and building against a remembered format would have been a silent source of
error. The current `num.txt` columns are:

```
adsh  tag  version  ddate  qtrs  uom  segments  coreg  value  footnote
```

Two fields matter especially:

- `qtrs = 0` means a point-in-time balance-sheet value; `qtrs = 4` means a full annual period.
- `segments` and `coreg`, when non-empty, mean the row is a segment or subsidiary breakdown rather than the
  consolidated company total. **I keep only rows where both are blank**, so every number is a company-level
  total.

**Why only 10-K filings.** Out of 244,697 total submissions I used the 53,156 that are annual 10-Ks. The
reason is specific and important: a 10-K shows **last year's balance sheet next to this year's**. That
comparative column is where I get the beginning-of-year assets figure — from the same filing, as the
company itself presents it, with no cross-filing join and no guessing. Quarterly filings don't give you
that. (See Part 5 for why beginning-of-year assets matter so much.)

**A second, smaller data source.** Before committing to the SEC pipeline I built a quick prototype using
`yfinance` on 300 randomly-drawn tickers, just to see whether the effect was visible at all. It wasn't
conclusive — only 207 observations landed in the test window, far too few — but it was the right order of
operations: cheap look first, expensive pipeline second. I kept it in the repo, labelled as a prototype,
and it's also where I tested market value of equity as a scalar (see Part 9.1).

---

## Part 4 — Building the sample

Every company-year I removed is counted and has a written reason. I fixed these filters **before running
the test**, so I couldn't tune the sample to produce an answer.

| Step | Dropped | Remaining | Firms |
|---|---:|---:|---:|
| 0. All 10-K company-years | — | 57,407 | 10,304 |
| 1. Fiscal years 2016–2025 only | 141 | 57,266 | 10,276 |
| 2. Drop missing industry code | 550 | 56,716 | 10,078 |
| 3. Drop financial firms (SIC 6000–6999) | 14,590 | 42,126 | 7,251 |
| 4. Drop utilities (SIC 4900–4949) | 1,404 | 40,722 | 7,034 |
| 5. Drop missing net income | 703 | 40,019 | 6,979 |
| 6. Drop missing or non-positive lagged assets | 764 | 39,255 | 6,882 |
| 7. Size floor: lagged assets ≥ $10m | 8,011 | 31,244 | 5,366 |
| 8. One filing per firm-year | 4 | **31,240** | **5,366** |
| Analysis window: \|ROA\| ≤ 0.10 | 15,222 | **16,018** | **3,582** |

**The reasoning behind each:**

1. **Fiscal-year range.** Only 2016–2025 are fully covered by the filing quarters I downloaded. The handful
   outside that range are delinquent filers catching up years late — a few dozen companies, not a usable
   cross-section.
2. **Missing industry code.** I can't apply the industry filters below without one.
3. **Financial firms.** This is the biggest single cut and the most important one. A bank's "total assets"
   are its loan book. An insurer's are its investment portfolio. Dividing profit by that means something
   completely different from dividing a manufacturer's profit by its factories and inventory. They're not
   comparable, so they come out. This is standard practice in the literature.
4. **Utilities.** Rate-regulated returns make utility earnings mechanically smooth near a target — the
   regulator effectively sets the profit. Conventional to exclude; I noted it either way and it's optional
   in the code.
5. **Missing net income.** No numerator, no observation.
6. **Missing or non-positive lagged assets.** The denominator has to exist and be positive. A negative
   denominator would flip the sign of the whole ratio and put a loss on the profit side of zero.
7. **Size floor of $10m.** Tiny denominators produce wild ratios — a company with $50k of assets and a
   $30k loss has an ROA of −60%. Durtschi and Easton identify exactly this as a source of the artifact.
   **I don't just assert the floor is harmless — I test it** (Part 9.3), re-running everything at floors
   from $0 to $500m.
8. **One filing per firm-year.** Amendments and transition-period filings can duplicate a company-year;
   I keep the most recent period end.

**The analysis window.** After filtering, I restrict the test to companies within ±10% of zero. This isn't
a sample-quality filter, it's a statement of what's being studied: behaviour *near* zero. A company earning
40% on assets is not deciding whether to cross the line. I report this separately from the filters for
exactly that reason.

**Pooling.** Companies appear multiple times — 5.82 years each on average. This inflates my N relative to
the number of independent units, so the p-values are somewhat optimistic. Pooling is standard in this
literature and the simplest defensible choice, but I state it rather than hide it.

---

## Part 5 — The measurement decision that matters most

The measure is **return on assets**:

```
ROA = net income for the year ÷ total assets at the START of the year
```

**Why divide at all.** Raw net income can't be compared across companies. $1m of profit is enormous for a
small firm and a rounding error for a large one. Scaling by size puts every company on the same axis.

**Why beginning-of-year, not end-of-year.** This is the pitfall I was most careful about. Companies report
assets at the end of the year — and that end-of-year figure **already includes this year's profit**, because
profit flows into retained earnings, which is part of equity, which is part of the balance sheet.

If I divided by end-of-year assets, I'd be dividing profit by something that contains that same profit.
Mechanically, that pulls the ratio toward zero and **smooths out the exact break I'm trying to detect.**
It's the single most common way this analysis goes wrong and it's easy to do by accident.

**How much does it matter in practice?** In my panel the two figures are essentially never identical —
they match in 0.02% of company-years — and the median absolute difference in the resulting ratio is
**0.0093**, which is about two bins wide at my main bin width. Not a rounding difference; a real one.

**Where the number comes from.** Straight out of the 10-K's comparative balance sheet column, as the
company itself reported it. And I wrote a unit test that fails if the code ever reaches for the
end-of-year figure by mistake.

**Other scalars I built** (used in the robustness checks): revenue, beginning-of-year book equity, and
market value of equity — plus cash flow from operations scaled by the same lagged assets, for the placebo.

---

## Part 6 — How the test works

This is simpler than it sounds and I can explain it with three bars.

**Step 1 — bin the data.** Chop the range from −10% to +10% into equal bins. At my main bin width of 0.005,
each bin is half a percent of assets wide, and there are 40 of them.

**Step 2 — predict each bin from its neighbours.** If the curve were smooth, the count in any bin should be
roughly the average of the two bins either side of it:

```
expected count = (count in bin before + count in bin after) ÷ 2
```

**Worked example, using the real numbers.** The bin just below zero (−0.005 to 0):
- The bin before it holds **409** company-years
- The bin after it holds **550**
- So if the curve were smooth I'd expect about **(409 + 550) ÷ 2 = 479.5**
- I actually observe **459** — a shortfall of about 20, in the direction the hypothesis predicts

**Step 3 — ask whether 20 is surprising.** Counts bounce around by chance, so a gap of 20 means nothing
until I know how big a gap chance alone produces. I divide the gap by its standard error to get a
**z-score**:

```
z = (observed − expected) ÷ standard error
```

The rule of thumb: |z| above about 2 is unusual enough to take seriously (that's the 5% significance
level); |z| below 1 is comfortably inside what randomness produces. Here z = **−0.79**, so: right
direction, not surprising.

**Where the standard error comes from.** Each company either lands in this bin or doesn't, so the count
follows a binomial distribution. With N observations and bin probabilities p, the standard deviation of
the difference works out to:

```
sd = √[ N·pᵢ·(1−pᵢ) + ¼·N·(pᵢ₋₁+pᵢ₊₁)·(1−pᵢ₋₁−pᵢ₊₁) ]
```

The first term is the variance of the bin's own count; the second is the variance of the neighbour average
(hence the ¼, since averaging two things halves the variance, and ½² = ¼). This is the standard formula
used in this literature.

**A second test.** I also run a goodness-of-fit test that doesn't rely on the neighbour assumption: fit a
smooth curve (a degree-4 polynomial) to the whole window *with the two zero-adjacent bins held out*, then
ask whether those two held-out bins fit the curve. Because the fit never saw the bins being tested, its
two degrees of freedom are interpretable in the normal way. It rejects smoothness at all three bin widths
(p ≈ 0.001–0.005) — but the rejection is driven almost entirely by the surplus *above* zero, not by any
deficit below.

---

## Part 7 — The three guardrails

These are about not fooling myself, and I set all three in code before seeing any result.

**1. Zero always sits on a bin edge, never inside a bin.**
Every bin edge is an exact integer multiple of the bin width, so zero is always a boundary. If a bin
straddled zero, the deficit below and the surplus above would land in the same bar and cancel out — I'd
be averaging away the exact thing I'm measuring. There's a unit test that fails if this ever breaks, and
it checks awkward widths too, not just convenient ones.

*Detail worth knowing:* bins are half-open `[left, right)`, so a company reporting exactly zero falls in
the bin *above* zero. That's a deliberate, stated convention — breakeven is not a loss.

**2. Every test runs at three bin widths: 0.0025, 0.005, and 0.01.**
Bin width is a real analytical choice, not a plotting detail. Too wide and you smooth the notch away; too
narrow and every bin is noise. So I don't pick one — I run all three and report all three, every time. A
result that only shows up at one width is a property of the width, not of the companies.

**3. I always report both sides of zero.**
The hypothesis predicts a deficit below zero *and* a surplus above. It would be easy to lead with whichever
side looks better. Finding only one is weaker evidence, and I say so plainly rather than quietly
emphasising the stronger half.

---

## Part 8 — What I found

**The main test, net income scaled by beginning-of-year assets, N = 16,018:**

| Bin width | Below zero (seen / expected) | z | p | Above zero (seen / expected) | z | p |
|---|---|---:|---:|---|---:|---:|
| 0.0025 | 246 / 252 | −0.31 | 0.75 | 291 / 253 | +1.91 | 0.057 |
| 0.005 | 459 / 480 | −0.79 | 0.43 | 550 / 496 | +1.95 | 0.051 |
| 0.01 | 868 / 899 | −0.87 | 0.38 | 1,083 / 1,017 | +1.73 | 0.083 |

**How to read this honestly:**

- The **sign is right at every width**. Fewer small losses than the curve implies, more small profits. That
  consistency across widths is worth something — it isn't a single-specification artifact.
- But the **deficit below zero is nowhere near significant** (p = 0.75, 0.43, 0.38). That's noise territory.
- And the **surplus above zero is borderline** (p = 0.057, 0.051, 0.083) — sitting right on the 5% line,
  which is exactly where you should be most suspicious of yourself.
- The held-out goodness-of-fit test does reject smoothness, but driven by the surplus above zero.

**My summary sentence: weak, directionally consistent, not significant.** If I'd stopped here I would say
"there's a hint of something, mostly on the profit side." I didn't stop here.

---

## Part 9 — The four robustness checks

This is the part of the project I'd most want to be asked about.

### 9.1 — Alternate denominators (does the scaling choice drive the result?)

Same companies, same years, same test. Only the divisor changes.

| Profit divided by | N | z below | p | z above | p |
|---|---:|---:|---:|---:|---:|
| beginning-of-year assets | 16,018 | −0.79 | 0.43 | +1.95 | 0.051 |
| **revenue** | 13,452 | **−2.97** | **0.003** | **+4.62** | **<0.001** |
| beginning-of-year book equity | 7,177 | −1.20 | 0.23 | +1.61 | 0.11 |

**This is the most important finding in the project.** Scale by revenue and you get a clean, significant
notch that holds at all three bin widths (z below = −3.31 / −2.97 / −3.25). Scale by assets or book equity
and you get nothing. Same firms, same net income, three scalars, three different answers — and one of them
is what you'd call publishable.

This is Durtschi and Easton's argument appearing empirically in 2016–2025 data rather than as a theoretical
objection. It means the notch is partly a property of the scaling choice, not purely of the earnings.

**The honest caveat I volunteer here:** revenue is tagged inconsistently across filers, so the
revenue-scaled sample (13,452) is a somewhat different set of companies than the asset-scaled one (16,018).
I can't fully separate "revenue behaves differently as a scalar" from "the revenue subsample is a different
population." Both are consistent with the critique, but they're different mechanisms and I don't claim to
have distinguished them.

**Market value of equity** is the one check I couldn't run at scale: the SEC flat files carry no share
prices. I used book equity as the equity-based scalar on the main sample, and tested market value on the
300-ticker yfinance prototype — but that gave only 237 observations, far too few to inform anything. I
report this as a documented deviation rather than quietly dropping it.

### 9.2 — Size subsamples (is it a small-company artifact?)

The artifact story makes a specific prediction: if the notch comes from tiny denominators, it should be
strongest among small companies.

| Tercile | Median assets | N | z below | z above |
|---|---:|---:|---:|---:|
| Small | $196m | 5,340 | −0.25 | +1.38 |
| Medium | $1.5bn | 5,339 | −0.26 | +1.23 |
| Large | $9.6bn | 5,339 | −0.91 | +0.73 |

**No concentration in small firms** — if anything the mild deficit is largest among the biggest companies.
That cuts *against* the small-firm artifact story. Though with nothing significant in any tercile, this
check doesn't distinguish very much either way, and I say so.

### 9.3 — Size-floor sensitivity (does my $10m cutoff matter?)

I re-ran the entire filter chain and test at six different minimum sizes.

| Floor | Panel N | Window N | z below | z above |
|---|---:|---:|---:|---:|
| $0 | 39,242 | 16,480 | −0.72 | +1.93 |
| $1m | 34,941 | 16,386 | −0.82 | +1.95 |
| **$10m (headline)** | 31,240 | 16,018 | −0.79 | +1.95 |
| $50m | 26,315 | 14,929 | −1.09 | +2.08 |
| $100m | 23,782 | 14,193 | −0.74 | +1.85 |
| $500m | 16,572 | 11,384 | −0.75 | +1.46 |

**Flat.** The result barely moves across a fifty-fold range of size cutoffs. My chosen floor isn't doing
any work, which is exactly what I want to be able to say about an arbitrary-looking parameter.

### 9.4 — The cash-flow placebo (the decisive check)

**The logic.** Earnings can be nudged through accounting judgment — timing, estimates, accruals. Cash flow
from operations is much harder to nudge that way: cash either arrived or it didn't. So I run the *identical*
test on cash flow, scaled by the *identical* denominator.

- If net income shows a notch and cash flow doesn't → the anomaly is specific to accrual earnings, which
  is what the management story predicts.
- If both show a notch → suspect the scaling or the method, because cash flow can't have been managed into
  that shape.

**What actually happened — and it surprised me:**

| Measure | Bin width | z below | p | z above | p |
|---|---:|---:|---:|---:|---:|
| Net income | 0.005 | −0.79 | 0.43 | +1.95 | 0.051 |
| **Cash flow** | 0.005 | **+2.04** | **0.042** | −1.79 | 0.074 |
| **Cash flow** | 0.01 | **+3.55** | **<0.001** | **−3.59** | **<0.001** |

Cash flow shows a break at zero that is **larger than the earnings one and points the opposite way** — a
*surplus* just below zero and a *deficit* just above.

**What I take from this.** This is not the simple "shared scaling artifact" result, which would have pushed
both measures the same way. It's something more awkward and more interesting: the test's core assumption —
that the curve is locally smooth, so neighbours predict the middle — **breaks down badly in this kind of
data**. And it's the same machinery that produced the borderline z-scores for net income. So the placebo
doesn't merely fail to confirm the result; it undermines confidence in the tool that produced it.

**One more clue that supports that reading:** the cash-flow effect grows steadily with bin width (+0.45 →
+2.04 → +3.55). A genuine knife-edge discontinuity at zero wouldn't behave that way. Smooth curvature in
the density being mistaken for a break would — wider bins reach further out, where the curve bends more,
so neighbour-averaging misestimates by more.

---

## Part 10 — The conclusion, and how to phrase it

**What I conclude:** I did not find statistically significant evidence of a deficit of small losses in
recent SEC filing data. The direction matches the classical result at every bin width, which is worth
something, but:

1. The deficit below zero is never significant under the headline specification.
2. The one clearly significant version appears only under revenue scaling.
3. The cash-flow placebo shows the smoothness assumption failing on data that cannot have been managed.

Read as a **measurement study**, the contribution is showing how much the classical result depends on
choices — of scalar above all — that are usually made in passing.

**The phrasing discipline.** Where a notch does appear, the most anyone can say is that it is
**"consistent with earnings management."** This test detects a distributional anomaly. It does not identify
a manager, a decision, or a journal entry, and it cannot separate management from any other mechanism that
puts extra mass just above zero.

I never say this "proves managers manipulate earnings." That phrasing is banned in my own writeup, and if
someone else uses it about my result I'd correct it. Overclaiming is the way this project goes wrong.

**Why a null is a good outcome here.** I planned for it from the start — the project was designed so that a
clean "no" would still be complete: here is the distribution of scaled earnings near zero in this period,
here is how it responds to bin width, scaling choice, and sample filters, and here is what would have to be
true for the classical result to hold in this sample. That's a finished piece of work, and it's more
defensible than a positive I'd have to walk back under questioning.

---

## Part 11 — Limitations I volunteer before being asked

- **Companies repeat across years.** 5.82 years each on average; those observations aren't independent, so
  my p-values are somewhat optimistic. Pooling is standard, but it's a real caveat.
- **The period is 2016–2025 only.** The original result used 1976–1994. If the notch genuinely faded after
  Sarbanes-Oxley made earnings management riskier and costlier, then a null today is *compatible* with
  Burgstahler and Dichev rather than a refutation of them. My data can't test that, because the SEC
  structured datasets don't reach back before 2009.
- **The null hypothesis is the weak link.** Neighbour-averaging assumes local linearity. The placebo proves
  it isn't safe. A stronger design would model the whole density and test a break against the fitted model
  rather than against two neighbours.
- **Coverage and survivorship.** XBRL-era filers only, so companies that deregistered before 2017 never
  appear. Revenue is tagged inconsistently, which is why the revenue-scaled sample differs.
- **Market value of equity untested at scale** (see 9.1).
- **10-K only.** I excluded amended filings (10-K/A) rather than merging them — a simplification.

---

## Part 12 — How the project is built

For a more technical conversation.

**Repository:** `github.com/riddhi-shedge/earnings-discontinuity` — Python 3.13, pandas, numpy, scipy,
matplotlib, pyarrow. About 3,200 lines across `src/` and `tests/`.

**Layout:**

```
src/         sec_loader     downloads and reduces the 37 quarterly archives
             panel          the filters, the drop log, the scaled variables
             binning        bin edges — enforces zero-on-a-boundary
             discontinuity  the neighbour test, z-statistics, chi-square
             plotting       the publication figures
             build_panel    one command to rebuild the cached panel
             export_*       PDF, dashboard, deck and explainer exporters
notebooks/   01_explore · 02_main_test · 03_robustness
data/        panel.parquet (committed), drop_log.csv, result tables
figures/     headline histogram + robustness figures, PNG/SVG/PDF
tests/       35 unit tests
```

**Design decisions worth mentioning:**

- **The drop log is a first-class object, not a comment.** `apply_filters()` returns
  `(clean_panel, drop_log)` — every filter appends a row with its name, rationale, rows before, rows
  dropped, rows after, and firms remaining. The README table is generated from it. A test asserts the
  chain is arithmetically consistent, so a filter can't silently lose rows.
- **`num.txt` is parsed by hand rather than with `read_csv`.** At ~550 MB per quarter with a free-text
  footnote field that breaks naive quoting, splitting on tabs and filtering before materialising anything
  keeps memory flat and lets me count malformed lines exactly instead of skipping them silently. Result:
  113.2M rows scanned, 0 malformed.
- **Caching.** Raw archives are gitignored; the cleaned panel is committed as parquet. Notebooks run
  top-to-bottom off the cache and never touch SEC servers. Anyone can reproduce every published number
  without downloading 2 GB.
- **SEC politeness.** SEC's fair-access policy requires a real contact address in the User-Agent. That's
  read from an environment variable rather than hardcoded, so the address isn't published in the repo.

**The 35 tests, and what they actually protect:**

- **Zero-on-a-boundary** — parameterised across all three widths plus awkward ones like 0.003 and 0.0001,
  where 0.10 isn't an integer multiple of the width. Also tests that exactly one bin is flagged each side,
  that an exact zero lands above, and that −1e-9 lands below.
- **The lagged denominator** — that ROA uses the prior year's assets, that a firm's first observation has
  no lag, that a *gap* year doesn't silently become the lag, and that lags never cross between companies.
- **Drop-log accounting** — that each step's "before" equals the previous step's "after."
- **Does the test actually work?** — I inject a synthetic notch into random data by moving half the mass
  from the bin below zero into the bin above, and assert the test detects it in both directions (z < −5
  and z > +5). And the mirror: on smooth random data it must *not* fire. This is the test I'd point at if
  someone asks how I know the statistics are right.

**Other deliverables:** a publication-quality headline figure, a 4-page writeup, a 19-slide presentation
with full speaker notes, an Excel workbook where the histograms are live `COUNTIFS` formulas over the
panel, and a Google Sheets edition where the expected counts, z-scores and p-values are live formulas.

---

## Part 13 — Questions I expect, and how I'd answer them

### About the result

**"So did you find anything?"**
Not a significant result, and that's the honest headline. The direction matched the prediction at every bin
width — fewer small losses, more small profits — but the deficit below zero was never significant and the
surplus above was borderline at around p = 0.05. What I did find is more interesting: the result depends
heavily on what you divide profit by, and a placebo test on cash flow showed the statistical method itself
producing false breaks. So my conclusion is a measurement one.

**"Isn't a null result a failure?"**
It would be if I'd designed the project to only work if the answer was yes. I didn't — I planned for the
null from the start, because the alternative is being tempted to torture the data. What I ended up with is
a complete measurement study: here's the distribution, here's how it responds to every choice I made, and
here's what would have to be true for the classical result to hold here. And the two findings that came out
of it — denominator-dependence and the placebo failure — are more useful than a marginal confirmation
would have been.

**"Why do you think you didn't find it when the 1997 paper did?"**
Three candidate explanations, and I can't fully distinguish them. First, period: they used 1976–1994, I
used 2016–2025, and it's plausible the notch genuinely faded after Sarbanes-Oxley raised the cost of
earnings management. Second, method: my placebo suggests the neighbour-smoothness test is unreliable on
this data, which raises a question about the original test too. Third, sample: XBRL-era filers are a
different population than the Compustat universe of the 1980s. If I had more time, the time-trend split
is the check I'd run first — but the SEC structured data doesn't reach before 2009, so it'd need a
different source.

**"Which of your findings are you most confident in?"**
The denominator sensitivity. It's a within-sample comparison — same companies, same years, same code, only
the divisor changes — so it isn't confounded by period or sample construction in the way a comparison to a
1997 paper would be. And it reproduces at all three bin widths.

### About the method

**"Explain the test to someone non-technical."**
Line every company up by profit-as-a-percentage-of-size and count how many fall in each narrow band. For
any band, ask: if the pattern were smooth, how many should be here? The natural answer is the average of
the two bands either side. Then compare that to what's actually there. If a band is much emptier than its
neighbours suggest, something unusual is happening there. The z-score just measures "much" in units of how
much random variation you'd expect anyway.

**"Why three bin widths?"**
Because bin width is an analytical choice that changes the answer, and reporting only one invites the
question "did you pick the flattering one?" Too wide smooths the notch away, too narrow makes every bin
noise. Running all three and reporting all three removes the question. It also turned out to be
diagnostic: the cash-flow effect *grew* with bin width, which is the signature of curvature rather than a
genuine discontinuity — I'd never have spotted that from a single width.

**"Why does zero have to be on a bin edge?"**
Because the whole hypothesis is about a break at exactly zero. If a bin ran from −0.0025 to +0.0025, the
missing losses and the extra profits would land in the same bar and average each other out. I'd be
deleting the signal before measuring it. My bin edges are integer multiples of the width so zero is always
a boundary, and there's a test that fails if that ever changes.

**"Where does the standard error formula come from?"**
Each observation either lands in a given bin or it doesn't, so counts are binomial. The variance of the
difference between an observed count and the neighbour average is the bin's own binomial variance plus the
variance of the average of the two neighbours — and averaging two things gives you the one-quarter factor.
It's the standard approach in this literature. I also ran a second test that doesn't depend on the
neighbour assumption: fit a smooth curve with the two zero-adjacent bins held out, then test those bins
against the fit.

**"How do you know your test actually works?"**
I tested it on data where I know the answer. I take random smooth data, move half the observations from
the bin below zero into the bin above — injecting a notch of known size — and assert the test detects it
strongly in both directions. Then the mirror: on smooth data with no injected notch it must not fire.
Both are in the unit test suite and run on every change.

**"What would have convinced you the effect was real?"**
A deficit below zero significant at all three bin widths, surviving all three denominators, *and* absent
from the cash-flow placebo. I got none of the three. I'd also have wanted the effect not to grow
monotonically with bin width, since that pattern points at curvature rather than a break.

### About the data

**"Why SEC data rather than a commercial database?"**
It's free, it's the primary source, and it's fully reproducible by anyone without a licence — which
matters for a portfolio project someone might want to check. The trade-off is that it only goes back to
2009 and coverage is XBRL-era only, which is a real limitation and one of the candidate explanations for
my null.

**"How did you handle the volume?"**
113 million rows across 37 archives. I parse `num.txt` by hand rather than with `read_csv` — the files are
around 550 MB each and have a free-text footnote field that breaks naive quoting. Splitting on tabs and
filtering to my six tags *before* materialising anything keeps memory flat and lets me count malformed
lines exactly rather than silently skipping them. Zero malformed across all 37 quarters.

**"Why 10-Ks only? Didn't that throw away data?"**
It threw away quarterly filings, yes — but it bought me the thing I most needed. A 10-K shows last year's
balance sheet next to this year's, so one filing gives me both the profit and the beginning-of-year assets
figure I divide by, from the same audited document. No cross-filing join, no risk of mismatching a company
to the wrong prior year. Given that the lagged denominator is the most important measurement decision in
the project, that was worth the trade.

**"Why drop banks? That's 14,590 observations — a quarter of your data."**
Because "total assets" doesn't mean the same thing for them. A bank's assets are its loan book; an
insurer's are its investment portfolio. Both are an order of magnitude larger relative to earnings than a
manufacturer's factories and inventory, so ROA isn't comparable across the boundary. Including them would
mean the distribution I'm testing is a mixture of two populations with different natural scales, which
could itself create shape artifacts. It's standard in the literature, and it's in the drop log with a
count so nobody has to take my word for it.

### About the critique

**"What's the Durtschi–Easton critique, in one sentence?"**
That a discontinuity in scaled earnings can be produced by the scaling and by sample selection rather than
by managers, so the shape of the distribution is not evidence of manipulation by itself.

**"How did your design respond to it?"**
Four ways, and they map onto my four robustness checks. Alternate denominators test the scaling directly.
Size terciles test their specific prediction that the effect should concentrate in small firms. Size-floor
sensitivity tests whether my own arbitrary cutoff is doing work. And the cash-flow placebo tests whether
whatever produces the break can plausibly be earnings management at all. Three of the four came back
pointing away from a management interpretation.

**"Did your results support the critique?"**
Partly, and not in the way I expected. The denominator sensitivity supports it directly — the notch appears
under revenue scaling and not under assets or equity. But the size checks cut *against* the specific
small-firm mechanism they emphasise. And the placebo found something neither paper predicts: a significant
opposite-signed break in cash flow, which suggests the smoothness assumption itself is unreliable here,
independent of scaling.

### About judgment and process

**"What was the hardest decision?"**
Which denominator to make the headline. Revenue gives the significant, publishable-looking result. Assets
is the convention in this literature, it's what the original paper used, and it's the one I'd committed to
before seeing any output. I went with assets and reported revenue as a robustness finding. If I'd flipped
that after seeing the results, the whole project would have been a p-hacking exercise with extra steps.

**"What would you do differently?"**
Model the density properly. The neighbour-averaging null is the weak link, and my own placebo proved it.
I'd fit a smooth model to the whole distribution and test a break against that, which would also let me
put a confidence interval on the size of the notch rather than just testing against zero. Second, I'd try
harder on market value of equity — probably by joining CIKs to a price source rather than falling back to
my small prototype sample.

**"How long did this take, and what was the sequence?"**
I built it in phases with a gate at each one. First a crude 300-ticker prototype to see if the effect was
even visible — it wasn't conclusive, but that was the point of doing it cheaply. Then the reusable
modules and tests. Then the SEC pipeline and the documented sample. Then the main test at all three
widths. Then the robustness checks. Then the writeup and figures. The order matters: filters and
guardrails were committed to code before any result existed.

**"What are you most proud of?"**
That the project is honest under pressure. Every exclusion is counted, every specification is reported,
the phrasing never exceeds the evidence, and when the placebo came back pointing the wrong way I wrote
that up as the most interesting finding instead of burying it. The code enforces the discipline too —
the zero-on-a-boundary rule and the lagged denominator are both protected by tests, not by my memory.

**"If I gave you this dataset and a week, what else would you look at?"**
The other threshold from the original paper — zero *change* in earnings year over year, which is a second
place managers are said to avoid crossing. It uses the same machinery with a different variable, so it's
a cheap extension and a genuine independent test. After that, the time trend, if I could find a source
reaching back past 2009.

---

## Part 14 — Numbers cheat sheet

**Data pipeline**

- 37 quarterly SEC archives, 2017 Q1 – 2026 Q1
- 113,203,537 fact rows scanned, 0 malformed
- 244,697 total submissions → 53,156 annual 10-Ks used
- ~3,200 lines of Python; 35 unit tests, all passing

**Sample**

- 57,407 raw company-years → **31,240** after filters, **5,366** companies, fiscal years 2016–2025
- **16,018** company-years from **3,582** companies inside the ±10% test window
- 5.82 years per company on average
- Median beginning-of-year assets: $615m
- Share of company-years reporting a loss: 50.0%
- Largest single exclusion: financial firms, 14,590

**Main test — net income ÷ lagged assets**

| Bin width | Below zero | z | p | Above zero | z | p |
|---|---|---:|---:|---|---:|---:|
| 0.0025 | 246 vs 252 | −0.31 | 0.75 | 291 vs 253 | +1.91 | 0.057 |
| 0.005 | 459 vs 480 | −0.79 | 0.43 | 550 vs 496 | +1.95 | 0.051 |
| 0.01 | 868 vs 899 | −0.87 | 0.38 | 1,083 vs 1,017 | +1.73 | 0.083 |

Held-out χ² p-values: 0.0009 / 0.0052 / 0.0044 — driven by the surplus above zero.

**Robustness, at bin width 0.005**

| Check | z below | z above | Verdict |
|---|---:|---:|---|
| Revenue scaling | **−2.97** (p 0.003) | **+4.62** (p <0.001) | significant at all three widths |
| Book equity scaling | −1.20 | +1.61 | not significant |
| Size terciles (small / med / large) | −0.25 / −0.26 / −0.91 | — | no small-firm concentration |
| Size floors $0 → $500m | −0.72 to −1.09 | +1.46 to +2.08 | flat across a 50× range |
| **CFO placebo** | **+2.04** (p 0.042) | **−1.79** | opposite sign |
| **CFO placebo at width 0.01** | **+3.55** (p <0.001) | **−3.59** (p <0.001) | grows with bin width |

**Measurement**

- Lagged and end-of-year assets identical in only 0.02% of company-years
- Median absolute difference in the resulting ratio: 0.0093 (≈ 2 bins at width 0.005)

**Citations — verified against publishers, not quoted from memory**

- Burgstahler, D., & Dichev, I. (1997). *Journal of Accounting and Economics*, 24(1), 99–126.
- Durtschi, C., & Easton, P. (2005). *Journal of Accounting Research*, 43(4), 557–592.

---

## Glossary

**Accrual** — an accounting entry recording revenue or expense when it's earned or incurred rather than
when cash moves. Accruals are where most legitimate discretion lives, which is why they're the suspected
channel for earnings management.

**Book equity** — assets minus liabilities as reported on the balance sheet. Distinct from *market* equity,
which is the share price times shares outstanding.

**CIK** — Central Index Key, the SEC's permanent identifier for a filing entity. The key I join on.

**Discontinuity / notch** — a sharp break in an otherwise smooth distribution. Here, the dip just below
zero and bump just above.

**Earnings management** — using discretion within accounting rules to influence reported results. Not the
same as fraud.

**Fiscal year** — a company's own 12-month reporting period, which needn't match the calendar year.

**Goodness-of-fit test** — asks whether observed counts match what a model predicts, across many bins at
once rather than one bin at a time.

**Lagged assets** — total assets at the *start* of the year, i.e. the prior year's closing balance sheet.

**Net income** — bottom-line profit after all expenses, interest and tax.

**p-value** — the probability of seeing a result at least this extreme if nothing unusual were happening.
Below 0.05 is the conventional threshold for "significant."

**Placebo test** — running the same test on something that shouldn't show the effect. If it does, the
method is suspect.

**ROA (return on assets)** — net income divided by total assets. My main measure, always with lagged assets.

**SIC code** — Standard Industrial Classification, the SEC's industry code. I use it to exclude financial
firms (6000–6999) and utilities (4900–4949).

**Standard error** — how much a statistic would bounce around from random sampling alone. The yardstick the
observed gap is measured against.

**XBRL** — the structured tagging standard the SEC requires in filings. It's what makes machine-readable
flat files possible.

**z-score** — how many standard errors an observation sits from its expected value. |z| > 1.96 is the 5%
significance threshold.

---

*Riddhi Shedge · UCLA, Statistics & Data Science*
*Code, data and figures: github.com/riddhi-shedge/earnings-discontinuity*
