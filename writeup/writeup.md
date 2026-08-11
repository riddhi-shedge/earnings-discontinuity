# Do companies bend earnings to avoid reporting a loss?

### A discontinuity test on 16,018 recent SEC firm-years, and why the answer is "not clearly"

---

## The question

If reported earnings were unmanaged, the distribution of net income across thousands
of firms should be smooth. There is no economic reason for a sharp break at exactly
zero. But a manager staring at a small loss has discretion — the timing of a
write-off, a slightly early revenue recognition, a reserve estimate nudged. If that
discretion gets used to cross zero, the distribution should carry a **notch**: too few
firms just below zero, too many just above.

Burgstahler and Dichev (1997) found exactly that notch and read it as evidence of
earnings management to avoid losses. The finding is one of the most cited in empirical
accounting.

Durtschi and Easton (2005) argued the inference does not follow. A discontinuity in a
*scaled* earnings distribution can be produced by the scaling itself, by
sample-selection, or by differences between the kinds of firms that fall either side
of zero — none of which require a manager to do anything. Their title says it: the
shapes of these distributions "are not evidence ipso facto."

That disagreement is what makes the exercise worth doing carefully. Replicating the
notch is a small task. Finding out whether it survives contact with the critique is
the real one.

## Data and construction

The sample is built from the **SEC Financial Statement Data Sets** — quarterly flat
files derived from XBRL filings, free and unauthenticated. I processed 37 quarterly
archives spanning 2017q1 through 2026q1, scanning 113.2 million fact rows. The schema
was verified against the live 2026q1 archive before any loader code was written; it
has changed across the years and building against a remembered format would have been
a silent source of error.

Only **10-K** filings are used, for a specific reason: a 10-K carries the comparative
balance sheet, so one submission gives both current-year and prior-year total assets.
That supplies the lagged denominator directly, from the filer's own comparative
column, with no cross-filing join.

The measure is

$$ROA_{it} = \frac{NetIncome_{it}}{TotalAssets_{i,t-1}}$$

with **beginning-of-year** assets. Using end-of-year assets would put the current
year's earnings into the denominator of the thing being measured — the most common way
this analysis goes wrong.

Filters were fixed before any result was looked at, and every exclusion is counted in
the README: 57,407 raw 10-K firm-years, less financial firms (14,590), utilities
(1,404), missing industry codes, missing net income, non-positive lagged assets, and
a $10m size floor, leaves **31,240 firm-years across 5,366 firms**, fiscal years
2016–2025. Restricting to the analysis window |ROA| ≤ 0.10 leaves **16,018 firm-years
across 3,582 firms**. Firm-years are pooled, which inflates N relative to independent
units — stated, not hidden.

Two things are enforced in code rather than by care. Zero always falls on a **bin
boundary**: every edge is an integer multiple of the bin width, so a bin can never
straddle the point being tested. And every test runs at **three** bin widths —
0.0025, 0.005, 0.01 — because a result that appears at only one width is a choice, not
a finding.

## Method

Each bin's count is predicted from its immediate neighbours,
`expected_i = (count_{i-1} + count_{i+1}) / 2`, and the standardized difference uses
the binomial variance standard in this literature. Both the bin immediately below zero
and the bin immediately above are always reported: the hypothesis predicts a deficit
below *and* a surplus above, and finding only one is weaker evidence.

## What I found

**The direction is right. The magnitude is not there.**

| Bin width | below zero | z | above zero | z |
|---|---|---:|---|---:|
| 0.0025 | 246 obs / 252 pred | −0.31 | 291 / 252 | +1.91 |
| 0.005 | 459 / 480 | −0.79 | 550 / 496 | +1.95 |
| 0.01 | 868 / 899 | −0.87 | 1,083 / 1,017 | +1.73 |

At every width the bin below zero is thinner than its neighbours predict and the bin
above is thicker — the predicted pattern. But the deficit below zero is nowhere near
significance (p = 0.75, 0.43, 0.38), and the surplus above sits right at the boundary
(p = 0.057, 0.051, 0.083). A goodness-of-fit test that holds the two zero-adjacent
bins out of a smooth fit does reject smoothness (p ≈ 0.001–0.005), but the rejection
is driven by the surplus above zero, not by any deficit below it.

The honest summary of the main test: **weak, directionally consistent, not
significant.**

**Then the robustness checks got interesting.**

*Scaling matters enormously.* Rescaling the same firms by revenue rather than lagged
assets produces a clear notch — z = −2.97 below zero (p = 0.003) and +4.62 above
(p < 0.001), holding at all three bin widths. Book equity produces nothing (z = −1.20).
Same firms, same years, same test; three scalars, three different answers, one of them
publishable and two of them null. This is Durtschi and Easton's argument arriving
empirically rather than theoretically, and it is the most useful thing in the project.

*Size is not the story.* The artifact explanation predicts the notch should concentrate
among small firms, whose tiny denominators produce extreme scaled values. It does not:
z below zero is −0.25 (small), −0.26 (medium), −0.91 (large). And the result is
insensitive to the size floor across the full range from $0 to $500m, so the headline
$10m threshold is not doing any work.

*The placebo is the punchline.* Cash flow from operations, scaled by the same lagged
assets, should be far harder to push across zero through accrual timing. The
prediction is that the notch is absent there. Instead CFO shows a **larger break in
the opposite direction** — a surplus just below zero and a deficit just above
(z = +3.55 / −3.59 at width 0.01, p < 0.001).

That is not the simple scaling-artifact result, which would have pushed both measures
the same way. It is something more awkward: the local-smoothness null fails, and fails
significantly, on a measure that should not have a discontinuity at all. Note too that
the CFO effect grows steadily with bin width (+0.45 → +2.04 → +3.55) — the signature
of density curvature being read as a break, not of a knife-edge jump at zero. Whatever
neighbour-averaging is picking up in CFO, it cannot be earnings management, and the
same machinery is what produced the marginal z-statistics for net income.

## What I conclude

**I did not find evidence of a discontinuity at zero in scaled net income** in recent
SEC filing data. The direction of the effect matches the classical result at every bin
width, which is worth something, but the deficit of small losses is not statistically
significant under the headline specification; the one clearly significant version
appears only under revenue scaling; and the placebo shows the test's own null
assumption breaking down on data that cannot have been managed into shape.

Where a notch does appear, "consistent with earnings management" is as far as the
evidence reaches. This test detects a distributional anomaly. It does not identify a
manager, a decision, or an accrual, and it cannot separate management from any other
mechanism that places extra mass just above zero.

## Limitations, plainly

- **Pooled firm-years.** 5.8 years per firm on average; within-firm observations are
  not independent, so the p-values above are optimistic.
- **The null is the weak link.** Neighbour-averaging assumes local linearity in the
  density. The placebo demonstrates that assumption failing. A stronger design would
  model the density and test a break against the fitted model.
- **Period.** Fiscal years 2016–2025 only. Burgstahler and Dichev worked on 1976–1994.
  If the notch has genuinely faded in the post-SOX, post-XBRL era, a null here is
  compatible with their finding rather than a refutation of it. Testing that would
  require pushing the panel back before 2009, which the SEC data sets do not reach;
  the time-trend split was deliberately left out of scope.
- **Coverage.** XBRL-era filers only, so firms that deregistered before 2017 never
  appear. Revenue is tagged inconsistently across filers, so the revenue-scaled sample
  is a somewhat different set of firms than the asset-scaled one — which is itself a
  candidate explanation for why revenue scaling behaves differently.
- **Market value of equity** could not be tested at scale: the SEC flat files carry no
  price data. Book equity substituted on the main sample; market value was tested on a
  237-observation yfinance sample, far too small to inform anything.

## References

Burgstahler, D., & Dichev, I. (1997). Earnings management to avoid earnings decreases
and losses. *Journal of Accounting and Economics*, 24(1), 99–126.

Durtschi, C., & Easton, P. (2005). Earnings Management? The Shapes of the Frequency
Distributions of Earnings Metrics Are Not Evidence Ipso Facto. *Journal of Accounting
Research*, 43(4), 557–592.

U.S. Securities and Exchange Commission. Financial Statement Data Sets.
https://www.sec.gov/data-research/sec-markets-data/financial-statement-data-sets

---

*Code, notebooks, the full exclusion log and all figures: see the repository README.
Sample N = 16,018 firm-years (3,582 firms), fiscal years 2016–2025.*
