# Earnings Discontinuity Analysis

### A complete guide to the project: what I did, why, and what it all means

---

## How to use this guide

This is written to be read straight through by someone who knows no accounting and no
statistics. Every technical term is defined the first time it appears, and every formula
is worked through with real numbers from the project.

The guide is organised in ten parts:

| Part | Chapters | What it covers |
|---|---|---|
| I | 1–4 | The background: how companies report money, and how distributions work |
| II | 5–6 | The research question and the two papers that frame it |
| III | 7–9 | Where the data comes from and how I got it |
| IV | 10–13 | Which companies I kept, which I removed, and why |
| V | 14–16 | The measurement: what I divide by, and why it matters enormously |
| VI | 17–21 | The statistics, built up from scratch |
| VII | 22–27 | What I found, including all four robustness checks |
| VIII | 28–29 | Limitations, and the discipline of not overclaiming |
| IX | 30 | How the code is built |
| X | 31 | Questions I expect, with answers |

At the end there is a one-page numbers cheat sheet and a full glossary.

**If you read only one thing,** read Chapter 26 (the cash-flow placebo) and Chapter 27
(what it all means). That is where the project's real contribution sits.

**One thing to fix in your head before starting.** The headline result is a *null
result* — I did **not** find convincing evidence that companies bend their earnings to
avoid reporting a loss. That is not a failed project. A null that is honestly reported
and thoroughly checked is a real finding, and the checks that produced it turned out to
be more interesting than a positive result would have been. Chapter 27 explains why.

---

# PART I — THE BACKGROUND YOU NEED

---

## Chapter 1 — What a company reports every year

Before any of this makes sense, you need to know what numbers companies publish and what
those numbers mean. If you already know what net income and total assets are, skim to
Chapter 2.

### 1.1 The three financial statements

Every public company in the United States must publish a set of financial statements once
a year. There are three main ones, and they answer three different questions.

> **Income statement** *(also called the profit-and-loss statement, or P&L)*
> Answers: **how much did the company earn over the year?** It starts with revenue at the
> top, subtracts every cost, and ends with a single bottom-line number.

> **Balance sheet**
> Answers: **what does the company own and owe, at one exact moment?** It is a snapshot,
> not a period. It is dated, for example "as at 31 December 2024."

> **Cash flow statement**
> Answers: **how much actual cash moved in and out over the year?** This is different
> from profit, for reasons explained in Chapter 2.

An analogy that holds up reasonably well. The income statement is like your payslip for
the year: it covers a stretch of time. The balance sheet is like a photograph of your
bank account, your car, and your student loan on one particular day. The cash flow
statement is your bank transaction history, showing what actually moved.

### 1.2 The four numbers this project uses

Out of the hundreds of line items in those statements, this project uses four.

> **Net income**
> The bottom line of the income statement. Revenue minus every expense: cost of goods,
> wages, rent, interest on debt, and tax. If it is positive the company made a
> **profit**. If it is negative the company made a **loss**. *This is the number at the
> centre of the whole project.*

> **Total assets**
> From the balance sheet. Everything the company owns that has value: cash in the bank,
> inventory sitting in a warehouse, factories, machinery, patents, and money customers
> owe it. It is the standard measure of how big a company is.

> **Revenue** *(also called sales, or turnover)*
> The top line of the income statement. Total money earned from selling things, before
> any costs are subtracted. A company can have enormous revenue and still make a loss.

> **Cash flow from operations** *(often shortened to CFO, not to be confused with Chief
> Financial Officer)*
> From the cash flow statement. The cash the company's actual business generated,
> ignoring money raised from investors or spent buying other companies. This becomes very
> important in Chapter 26.

### 1.3 How the balance sheet fits together

One fact you need for Chapter 15, so it is worth knowing now. A balance sheet always
balances, because of this identity:

```
Assets  =  Liabilities  +  Shareholders' equity
```

In words: everything the company owns was paid for either with borrowed money
(liabilities) or with owners' money (equity). There is no third source.

> **Liabilities** — what the company owes to others: bank loans, bonds, unpaid bills.

> **Shareholders' equity** *(also called book equity, or just equity)*
> What would be left for the owners if the company sold everything and paid off every
> debt. It is literally assets minus liabilities.

Here is the part that matters later. **Profit flows into equity.** When a company earns
money and does not pay it all out to shareholders, the leftover is added to a bucket
inside equity called *retained earnings*. So:

```
This year's profit  →  retained earnings  →  equity  →  total assets
```

That chain is why the *timing* of the assets figure turns out to be the single most
important measurement decision in this project. Hold that thought until Chapter 15.

### 1.4 Fiscal years

> **Fiscal year** — a company's own twelve-month reporting period. It does not have to
> match the calendar year.

Most US companies end their year on 31 December. But plenty do not. Apple's fiscal year
ends in late September. Many retailers end in late January, after the Christmas rush has
been fully counted.

This matters practically: when I compare a company across time, I compare its own fiscal
year to its own previous fiscal year. I never assume a year runs January to December.

### In one sentence

A company publishes an income statement (what it earned over the year), a balance sheet
(what it owns at one moment), and a cash flow statement (what cash actually moved); this
project uses net income, total assets, revenue, and cash flow from operations.

---

## Chapter 2 — Why profit is not cash, and why that creates room for judgment

This chapter explains the mechanism that makes the entire research question possible. If
profit were simply "cash in minus cash out," there would be almost nothing to manage, and
no project here.

### 2.1 Two ways to count

There are two systems for deciding *when* something counts as revenue or expense.

> **Cash accounting** — you record money when it actually moves. Cash arrives, you count
> it. Cash leaves, you count it. Simple and hard to argue with.

> **Accrual accounting** — you record revenue when it is *earned* and expenses when they
> are *incurred*, regardless of when the cash moves.

Public companies are required to use accrual accounting. Here is why, with an example.

A company signs a contract in November 2024 to deliver software. It delivers the software
in December 2024. The customer pays in February 2025.

- Under **cash** accounting, the whole sale counts in 2025, the year the money arrived.
- Under **accrual** accounting, it counts in 2024, the year the work was done.

Accrual is more informative. It tells you the company did the work in 2024, which is what
you want to know if you are judging how 2024 went. Cash accounting would make 2024 look
empty and 2025 look unusually good, misrepresenting both years.

> **Accrual** — an accounting entry that records revenue or expense before the
> corresponding cash moves. The gap between profit and cash is made up of accruals.

### 2.2 Where judgment necessarily enters

Accrual accounting is more informative, but it requires *estimates*, and estimates require
judgment. Four real examples where a company must make a call.

**Bad debt allowance.** A company sells on credit and some customers will never pay.
Accounting rules require estimating that loss *now*, not waiting to find out. Is it 2% of
receivables, or 3%? Both may be defensible. The difference changes reported profit.

**Warranty reserve.** A company sells appliances with a three-year warranty. It must
estimate today what future repairs will cost. That estimate is a guess informed by
history, and reasonable people can land in different places.

**Depreciation life.** A company buys a machine for $10 million and spreads that cost over
the machine's useful life. Is the machine useful for eight years or twelve? At eight years
the annual charge is $1.25m; at twelve it is $833k. That is a $417k difference in reported
profit every year, from one judgment call.

**Timing of a write-off.** A product line is failing and the company must eventually write
down its value. But *when* the evidence becomes conclusive enough to require it is a
matter of judgment, and can reasonably fall in December or in January.

None of these four are cheating. They are ordinary accounting, done by honest people, and
auditors sign off on ranges of reasonable answers rather than single correct ones.

### 2.3 Why cash flow is different

Now the crucial contrast, which Chapter 26 depends on entirely.

**Cash flow from operations is much harder to influence through judgment.** You cannot
change how much cash is in the bank by revising an estimate of future warranty costs. The
estimate changes reported profit; it does not change the bank balance. Cash either arrived
or it did not.

This is not to say cash flow is impossible to influence. A company can delay paying
suppliers, or push hard to collect from customers before year end. But those are real
operational actions with real consequences, not a change of estimate in a spreadsheet.

Put the two side by side:

| | Net income | Cash flow from operations |
|---|---|---|
| Built from | Revenue and expenses, including estimates | Actual cash movements |
| Contains accruals | Yes, substantially | No |
| Movable by revising an estimate | Yes | No |
| Movable by real operational action | Yes | Yes, but with real costs |

**This asymmetry is the foundation of the placebo test in Chapter 26.** If companies are
nudging reported numbers through accounting judgment, the effect should appear in net
income and *not* in cash flow. That prediction is testable, and testing it is the most
valuable thing in this project.

### In one sentence

Accrual accounting records revenue and expenses when they are earned or incurred rather
than when cash moves, which requires estimates, which creates legitimate room for
judgment — and cash flow, which contains no accruals, is much harder to move that way.

---

## Chapter 3 — What "earnings management" means, and why zero is special

### 3.1 The definition

> **Earnings management** — using the discretion available within accounting rules to
> influence reported results toward a desired number.

Notice what that definition does *not* say. It does not say lying. It does not say fraud.
Earnings management sits in the grey zone: choices that are individually defensible, made
with an eye on where the bottom line lands.

The line between the two:

| | Earnings management | Accounting fraud |
|---|---|---|
| Within the rules? | Yes | No |
| Example | Choosing a 3% bad-debt allowance rather than 2%, both defensible | Recording a sale that never happened |
| Auditor would sign off? | Usually yes | No |
| Legal? | Yes | No |

This project tests for the first, not the second. Being precise about this matters,
because "companies manipulate earnings" sounds like an accusation of fraud, and that is
not what any of this shows.

### 3.2 Why zero specifically?

The number zero has no special economic meaning. A company earning $1 of profit is not
meaningfully healthier than one losing $1. The difference is a rounding error against a
billion-dollar balance sheet.

But zero has enormous *psychological and contractual* meaning. Four reasons:

**1. It is a headline.** "Company posts loss" is a story. "Company posts small profit" is
not. The sign of the number changes how it gets reported, far more than the size does.

**2. Debt covenants.** When a bank lends to a company, the loan agreement often contains
conditions called covenants. For example, the company must stay profitable, or keep a
financial ratio above some level. Breaching a covenant can let the lender demand immediate
repayment. A loss can trigger that; a tiny profit does not.

**3. Executive bonuses.** Many bonus schemes pay out only if the company is profitable. A
manager whose bonus vanishes at zero has an obvious interest in which side of zero the
year lands on.

**4. Human loss aversion.** There is a long line of psychology research showing people
treat losses as much worse than equivalent gains. A "loss year" feels categorically
different from a "breakeven year," even when the underlying numbers barely differ.

### 3.3 Putting it together into a testable claim

Here is the logical chain the whole project rests on:

1. Zero is a meaningful threshold for managers, for the four reasons above.
2. Accrual accounting gives managers legitimate discretion over reported profit
   (Chapter 2).
3. A manager facing a small loss might use that discretion to land just above zero.
4. If *enough* managers do that, it should be visible in the shape of the distribution
   across thousands of companies.

Step 4 is what makes this testable. You cannot look inside one company and see a decision.
But you can look at thousands of companies at once and ask whether the overall pattern
looks natural.

That requires understanding distributions, which is Chapter 4.

### In one sentence

Earnings management is using legitimate accounting discretion to steer the reported
number; zero matters because of headlines, debt covenants, bonuses, and loss aversion; and
if managers act on that, it should leave a visible fingerprint across thousands of
companies.

---

## Chapter 4 — Distributions, histograms, and why bin width matters

This chapter builds the statistical picture from nothing. If you are comfortable with
histograms, skim to 4.4, which contains something genuinely important.

### 4.1 What a distribution is

> **Distribution** — the pattern of how often each value occurs across a group.

Take the height of everyone in a large school. A few people are very short, a few very
tall, and most are somewhere in the middle. If you counted how many people fall in each
height range, you would get a shape: low at the edges, high in the middle. That shape is
the distribution of height.

The key idea is that you learn something from the *shape* that you cannot learn from any
single person. No individual is "the distribution." It only exists across the group.

### 4.2 Building a histogram

> **Histogram** — a chart of a distribution. You split the range of values into equal
> intervals called **bins**, count how many observations fall in each bin, and draw a bar
> for each count.

> **Bin** — one interval in a histogram. Every bin has a **left edge** and a **right
> edge**, and every observation lands in exactly one bin.

Worked example with eight companies. Suppose their profits, as a percentage of their size,
are:

```
-1.2%,  -0.4%,  -0.1%,  0.3%,  0.6%,  0.9%,  1.4%,  1.8%
```

Using bins one percentage point wide:

| Bin | Values landing in it | Count |
|---|---|---:|
| −2% to −1% | −1.2% | 1 |
| −1% to 0% | −0.4%, −0.1% | 2 |
| 0% to +1% | 0.3%, 0.6%, 0.9% | 3 |
| +1% to +2% | 1.4%, 1.8% | 2 |

Drawn as bars, that is a histogram. Eight observations became four numbers, and those four
numbers describe the shape.

**One convention worth stating**, because it matters in this project. A bin is
**half-open**, written `[left, right)`. A value exactly equal to the left edge belongs to
that bin; a value exactly equal to the right edge belongs to the *next* bin. Without that
rule, a value sitting exactly on a boundary would belong to two bins at once.

In this project that convention has a specific consequence: a company reporting *exactly*
zero profit lands in the bin **above** zero. That is deliberate and stated. Breaking even
is not a loss.

### 4.3 What "smooth" means, and why we expect it

> **Smooth distribution** — one where the count changes gradually from bin to bin, with no
> sudden jumps.

Go back to the height example. If you found 400 people between 170 and 171 cm, you would
expect roughly 400 in the 171-to-172 bin too. Maybe 380, maybe 420, but not 40 and not
4,000. Height varies continuously, so the counts change gradually.

The same logic applies to company profits. Business conditions vary continuously. Companies
face a continuous range of luck, competence, demand, and cost. So the number of companies
earning 0.1% should be close to the number earning 0.2%, which should be close to the
number earning 0.3%.

**A sudden break in that gradual pattern demands an explanation.** If one bin is far
emptier than both its neighbours, something is pushing observations out of it. Since
business conditions do not jump, that something is probably not economics.

### 4.4 Why bin width is a real decision, not a display setting

This is easy to underestimate, and it turned out to matter a great deal.

The same data plotted with different bin widths tells different stories.

**Bins too wide.** Suppose the real effect lives in the range −0.5% to 0%, but you use bins
5 percentage points wide. Then the bin running from −5% to 0% contains the affected
companies *and* thousands of unaffected ones. The signal is diluted to nothing. You have
averaged away the very thing you were looking for.

**Bins too narrow.** Now use bins 0.01 percentage points wide. Each bin holds a handful of
companies. Counts of 3 and 7 in neighbouring bins look like a dramatic difference, but with
numbers that small, that is just randomness. Every bin becomes noise and everything looks
like a discontinuity.

**There is no single correct width.** It depends on how much data you have and how narrow
the real effect is, and you do not know the second one in advance.

**So what I did about it.** I refused to pick one. Every statistical test in this project
runs at three bin widths — 0.0025, 0.005, and 0.01 — and all three are always reported.
This does two things:

1. It removes the question "did you pick the width that flattered your result?"
2. More importantly, it turned out to be *diagnostic*. In Chapter 26 you will see an effect
   that grows steadily as bins get wider, and that pattern is itself a clue about what is
   causing it. I would have missed that entirely with a single width.

### 4.5 Why zero must sit on a bin edge

One more structural point, and the one I was most careful about.

The hypothesis says there is a deficit just *below* zero and a surplus just *above* it. Now
imagine a bin running from −0.25% to +0.25%. That bin straddles zero. It contains both the
missing companies below zero and the extra companies above zero.

Those two effects **cancel out inside the same bar.** The count comes out looking perfectly
normal. You have destroyed the signal before measuring it.

So zero must fall on a boundary *between* two bins, never inside one. In my code, every bin
edge is an exact integer multiple of the bin width, which guarantees zero is always an
edge. An automated test fails if this ever stops being true, including for awkward widths
where the window does not divide evenly.

### In one sentence

A distribution is the pattern of how often each value occurs; a histogram displays it by
counting observations into bins; bin width is a real analytical choice that changes the
answer, which is why I report three; and zero must sit on a bin edge, or the effect being
measured cancels itself out.

---

# PART II — THE RESEARCH QUESTION

---

## Chapter 5 — The hypothesis, stated precisely

### 5.1 The picture

Everything from Part I now combines into one testable claim.

Line up every public company by its profit, measured as a fraction of its size. Count how
many fall in each narrow band. You get a distribution.

**If no one is managing anything,** that distribution should pass smoothly through zero.
The number of companies earning a tiny profit should be close to the number posting a tiny
loss, because nothing economic distinguishes the two.

**If some managers push small losses into small profits,** you should see:

- **A deficit just below zero** — a dip, where companies would have been but no longer are
- **A surplus just above zero** — a bump, where they ended up instead

> **Notch** *(also called a discontinuity)* — a sharp break in an otherwise smooth
> distribution. Here, specifically the dip-then-bump pattern at exactly zero.

The figure `explain_notch.png` in the repository shows both scenarios side by side.

### 5.2 Formal statement

Stating a hypothesis precisely matters, because it fixes in advance what would count as
evidence.

> **Null hypothesis (H₀)** — the "nothing unusual is happening" baseline. Here: the
> distribution is smooth through zero, and any apparent notch is ordinary random variation
> in the counts.

> **Alternative hypothesis (H₁)** — what you are testing for. Here: the count in the bin
> immediately below zero is genuinely lower than its neighbours predict, and the count
> immediately above is genuinely higher.

Chapter 17 explains why tests are framed this way round, with the boring option as the
default.

### 5.3 Two commitments this framing forces

Writing the hypothesis down properly forces two commitments I stuck to.

**Both sides of zero must be reported.** The hypothesis predicts a deficit below *and* a
surplus above. Finding only one is weaker evidence than finding both. It would be easy to
report whichever side looked better and quietly skip the other. I report both, every time,
at every bin width. This turned out to matter: in my results the two sides behave quite
differently.

**The direction is predicted in advance.** I am not looking for "any anomaly at zero." I am
looking for a specific, signed pattern: negative below, positive above. A large effect
pointing the *wrong* way is not support for the hypothesis. In Chapter 26 that distinction
does a lot of work.

### In one sentence

The hypothesis is that the bin just below zero is emptier than its neighbours predict and
the bin just above is fuller, with the null being a smooth distribution — and the
prediction is directional, so a break pointing the other way is not support.

---

## Chapter 6 — The two papers that frame everything

This project is not the first to ask this question. Two papers define the debate, and
understanding both is what turns a replication into a real piece of work.

### 6.1 Burgstahler & Dichev (1997): the original finding

> Burgstahler, D., & Dichev, I. (1997). "Earnings management to avoid earnings decreases
> and losses." *Journal of Accounting and Economics*, 24(1), 99–126.

They examined US companies from 1976 to 1994, built exactly the distribution described
above, and found the notch. Too few companies just below zero, too many just above. They
interpreted it as evidence of earnings management to avoid reporting losses.

The paper became one of the most-cited results in empirical accounting. It is taught. It is
the standard reference for the claim that companies manage earnings around zero.

They also tested a second threshold: zero *change* in earnings from the previous year, on
the theory that managers avoid reporting a decline as well as a loss. I did not test that
second threshold. It is the most natural extension of this project and I say so in
Chapter 31.

### 6.2 Durtschi & Easton (2005): the critique

> Durtschi, C., & Easton, P. (2005). "Earnings Management? The Shapes of the Frequency
> Distributions of Earnings Metrics Are Not Evidence Ipso Facto." *Journal of Accounting
> Research*, 43(4), 557–592.

Eight years later, a serious challenge. The title is the argument: the shape of these
distributions is *not evidence by itself*.

Their core point starts from something unavoidable. You cannot compare raw profit across
companies. A million dollars is a triumph for a corner shop and a rounding error for Apple.
So every study in this literature **divides profit by something** — total assets, revenue,
market value — to put companies on a common scale.

Durtschi and Easton showed that **the act of dividing, together with the choice of which
companies end up in the sample, can produce a notch even when no manager did anything.**

Here is one mechanism, simplified enough to follow.

Suppose you scale profit by company size, and suppose small companies tend to be less
profitable and more variable than large ones, which is broadly true. Think about what
dividing does to each group. For a large, stable company, dividing a modest profit by a
huge asset base produces a small ratio, close to zero. For a small, volatile company,
dividing by a tiny asset base produces a large ratio, far from zero.

So the region near zero fills up disproportionately with large stable companies, and the
tails fill up with small volatile ones. The sample near zero is a *different population*
from the sample further out. If those two populations have different natural shapes, the
join between them can produce a kink — and that kink has nothing to do with managers.

Add sample selection on top. Requiring a company to have every data item you need removes
companies non-randomly, and if the removal rate differs on either side of zero, that alone
shifts the shape.

### 6.3 Why this makes the project worth doing

If only the 1997 paper existed, this project would be a replication exercise: run the old
test on new data, report whether it still holds.

The 2005 critique changes the job. Now the question is not just "is the notch there?" but
"if it is there, is it evidence of anything?" That is a harder and more interesting
question, and it dictates the entire design of what follows:

- The sample filters in Part IV exist because sample selection is half the critique.
- The **alternate denominators** check in Chapter 23 tests the scaling half directly.
- The **size** checks in Chapters 24 and 25 test their specific prediction that the effect
  should concentrate among small companies.
- The **cash-flow placebo** in Chapter 26 tests whether whatever produces the break could
  plausibly be earnings management at all.

Every one of those is a deliberate response to a specific argument in the critique.

**On the citations.** I verified both against the publishers' records rather than quoting
from memory. There is also a longer 2009 follow-up by the same two authors in the same
journal; I mention it in the README but do not rely on it, because I did not independently
verify its page numbers.

### In one sentence

A 1997 paper found the notch and read it as earnings management; a 2005 paper argued the
notch can be manufactured by the scaling and the sample selection rather than by managers;
and responding to that critique is what shapes every design decision in this project.

---

# PART III — GETTING THE DATA

---

## Chapter 7 — Where public company data comes from

### 7.1 The SEC and EDGAR

> **SEC (Securities and Exchange Commission)** — the US government agency that regulates
> public companies and stock markets. Its job includes making sure investors get accurate
> information.

Any company whose shares trade publicly in the US must file reports with the SEC. Those
filings go into a public database called **EDGAR**, and anyone can read them for free.
That is not a courtesy; public disclosure is the point of the system.

The two filings that matter here:

> **10-K** — the annual report. Filed once a year, audited, and comprehensive. It contains
> all three financial statements plus a long written discussion of the business and its
> risks.

> **10-Q** — the quarterly report. Filed three times a year (the fourth quarter is covered
> by the 10-K). Shorter, and *unaudited*.

> **Audited** — an independent accounting firm has examined the numbers and issued an
> opinion on whether they fairly represent the company's position. Audited numbers are more
> reliable than unaudited ones.

**I used only 10-K filings.** Chapter 9 explains why, and the reason is more specific and
more important than "because they are audited."

### 7.2 The problem XBRL solved

For most of EDGAR's history, filings were documents. A human could read them; a computer
could not, at least not reliably. Extracting "total assets" from ten thousand differently
formatted documents was a genuinely hard engineering problem, and it is why financial
databases were expensive commercial products.

> **XBRL (eXtensible Business Reporting Language)** — a tagging standard that attaches a
> machine-readable label to every number in a filing.

Instead of a number sitting in a table that a human has to interpret, the filing now says,
in effect: *this number is `Assets`, it is in US dollars, it refers to 31 December 2024,
and it is a point-in-time value.* The SEC began phasing in XBRL requirements around 2009.

This is what makes a project like mine possible without a data licence. It is also the
source of one of my real limitations: **my data cannot go back before the XBRL era**, which
matters in Chapter 28.

### 7.3 The Financial Statement Data Sets

The SEC does one more helpful thing. Rather than making you parse XBRL yourself, it
publishes quarterly bundles that flatten every filing's tagged numbers into plain
tab-separated text files.

> **SEC Financial Statement Data Sets** — quarterly ZIP archives containing every number
> the SEC rendered from XBRL filings in that quarter, as flat text files.

The URL pattern is predictable:

```
https://www.sec.gov/files/dera/data/financial-statement-data-sets/{YYYY}q{Q}.zip
```

So `2025q1.zip` holds every filing processed in the first quarter of 2025. Coverage runs
from 2009 Q1 to the present.

**Why I chose this over a commercial database.** Three reasons. It is free, so anyone can
reproduce my work without a licence. It is the primary source, not a vendor's cleaned
version, so nobody has made silent decisions on my behalf. And it is fully transparent
about its own limits. The cost is that coverage starts in 2009 and only includes companies
that filed electronically with XBRL tags.

### 7.4 Being a good citizen of someone else's server

The SEC publishes a fair-access policy. Automated requests must identify themselves with a
descriptive name and a working contact email in the User-Agent header. Requests without one
get rate-limited or blocked, and reasonably so: this is a public service paid for by
taxpayers, not a free CDN.

I comply, and I read the contact address from an environment variable rather than
hardcoding it. That way the code is correct and polite without publishing a personal email
address in a public repository.

### In one sentence

Public companies file with the SEC, XBRL made those filings machine-readable from about
2009 onward, and the SEC publishes free quarterly bundles of the tagged numbers that this
project downloads directly.

---

## Chapter 8 — The actual files, and how I read 113 million rows

This chapter is the engineering. It matters because "I downloaded some data" hides real
decisions, and because volume forced choices that a smaller project would not face.

### 8.1 What is inside one archive

Each quarterly ZIP contains four files. I used two.

> **`sub.txt`** — *submissions*. One row per filing. Tells you who filed, what form it was,
> and what period it covers.

Useful columns:

| Column | Meaning |
|---|---|
| `adsh` | Accession number — the unique ID of this filing |
| `cik` | Central Index Key — the SEC's permanent ID for the company |
| `name` | Company name |
| `sic` | Industry code (see Chapter 11) |
| `form` | `10-K`, `10-Q`, `8-K`, and so on |
| `period` | The end date of the reporting period |
| `filed` | The date the filing was submitted |

> **CIK (Central Index Key)** — a company's permanent SEC identifier. Unlike a ticker
> symbol, it does not change if the company renames itself or moves exchange. This is what
> I join on.

> **`num.txt`** — *numbers*. One row per individual reported figure. This is the large one,
> roughly 550 MB uncompressed per quarter.

Its columns:

| Column | Meaning |
|---|---|
| `adsh` | Which filing this number came from |
| `tag` | The XBRL name of the concept, e.g. `Assets`, `NetIncomeLoss` |
| `ddate` | The date the number refers to |
| `qtrs` | How many quarters the number spans |
| `uom` | Unit of measure, e.g. `USD` |
| `segments` | Non-empty if this is a breakdown rather than a company total |
| `coreg` | Non-empty if it refers to a co-registrant subsidiary |
| `value` | The number itself |

### 8.2 Three fields that require care

**`qtrs` distinguishes snapshots from periods.** A balance-sheet item like total assets is
a point in time, so it carries `qtrs = 0`. An income-statement item like net income covers
a span, so a full year carries `qtrs = 4`. Getting this wrong would mean, for instance,
pulling one quarter of profit and treating it as the year. I filter explicitly on it.

**`segments` and `coreg` distinguish totals from breakdowns.** A company might report
revenue for the whole business *and* separately for North America, Europe, and Asia. All
four appear in `num.txt`. The segment rows carry a non-empty `segments` value.

**I keep only rows where both `segments` and `coreg` are blank.** Without that filter I
would be mixing company totals with regional subtotals, which would corrupt every number
downstream. This is exactly the kind of detail that is invisible in a summary and fatal in
practice.

**`ddate` is rounded to month end.** The SEC normalises dates. Combined with the fact that
some companies use 52- or 53-week fiscal years that drift by a few days annually, this means
I cannot match dates exactly. I match within a window instead, which Chapter 9 describes.

### 8.3 Why I parsed the file by hand

The obvious approach is `pandas.read_csv`. I did not use it, for three reasons.

**Size.** 550 MB per quarter, 37 quarters, roughly 20 GB of text. Loading a full quarter
into memory and then filtering wastes most of the work, because I need about six tags out
of thousands.

**The `footnote` column breaks naive parsing.** It contains free text written by filers.
Free text can contain quote characters, and a quote character in the wrong place makes a
CSV parser mis-read where fields begin and end, silently.

**Silent skipping is unacceptable.** Most parsers offer an option to skip malformed lines.
That would have meant dropping data without knowing how much or which. In a project whose
whole credibility rests on counting every exclusion, that is exactly backwards.

So I read the file line by line, split on tabs, and check membership in my tag set *before
building anything*. Memory stays flat regardless of file size, and I count malformed lines
explicitly rather than skipping them.

**The result:** 113,203,537 rows scanned across 37 archives, **zero malformed lines**. The
zero is worth stating because it means the count is a verified fact rather than an
assumption.

### 8.4 The tags I extracted

XBRL has thousands of concepts. I needed five, and several of them have more than one tag
in common use, because filers do not all choose the same one.

| Concept | Tags I accept, in priority order |
|---|---|
| Total assets | `Assets` |
| Net income | `NetIncomeLoss`, then `ProfitLoss` |
| Revenue | `Revenues`, then `RevenueFromContractWithCustomerExcludingAssessedTax`, then three older variants |
| Cash flow from operations | `NetCashProvidedByUsedInOperatingActivities`, then the continuing-operations variant |
| Shareholders' equity | `StockholdersEquity`, then the variant including non-controlling interests |

**Why priority order rather than picking one.** If I insisted on `Revenues` only, I would
lose every company that tagged its revenue with the newer contract-revenue concept — which,
after the 2018 revenue standard, is a great many of them. So I take the first available tag
in a stated order.

**And this is itself a finding.** Revenue is the messiest concept, with five plausible tags
and inconsistent use across filers. That inconsistency is the reason the revenue-scaled
sample in Chapter 23 contains different companies than the asset-scaled one, which is a
caveat I raise there rather than burying.

### In one sentence

Each archive holds a submissions file and a much larger numbers file; I parse the numbers
file by hand to keep memory flat and count malformed lines exactly, filtering to
consolidated USD company totals for five concepts, each of which may carry more than one
XBRL tag.

---

## Chapter 9 — Building the panel

### 9.1 What a panel is

> **Panel** *(also called panel data or longitudinal data)* — a dataset with multiple
> subjects observed over multiple time periods.

One row per company per year. Apple 2020, Apple 2021, Apple 2022, Ford 2020, and so on.
Each row is a **firm-year** (or company-year).

> **Firm-year** — one company observed for one fiscal year. It is the unit of analysis in
> this project. When I say "16,018 observations," I mean 16,018 company-year combinations,
> not 16,018 separate companies.

That distinction matters for Chapter 13, where I discuss why it inflates apparent
precision.

### 9.2 The comparative balance sheet, and why it made 10-Ks non-negotiable

Here is the neatest thing in the data pipeline, and the reason for a decision that looks
arbitrary from outside.

To compute my main measure I need two numbers: this year's profit, and the total assets
the company **started** the year with. Chapter 15 explains why the starting figure and not
the ending one. For now, take it as given.

The obvious approach is to fetch this year's filing for the profit, fetch last year's
filing for the assets, and join them. That approach has real problems:

- The company may not have filed last year, or may have filed late
- It may have changed its fiscal year end, so "last year" is not twelve months
- I have to match correctly across two documents, and a mismatch is silent

**But accounting rules solve this for me.** A 10-K must show the **comparative** balance
sheet: last year's figures printed alongside this year's, so readers can see the change.
Both years are in the same audited document, tagged in the same XBRL submission.

So from a single 10-K I get:

- Net income for the year (`qtrs = 4`, date = period end)
- Total assets at the end of the year (`qtrs = 0`, date = period end)
- **Total assets at the start of the year** (`qtrs = 0`, date ≈ one year earlier)

One filing. No join. No risk of pairing the wrong years. And the prior-year number is the
one the company itself presents as its comparative, audited alongside the rest.

**This is why I used only 10-Ks.** It threw away every quarterly filing, which sounds
wasteful — but given that the lagged denominator is the most important measurement decision
in the project (Chapter 15), buying it cleanly was worth the trade.

### 9.3 Matching dates when dates are fuzzy

`ddate` is rounded to month end, and 52/53-week fiscal years drift. So I match with
windows rather than exact equality:

- **Current year** — the fact's date falls within ±20 days of the filing's period end
- **Prior year** — the fact's date falls between 330 and 400 days *before* the period end

The 330-to-400 day window is deliberately generous enough to absorb a 53-week year and
month-end rounding, but tight enough that it cannot accidentally grab a figure from two
years ago.

### 9.4 Removing duplicate filings

The same company-year can appear more than once: an amended filing, or a transition period
when a company changes its fiscal year end. I keep one row per company per fiscal year,
choosing the most recent period end.

This removed only 4 rows out of 31,244, which is a good sign rather than a disappointing
one. It means the upstream logic was already clean, and the deduplication step is a safety
net rather than a workhorse.

### 9.5 Caching, and why the notebooks never hit the SEC

Downloading and parsing 37 archives takes about fifteen minutes and 2 GB of disk. Doing
that every time I wanted to re-run an analysis would be slow and rude to the SEC's servers.

So the pipeline runs in stages, and the cleaned result is saved.

> **Parquet** — a compressed, column-oriented file format for tabular data. Much faster to
> read than CSV and it preserves data types, so a date stays a date.

The finished panel is saved as `data/panel.parquet` and **committed to the repository**.
The raw archives are not — they are gitignored, because 2 GB of downloadable public data
does not belong in version control.

The consequence is the one I care about: **anyone can clone the repository and reproduce
every number in this project without downloading anything from the SEC.** The notebooks
read the cached panel and never touch the network.

### In one sentence

A panel is one row per company per year; I build it from 10-K filings because each one
contains the prior-year balance sheet I need, match fuzzy dates with windows, deduplicate,
and cache the result as parquet so every downstream analysis runs offline.

---

# PART IV — BUILDING THE SAMPLE

---

## Chapter 10 — Why you filter, and why filtering is dangerous

### 10.1 The case for filtering

Not every company belongs in this analysis. A bank's balance sheet works differently from a
manufacturer's. A company with missing data cannot be measured at all. A company with $50k
of total assets produces ratios so extreme they distort everything.

Leaving those in does not make the study more honest. It makes it *less* accurate, because
you end up measuring a mixture of incompatible things.

### 10.2 The case against filtering

Every filter is also an opportunity to cheat, whether or not you intend to.

Suppose I run the test, see a weak result, and think "maybe small companies are adding
noise." I raise the size floor. The result improves. I keep the change.

Nothing about that is dishonest in intent. Every step seems reasonable. But the end result
is a number that reflects my search process as much as the data.

> **p-hacking** *(also called data dredging)* — trying many analytical choices and keeping
> the one that produces the most favourable result. It inflates the apparent strength of
> findings and is a major cause of results that fail to replicate.

Sample filters are one of the most common routes to p-hacking, precisely because each
individual choice is defensible.

### 10.3 What I did about it

Three protections.

**1. Filters were fixed before any result existed.** I wrote the filter list, with a
rationale for each, before running the discontinuity test. They come from the literature
and from the structure of the data, not from looking at outputs.

**2. Every exclusion is counted.** Not described — counted. `apply_filters()` in my code
returns two things: the cleaned data, and a **drop log** with one row per filter recording
its name, its reason, the rows before, the rows dropped, the rows after, and the number of
companies remaining. The README table is generated from it, and an automated test verifies
that each step's "before" equals the previous step's "after," so a filter cannot silently
lose rows.

**3. The one arbitrary parameter is tested, not asserted.** The $10m size floor is the
only threshold I chose myself rather than inheriting. So I re-ran the entire analysis at
six different floors from $0 to $500m and reported all of them (Chapter 25). If the result
had moved, you would see it.

### In one sentence

Filtering is necessary because incomparable companies distort the measurement, and
dangerous because each choice is an opportunity to p-hack — so I fixed the filters in
advance, counted every exclusion, and stress-tested the one threshold I picked myself.

---

## Chapter 11 — Every filter, one at a time

Here is the complete exclusion log, followed by the reasoning for each step.

| Step | Dropped | Remaining firm-years | Remaining firms |
|---|---:|---:|---:|
| 0. All 10-K firm-years | — | 57,407 | 10,304 |
| 1. Fiscal years 2016–2025 only | 141 | 57,266 | 10,276 |
| 2. Drop missing industry code | 550 | 56,716 | 10,078 |
| 3. Drop financial firms (SIC 6000–6999) | 14,590 | 42,126 | 7,251 |
| 4. Drop utilities (SIC 4900–4949) | 1,404 | 40,722 | 7,034 |
| 5. Drop missing net income | 703 | 40,019 | 6,979 |
| 6. Drop missing or non-positive lagged assets | 764 | 39,255 | 6,882 |
| 7. Size floor: lagged assets ≥ $10m | 8,011 | 31,244 | 5,366 |
| 8. One filing per firm-year | 4 | **31,240** | **5,366** |

### 11.1 Fiscal years 2016–2025 (dropped 141)

I downloaded filings from 2017 Q1 to 2026 Q1. A fiscal year is only *fully* covered if
every company with that year end had time to file within my window.

A handful of filings in my data cover fiscal years from before 2016 — these are delinquent
filers, companies catching up on years of missed reports. Fiscal 2014 appears exactly once
in my data. One company is not a cross-section; including it would make the phrase "fiscal
years 2014–2025" technically true and substantively misleading.

So I restrict to the range that is properly covered, and say so.

### 11.2 Missing industry code (dropped 550)

> **SIC code (Standard Industrial Classification)** — a four-digit number classifying what
> a company does. 2834 is pharmaceutical preparations. 5812 is eating places. 6021 is
> national commercial banks.

I need it for the next two filters. No code, no way to apply them.

### 11.3 Financial firms, SIC 6000–6999 (dropped 14,590)

This is the largest single exclusion — about a quarter of the data — so it deserves the
most explanation.

**The problem: "total assets" means something structurally different for a bank.**

For a manufacturer, assets are the things it uses to make money: factories, machines,
inventory, the money customers owe it. Profit comes from *using* those assets.

For a bank, assets are mostly *loans it has made*. The bank's business is lending money and
collecting interest. Its assets are the loans themselves.

The consequence is a scale difference so large it breaks comparability. A bank might hold
$100 in assets for every $1 of annual profit. A software company might hold $2 in assets
for every $1 of profit. Both are healthy. But if I divide profit by assets for both, the
bank's ratio is tiny and the software company's is large — and that difference reflects
industry structure, not performance.

**Why this specifically damages my test.** Remember Chapter 6: the Durtschi–Easton critique
is that mixing populations with different natural scales can create artificial shape
effects. Including banks would mean the region near zero is a blend of two populations
whose ratios are naturally distributed very differently. Any kink at the join would be my
own construction.

Excluding financial firms is standard in this literature, and I did it for the standard
reason. The count is in the log so nobody has to take my word for how much it removed.

### 11.4 Utilities, SIC 4900–4949 (dropped 1,404)

> **Rate regulation** — for utilities like electricity and water, a government body sets
> the prices customers pay, typically calibrated to let the utility earn a specified rate
> of return.

If a regulator effectively sets your profit, your earnings are mechanically smooth near a
target, for reasons that have nothing to do with management discretion. Utilities are a
different data-generating process.

This exclusion is conventional but genuinely optional, and I treated it that way: it is a
flag in my code that can be switched off, and the drop log records it either way.

### 11.5 Missing net income (dropped 703)

No numerator, no observation. The most mechanical filter in the list.

### 11.6 Missing or non-positive lagged assets (dropped 764)

Two problems handled together.

**Missing** is straightforward — no denominator, no ratio.

**Non-positive** is more interesting. If total assets were zero, dividing produces infinity.
If total assets were negative, which is rare and usually indicates a data error, the sign of
the whole ratio flips. A company with a $5m loss and −$10m of assets computes to +0.5,
landing it on the *profit* side of zero. In a study about which side of zero companies fall
on, that is not a small problem. So non-positive denominators come out.

### 11.7 Size floor: lagged assets at least $10m (dropped 8,011)

> **Size floor** — a minimum company size required to enter the sample.

**Why any floor at all.** Very small denominators produce extreme ratios. A company with
$50,000 of assets and a $30,000 loss has a ratio of −60%. Dozens of such companies can
dominate the shape of a distribution built from thousands of normal ones.

Worse, these are exactly the companies Durtschi and Easton identify as the source of the
artifact. Leaving them in means the critique applies most strongly to my own work.

**Why $10m.** It is small enough to keep genuine small-cap companies — $10m in assets is a
modest business, not a large one — while removing shells and near-dormant entities.

**Why you should not simply trust that choice.** You should not, and I do not ask you to.
This is the only threshold I picked myself, so Chapter 25 re-runs the entire analysis at
six floors from $0 to $500m. The result barely moves. That check is what makes the choice
defensible; the reasoning alone would not be enough.

### 11.8 One filing per firm-year (dropped 4)

Described in Chapter 9.4. A safety net that caught almost nothing, which is the outcome you
want from a safety net.

### In one sentence

Nine filters take 57,407 raw firm-years to 31,240, the largest being financial firms whose
balance sheets are not comparable, and every one is counted in a log rather than described
in prose.

---

## Chapter 12 — The analysis window

### 12.1 What it is

After all the filters, one more restriction applies at test time: I only examine companies
whose scaled profit falls within **±10%**.

```
16,018 firm-years fall inside the window
15,222 firm-years fall outside it
```

Nearly half the data sits outside, so this deserves an explanation.

### 12.2 Why it is not a filter

The nine steps in Chapter 11 are *sample-quality* filters. They remove observations that do
not belong in the study at all — wrong industry, unusable data, distorting size.

The ±10% window is different in kind. It is a statement of **what is being studied**.

The hypothesis is about behaviour *near* zero. A manager whose company is on track for a
40% return on assets is not weighing whether to cross into profit; they crossed months ago.
Those companies are not part of the phenomenon, and including them would add thousands of
irrelevant observations to a test about the two bins touching zero.

Because it is a different kind of decision, I report it separately in my drop log rather
than burying it among the sample filters. It is honest about the fact that it is a choice.

### 12.3 Could the window be cherry-picked?

In principle, yes, and this is a fair question to ask of any windowed analysis. If I had
tried ±5%, ±10%, and ±20% and reported whichever gave the best answer, that would be
p-hacking.

I did not. The ±10% window was fixed in advance, and it is the conventional choice in this
literature. And the structure of my test limits how much the window could matter anyway:
the neighbour-based test in Chapter 18 depends only on the *three bins around zero*, which
are identical no matter where the window ends. Widening or narrowing the window changes
which bins appear in the chart, not the z-statistic for the bin below zero.

### In one sentence

The ±10% window is not a data-quality filter but a statement that the study is about
behaviour near zero; it was fixed in advance, it is conventional, and the main test depends
only on the three bins around zero regardless of it.

---

## Chapter 13 — Pooling, and why it makes my p-values optimistic

### 13.1 The issue

My panel has 31,240 firm-years from 5,366 companies. That is **5.82 years per company** on
average. Apple appears roughly nine times. Ford appears roughly nine times.

> **Pooling** — treating every firm-year as a separate observation, regardless of which
> company it came from.

### 13.2 Why that is a problem

Statistical tests assume observations are **independent** — that knowing one tells you
nothing about another.

Company-years violate this badly. If Apple was profitable in 2020, it was very likely
profitable in 2021. The same management, business model, industry, and cost structure
persist. The observations are correlated within a company.

The consequence: **31,240 correlated observations contain less information than 31,240
independent ones would.** My tests treat them as independent, so they credit me with more
precision than I actually have.

**In practical terms, my p-values are somewhat too small** — the results look a bit more
certain than they are.

### 13.3 Why I pooled anyway

Three reasons.

**It is the standard in this literature.** Both framing papers pool. Doing something
different would make my numbers not directly comparable to theirs.

**The alternatives have their own problems.** I could keep one year per company, which
would cut the sample to about 5,400 observations — and given that my result is already
marginal, that loss of power would make the test unable to detect anything. Or I could use
a statistical correction for clustering, which is the right answer but is not standard in
this specific literature and would make comparison harder.

**It does not change the conclusion.** My headline finding is a null. Pooling makes
p-values *smaller*, which biases toward finding significance. So if anything, correcting
for it would make my null *more* null. The bias runs in the direction that makes my
conclusion safer, not shakier.

### 13.4 The real point

The reason I lead with this rather than hiding it is that **stating a limitation you could
have concealed is how you establish that the ones you did not state are not hiding
either.** If I say "5.82 years per company, so my p-values are optimistic" before anyone
asks, the rest of my reporting becomes more credible.

### In one sentence

Companies appear 5.82 times on average and those observations are not independent, which
makes my p-values somewhat too small — I pooled anyway because it is standard, the
alternatives cost more than they fix, and the bias runs toward significance while my
finding is a null.

---

# PART V — THE MEASUREMENT

---

## Chapter 14 — Why you have to divide, and what by

### 14.1 Raw profit is useless for comparison

Two companies both report $1 million of profit.

- A neighbourhood restaurant chain with $3 million in assets
- Walmart, with roughly $250 billion in assets

The restaurant chain had an excellent year. Walmart had a catastrophe so severe it would
make international news. Same number, opposite meanings.

So raw net income cannot be compared across companies, and a distribution of raw net income
would be meaningless — dominated by company size rather than by performance.

### 14.2 Scaling

> **Scaling** *(also called normalising or deflating)* — dividing a number by a measure of
> size so that companies of different sizes can be compared.

Divide each company's profit by its own size and you get a ratio that means the same thing
everywhere: profit per dollar of size.

For the restaurant chain: $1m ÷ $3m = 0.33, or 33%.
For Walmart: $1m ÷ $250bn = 0.000004, or 0.0004%.

Now the numbers say what actually happened.

### 14.3 The main measure

> **ROA (return on assets)** — net income divided by total assets. The standard measure of
> how efficiently a company turns its asset base into profit.

```
ROA  =  net income for the year  ÷  total assets
```

This is my main measure, with one crucial refinement about *which* total assets, which is
the whole of Chapter 15.

### 14.4 But scaling is exactly what the critique attacks

Here is the uncomfortable part. Scaling is unavoidable — you genuinely cannot compare raw
profits. But scaling is also the mechanism Durtschi and Easton identify as capable of
manufacturing the notch.

I cannot escape that by being careful. There is no version of this analysis that avoids
dividing.

**What I can do is test whether my answer depends on the divisor.** That is Chapter 23,
and it produced the most important finding in the project. If the notch appears under every
reasonable scalar, the scaling explanation weakens considerably. If it appears under one
and not others, that is itself the answer.

### In one sentence

Raw profit cannot be compared across companies so it must be divided by a measure of size;
ROA is that measure here; and because scaling is exactly what the critique attacks, testing
whether the result survives a change of divisor is essential rather than optional.

---

## Chapter 15 — The lagged denominator: the most important decision in the project

If I had to defend one technical choice, it is this one. It is also the easiest to get
wrong by accident.

### 15.1 The question

ROA is profit divided by total assets. But a company reports assets at two moments: the
start of the year and the end of the year. Which do you use?

The intuitive answer is the end of the year, because that is the headline figure in this
year's balance sheet. **That answer is wrong**, and the reason is worth understanding
completely.

### 15.2 The contamination

Recall from Chapter 1.3:

```
This year's profit  →  retained earnings  →  equity  →  total assets
```

**End-of-year total assets already contain this year's profit.** The profit flowed into the
balance sheet by the time it was measured.

So if you compute:

```
ROA  =  this year's profit  ÷  end-of-year assets
```

you are dividing profit by something that *includes that same profit*. The profit appears
on both sides of the division.

### 15.3 Why that specifically damages this test

Watch what it does mechanically.

A company has a good year. Profit is high. That profit flows into assets, so the
denominator grows. A bigger denominator makes the ratio smaller. So a high profit gets
divided by an inflated number and comes out lower than it should.

Now a company has a bad year. It loses money. The loss reduces equity, so assets shrink. A
smaller denominator makes the ratio bigger — in this case, more negative than it should be.

**Both directions get pulled toward the middle.** High ratios get pushed down, low ratios
get pushed up. The distribution is compressed toward zero.

That is a disaster for a test about a sharp feature *at* zero. The contamination acts like
a smoothing filter applied exactly where I am trying to detect a break. I would be blurring
the signal before measuring it, and I would not be able to tell whether a missing notch was
absent from the data or erased by my own arithmetic.

### 15.4 The fix

Use the assets the company **started** the year with.

```
ROA  =  net income during year t  ÷  total assets at the end of year t−1
```

> **Lagged** — taken from the previous period. "Lagged assets" means the previous year's
> closing balance sheet, which is the same thing as this year's opening balance sheet.

The starting balance sheet was finalised before any of this year's profit existed. It
cannot contain it. The contamination is gone.

There is also a plain economic logic: you are asking how much profit the company generated
from the resources it *had available* at the start of the year. That is a real question
about performance. Dividing by the ending figure asks something muddled.

### 15.5 How much does it actually matter?

I checked, rather than assuming.

Across my panel:

| Check | Result |
|---|---|
| Firm-years where beginning and ending assets are identical | **0.02%** |
| Median absolute difference in the resulting ROA | **0.0093** |

The two figures are essentially never the same. And the median difference of 0.0093 is
almost two bins wide at my main bin width of 0.005. This is not a rounding difference. It
would shift a large number of companies into different bins, including the bins on either
side of zero that the entire test depends on.

### 15.6 How I protect against getting it wrong

Three layers.

**The data structure makes it natural.** Because I take the prior-year figure from the
comparative column of the same 10-K (Chapter 9.2), the correct number is right there. I do
not have to go looking for it.

**A unit test enforces it.** I built a tiny synthetic dataset where a company has $100 of
assets in year one and $400 in year two, with $20 of profit in year two. The correct ROA is
20 ÷ 100 = 0.20. The wrong one is 20 ÷ 400 = 0.05. The test asserts 0.20. If anyone ever
changes the code to use the ending figure, that test fails immediately.

**Related tests cover the edge cases.** A company's first year has no prior year, so its
lag must be empty rather than wrong. If a company is missing from the data for a year, the
observation from two years ago must *not* silently become the lag. And a lag must never
cross from one company to another. All three are tested.

### In one sentence

End-of-year assets already contain this year's profit, so dividing by them puts the
measured quantity into its own denominator and compresses the distribution toward zero —
exactly where the test looks — so I use beginning-of-year assets, taken from the same
filing's comparative column, and protect the choice with unit tests.

---

## Chapter 16 — The other scalars

For the robustness checks, I built three alternative denominators.

### 16.1 Revenue

```
net income ÷ revenue
```

> **Profit margin** — profit as a percentage of sales. This is what the ratio above is
> normally called.

**Why it is a reasonable alternative.** It measures a different and equally sensible notion
of size: how much business the company does, rather than how much it owns. It is also the
ratio a general audience finds most intuitive.

**Its weakness.** Revenue is the messiest concept in XBRL (Chapter 8.4), with five
plausible tags and inconsistent usage. So the companies with usable revenue are not quite
the same set as the companies with usable assets: 28,332 firm-years have revenue against
31,240 with assets. That difference matters in Chapter 23.

### 16.2 Book equity

```
net income ÷ shareholders' equity at the start of the year
```

> **ROE (return on equity)** — profit as a percentage of the owners' stake. Along with ROA,
> one of the two most common profitability ratios in finance.

Lagged, for exactly the same reason as assets — arguably more so, since profit flows
directly into equity.

**Its weakness.** Equity can be negative, for companies that have accumulated more losses
than capital. Negative denominators flip the sign, so those firm-years are excluded. That
is why this measure has the smallest sample of the three: 7,177 firm-years inside the
window.

### 16.3 Market value of equity — the one I could not do properly

```
net income ÷ (share price × shares outstanding)
```

> **Market capitalisation** — what the stock market says the company is worth: share price
> times the number of shares.

This is arguably the *best* scalar for this purpose, because it is the one measure of size
that is not itself an accounting number. Assets, revenue, and book equity are all produced
by the same accounting system whose outputs I am testing. Market value is set by investors
instead, so it cannot be contaminated by accounting choices in the same way.

**But the SEC flat files contain no share prices.** They are filing data, not market data.

What I did instead, honestly:

1. Used **book equity** as the equity-based scalar on the main sample
2. Tested **market value** on my 300-ticker prototype sample, which does have prices — and
   got only 237 observations inside the window, far too few to conclude anything
3. **Reported this as a documented deviation** in the README, the writeup, and here

The alternative would have been to join company IDs to a market-data source, which is a
real project in itself and one I did not do. What I did not do is quietly drop the check
and leave the impression I had run it.

### 16.4 The placebo variable

```
cash flow from operations ÷ total assets at the start of the year
```

Note carefully: **the same denominator as the main measure.** Only the numerator changes,
from net income to cash flow.

That is deliberate and it is the whole point. If the scaling is manufacturing a notch, it
will manufacture one here too, because the scaling is identical. Chapter 26 explains what
happened.

### In one sentence

Revenue and lagged book equity are the alternative scalars on the main sample, market value
of equity could not be built from SEC filing data and is reported as a documented gap, and
the placebo uses cash flow over the same lagged assets so that only the numerator changes.

---

# PART VI — THE STATISTICS

---

## Chapter 17 — Hypothesis testing, from nothing

This chapter assumes no statistics at all. If you know what a p-value is, skim to
Chapter 18.

### 17.1 The problem statistics solves here

I observe 459 companies in the bin just below zero. I expected about 480. There are 21
fewer than expected.

Is that meaningful, or is it nothing?

The honest answer is that you cannot tell by looking. Counts vary. If you flipped a fair
coin a thousand times you would not get exactly 500 heads, and getting 479 would not mean
the coin was rigged. You need a way to decide whether a gap is bigger than randomness
comfortably produces.

That is what hypothesis testing does. It is a procedure for deciding whether a pattern is
surprising enough to take seriously.

### 17.2 Sampling variation

> **Sampling variation** — the fact that any measurement based on a limited number of
> observations will bounce around, even when nothing is changing underneath.

Concretely. Imagine a world where companies' profits are perfectly smoothly distributed
and no manager touches anything. Even in that world, the count in a given bin would not
land on the theoretical value exactly. Some years it would be a bit above, some a bit
below. That wobble is sampling variation, and it exists no matter how careful you are.

So the question is never "is the count exactly what I expected?" The answer to that is
always no. The question is "is the gap larger than the wobble?"

### 17.3 The two hypotheses, and why the boring one is the default

> **Null hypothesis (H₀)** — the default assumption that nothing unusual is going on. Here:
> the distribution is smooth through zero, and the gap I see is ordinary wobble.

> **Alternative hypothesis (H₁)** — the claim you are testing. Here: the bin below zero is
> genuinely emptier than the smooth pattern implies.

The procedure is deliberately conservative. **You assume the null is true, and only reject
it if the data would be very unlikely under that assumption.**

This feels backwards at first, but the logic is like a criminal trial. You assume innocence
and require strong evidence to convict. The asymmetry is intentional: it makes it hard to
claim a discovery by accident.

Applied here, it means the burden is on me. I do not get to claim earnings management
because the numbers lean that way. I have to show the lean is too large to be chance.

### 17.4 The p-value

> **p-value** — the probability of seeing a result at least as extreme as the one you got,
> *if the null hypothesis were true*.

Read that definition twice, because it is the single most misunderstood idea in statistics.

**p = 0.43** means: if the distribution really were smooth, I would see a gap this big or
bigger about 43% of the time, just from randomness. Completely unremarkable.

**p = 0.001** means: if the distribution really were smooth, I would see a gap this big or
bigger about once in a thousand tries. Either something unusual happened, or the smoothness
assumption is wrong.

> **Significance level** — the threshold below which you call a result significant. By
> long-standing convention it is 0.05, meaning a 1-in-20 chance.

**What a p-value is not.** It is not the probability that the hypothesis is true. It is not
the probability you are wrong. It is a statement about how compatible the data are with the
null, and nothing more. This matters for my results, where two p-values land at 0.051 and
0.057 — just on the wrong side of a line that is itself arbitrary.

### 17.5 Two ways to be wrong

> **False positive (Type I error)** — you conclude something is happening when nothing is.
> The 0.05 threshold means you accept a 5% chance of this.

> **False negative (Type II error)** — you conclude nothing is happening when something is.
> This usually happens when you do not have enough data to detect a real but small effect.

Both are live possibilities in this project, and I try to be honest about each:

- My headline result is not significant. That *could* be a false negative — the effect
  might be real and small, and my sample too small to resolve it. Chapter 28 says so.
- My revenue-scaled result *is* significant. But I ran many specifications, and running
  many tests increases the chance that one comes up significant by luck. Chapter 23
  discusses this.

### 17.6 Significance is not importance

One more distinction. A result can be statistically significant and practically trivial, if
the sample is large enough. Statistical significance answers "is this distinguishable from
zero?" not "is this big enough to matter?"

In my case, even the significant revenue-scaled notch involves a shortfall of about 69
companies out of 13,452. Whether that is *interesting* is a separate judgment from whether
it is *detectable*.

### In one sentence

Hypothesis testing decides whether a pattern is bigger than random wobble by assuming
nothing is happening and asking how surprising the data would be under that assumption;
the p-value measures that surprise; and 0.05 is a convention, not a law of nature.

---

## Chapter 18 — The test itself, worked through completely

### 18.1 The idea in one line

To judge whether a bin is unusual, predict what it should contain from its two neighbours,
and see how far off you are.

### 18.2 Why neighbours

The obvious alternative would be to fit a curve to the whole distribution and compare each
bin to the curve. That requires choosing a functional form, and if you choose wrong you
have invented your own answer.

Using the two adjacent bins avoids that. It makes one minimal assumption: **over a short
stretch, the distribution is roughly straight.** If the count is rising as you move right,
the bin in the middle of three should sit about halfway between its neighbours.

```
expected count in bin i  =  (count in bin i−1  +  count in bin i+1)  ÷  2
```

This is a *local* assumption. It says nothing about the overall shape. That is its
strength — and, as Chapter 26 discovers, also its weakness.

### 18.3 The worked example, with the real numbers

The bin just below zero, at bin width 0.005. This is the bin covering ROA from −0.005 to 0,
meaning companies that lost between 0 and 0.5% of their assets.

**Step 1 — read the three counts.**

| Bin | ROA range | Count |
|---|---|---:|
| The one before | −0.010 to −0.005 | 409 |
| **The one being tested** | **−0.005 to 0** | **459** |
| The one after | 0 to +0.005 | 550 |

**Step 2 — predict the middle from the neighbours.**

```
expected = (409 + 550) ÷ 2 = 959 ÷ 2 = 479.5
```

**Step 3 — measure the gap.**

```
gap = observed − expected = 459 − 479.5 = −20.5
```

So the bin holds 20.5 fewer companies than a smooth curve implies. The sign is negative,
which is the direction the hypothesis predicts.

**Step 4 — decide whether 20.5 is a lot.** That needs the standard error, which is 18.4.

### 18.4 Where the standard error comes from

> **Standard error** — the typical amount a statistic bounces around from randomness alone.
> It is the yardstick you measure a gap against.

The derivation has two pieces.

**Piece one: the bin's own count.** Every company in the window either lands in this bin or
it does not. That is a yes-or-no outcome repeated across N companies.

> **Binomial distribution** — the distribution of the number of "successes" in N
> independent yes-or-no trials each with probability p. Its variance is N·p·(1−p).

> **Variance** — the square of the standard deviation. A measure of spread. Variances of
> independent quantities add, which is why the derivation works in variance units and takes
> a square root at the end.

So the variance of this bin's count is `N·pᵢ·(1−pᵢ)`, where pᵢ is the share of all
observations that land in bin i.

**Piece two: the neighbour average.** The prediction is itself built from two random counts,
so it wobbles too. The combined count in both neighbours has variance
`N·(pᵢ₋₁+pᵢ₊₁)·(1−pᵢ₋₁−pᵢ₊₁)`. But I use the *average* of the two, not the sum — and
halving a quantity quarters its variance, since (½)² = ¼. Hence the one-quarter factor.

**Adding them:**

```
variance = N·pᵢ·(1−pᵢ)  +  ¼·N·(pᵢ₋₁+pᵢ₊₁)·(1−pᵢ₋₁−pᵢ₊₁)

standard error = √variance
```

This is the standard formula in this literature, and I implemented it directly rather than
approximating it.

### 18.5 The z-score

> **z-score** — how many standard errors an observation sits away from its expected value.

```
z = gap ÷ standard error
```

For the bin below zero:

```
z = −20.5 ÷ 25.9 = −0.79
```

**How to read a z-score:**

| \|z\| | Meaning | Roughly corresponds to |
|---|---|---|
| under 1 | Completely ordinary | p above 0.32 |
| 1 to 1.96 | Mildly notable, not significant | p between 0.05 and 0.32 |
| **1.96** | **The 5% significance threshold** | **p = 0.05** |
| over 2.58 | Strong | p under 0.01 |
| over 3.29 | Very strong | p under 0.001 |

So z = −0.79 means the bin is 0.79 standard errors below its prediction. That is the kind
of gap randomness produces constantly. **The direction is right; the size is unremarkable.**

### 18.6 Both sides, every time

I run exactly the same calculation for the bin just above zero. For that bin, at the same
width:

```
observed  = 550
expected  = (459 + 533) ÷ 2 = 496
gap       = +54
z         = +1.95
```

That one is close to the threshold. The two sides behave differently, which is precisely
why I insist on reporting both rather than whichever is more convenient.

### In one sentence

Predict each bin's count from the average of its two neighbours, measure the gap, divide by
a standard error derived from the binomial distribution, and read the result as a z-score —
which for the bin below zero comes to −0.79: right direction, ordinary size.

---

## Chapter 19 — A second test that does not trust the neighbours

### 19.1 Why a second test

The neighbour method assumes the distribution is locally straight. That assumption is
doing real work, and if it is wrong the z-scores are wrong.

So I built a second test that gets its expectation a different way.

### 19.2 The held-out fit

> **Goodness-of-fit test** — compares observed counts against what a model predicts, across
> many bins at once rather than one at a time.

The procedure:

1. Take all 40 bins across the window.
2. **Remove the two bins next to zero** — the ones being tested.
3. Fit a smooth curve (a degree-4 polynomial) through the remaining 38 bins.
4. Use that curve to predict what the two removed bins should contain.
5. Compare observed to predicted using a **chi-square statistic**.

> **Chi-square statistic** — adds up, across bins, the squared difference between observed
> and expected, divided by expected. Large values mean poor fit.

> **Degrees of freedom** — roughly, the number of independent pieces of information in the
> test. It determines how large a chi-square value has to be before it counts as surprising.

**Step 2 is the important one.** Because the curve never saw the bins being tested, it
cannot have been bent to accommodate them. The test is a genuine out-of-sample comparison,
and its 2 degrees of freedom are interpretable in the normal way.

### 19.3 What it found

| Bin width | p-value |
|---|---:|
| 0.0025 | 0.0009 |
| 0.005 | 0.0052 |
| 0.01 | 0.0044 |

All three reject smoothness. On its own that looks like strong support for the hypothesis.

**But look at which side drives it.** Decomposing the statistic, almost all of it comes
from the **surplus above zero**, not from a deficit below. The distribution near zero does
not fit a smooth curve — but the misfit is on the profit side.

That matters because the hypothesis is specifically about a deficit of *losses*. A surplus
of small profits with no matching deficit of small losses is a weaker and more ambiguous
finding, since other things could put extra mass just above zero.

### 19.4 Why having two tests was worth it

The neighbour test and the held-out fit disagree in an informative way. The neighbour test
says "nothing significant below zero, marginal above." The held-out test says "the
smoothness assumption fails, mostly above zero."

Both point the same direction: **whatever is happening near zero is happening on the profit
side, and the loss side looks ordinary.** Two methods reaching a compatible conclusion by
different routes is worth more than either alone.

### In one sentence

A second test fits a smooth curve with the two zero-adjacent bins held out and tests them
against it; it rejects smoothness at all three widths, but the rejection comes almost
entirely from the surplus above zero rather than a deficit below.

---

## Chapter 20 — The three guardrails

These are about not fooling myself, and all three were fixed in code before any result
existed.

### 20.1 Zero always sits on a bin edge

**What.** Every bin boundary is an exact integer multiple of the bin width, so zero is
always a boundary and never falls inside a bin.

**Why.** Explained fully in Chapter 4.5: a bin straddling zero contains both the deficit and
the surplus, which cancel inside the same bar.

**How it is enforced.** I generate edges as integer multiples of the width rather than by
stepping from the left edge. Stepping accumulates floating-point error, and after forty
steps "zero" might be 0.0000000001, which is not zero.

A test checks this across all three widths **and** at deliberately awkward ones like 0.003
and 0.0001, where 0.10 is not an evenly divisible multiple. It also verifies that exactly
one bin is flagged on each side, that a value of exactly 0.0 lands in the bin above, and
that a value of −0.000000001 lands in the bin below.

### 20.2 Three bin widths, always all reported

**What.** Every test runs at 0.0025, 0.005, and 0.01.

**Why.** Explained in Chapter 4.4. Bin width changes the answer, and reporting one invites
the reasonable question of whether it was chosen for its result.

**The unexpected benefit.** Running three widths turned into a diagnostic tool. In
Chapter 26 an effect grows monotonically with bin width, and that *pattern* is evidence
about what is causing it. A single width would have shown me a number with no context.

### 20.3 Both sides of zero, always

**What.** Every result reports the bin below zero and the bin above.

**Why.** The hypothesis predicts both. Reporting one is a way of appearing to find more
than you did.

**Why it mattered here.** My two sides behave differently — the deficit below is
insignificant, the surplus above is marginal. Reporting only the above-zero side would have
made this project look like a positive result. It is not one, and saying so requires
showing both.

### 20.4 The underlying principle

All three are versions of the same idea: **make the decision before you can see which
answer it produces.** Once a choice is made in advance and enforced by a test, it cannot be
quietly revisited when the output is disappointing.

### In one sentence

Zero on a bin edge so the effect cannot cancel itself, three bin widths so the width cannot
be chosen for its result, and both sides of zero so half the prediction cannot be quietly
dropped — all fixed in code before any output existed.

---

## Chapter 21 — What "robustness" means and why four checks

### 21.1 The concept

> **Robustness check** — re-running an analysis under different reasonable choices to see
> whether the conclusion survives.

The motivating idea: any analysis contains dozens of decisions. Which companies, which
scalar, which bin width, which threshold. If the finding only holds under one exact
combination, it is a property of your choices. If it holds across many, it is more likely a
property of the world.

### 21.2 Why these four specifically

Each of mine targets a named alternative explanation, and three of the four come straight
out of the Durtschi–Easton critique.

| Check | Alternative explanation it targets | Chapter |
|---|---|---|
| Alternate denominators | The scaling is creating the notch | 23 |
| Size terciles | The effect is a small-company artifact | 24 |
| Size-floor sensitivity | My own arbitrary threshold is doing the work | 25 |
| Cash-flow placebo | Whatever causes the break is not earnings management | 26 |

The fourth is different in kind from the others and is the one I would defend most strongly.
It does not vary a parameter — it changes the *variable* to one where the hypothesis
predicts nothing should happen.

### 21.3 What a placebo test is

> **Placebo test** — running the same analysis on something the hypothesis says should show
> no effect. If an effect appears anyway, the method is suspect.

The name comes from medicine. To know whether a drug works, you also give some patients an
inert pill. If the sugar pill produces the same improvement, the improvement is not coming
from the drug.

Cash flow is my sugar pill. Chapter 2 established that cash flow contains no accruals and
therefore cannot be moved by revising an estimate. So:

- **Notch in net income but not cash flow** → consistent with accrual-based management
- **Notch in both** → something other than management is producing it

Chapter 26 reports what actually happened, which was neither.

### In one sentence

Robustness means checking whether a conclusion survives different reasonable choices; my
four checks each target a specific alternative explanation, and the fourth is a placebo
test that asks whether the effect appears where the hypothesis says it should not.

---

# PART VII — WHAT I FOUND

---

## Chapter 22 — The main result

### 22.1 The numbers

Net income divided by beginning-of-year total assets. N = 16,018 firm-years from 3,582
companies, fiscal years 2016–2025.

| Bin width | Below zero: observed / expected | z | p | Above zero: observed / expected | z | p |
|---|---|---:|---:|---|---:|---:|
| 0.0025 | 246 / 252.0 | −0.31 | 0.753 | 291 / 252.5 | +1.91 | 0.057 |
| 0.005 | 459 / 479.5 | −0.79 | 0.429 | 550 / 496.0 | +1.95 | 0.051 |
| 0.01 | 868 / 898.5 | −0.87 | 0.383 | 1,083 / 1,017.0 | +1.73 | 0.083 |

The headline figure is `figures/headline_histogram.png`, drawn at the middle width.

### 22.2 What is encouraging

**The sign is correct at every width.** Below zero is always negative; above zero is always
positive. That is the pattern the hypothesis predicts, and getting it three times from
three different binnings is not nothing. If this were pure noise, you would expect the signs
to scatter.

### 22.3 What is not

**The deficit below zero is nowhere near significant.** p-values of 0.753, 0.429, and 0.383
mean that if the distribution were perfectly smooth, I would see gaps this large about 40 to
75 percent of the time. That is not evidence; that is ordinary variation.

**The surplus above zero sits exactly on the threshold.** p-values of 0.057, 0.051, and
0.083 straddle 0.05. Two are just above, one further away.

This is the most uncomfortable place for a result to land, and it is worth being explicit
about why. The 0.05 line is a convention, not a natural boundary. A result at p = 0.051 and
one at p = 0.049 are essentially identical pieces of evidence; only one of them gets called
"significant." Treating 0.051 as a discovery would be exactly the kind of borderline
reasoning that fills the literature with findings that do not replicate.

So I do not. I call it marginal, and I let the robustness checks decide how much weight it
can carry.

### 22.4 The honest summary

**Weak, directionally consistent, not significant.**

If I had stopped here, the fair description would be: "there is a hint of something,
concentrated on the profit side, that does not reach conventional significance." That is
where a less thorough version of this project would have ended.

I did not stop here, and the next four chapters are the reason the conclusion changed.

### In one sentence

At all three bin widths the bin below zero is thinner and the bin above is thicker than
neighbours predict — the predicted pattern — but the deficit below is far from significant
and the surplus above sits exactly on the 0.05 line.

---

## Chapter 23 — Robustness 1: does the answer depend on what you divide by?

This is the most important of the four checks, because it tests the core of the
Durtschi–Easton critique directly.

### 23.1 The design

Same companies. Same years. Same code. Same bin widths. **Only the denominator changes.**

That isolation matters. Any difference in the results cannot be caused by a different time
period, a different filter, or a different method, because none of those changed.

### 23.2 The results

At bin width 0.005:

| Profit divided by | N | z below | p | z above | p |
|---|---:|---:|---:|---:|---:|
| Beginning-of-year assets | 16,018 | −0.79 | 0.43 | +1.95 | 0.051 |
| **Revenue** | 13,452 | **−2.97** | **0.003** | **+4.62** | **<0.001** |
| Beginning-of-year book equity | 7,177 | −1.20 | 0.23 | +1.61 | 0.11 |

And revenue holds up across widths, which rules out a single-binning fluke:

| Bin width | z below | p | z above | p |
|---|---:|---:|---:|---:|
| 0.0025 | −3.31 | 0.0009 | +1.80 | 0.071 |
| 0.005 | −2.97 | 0.003 | +4.62 | <0.001 |
| 0.01 | −3.25 | 0.001 | +3.76 | 0.0002 |

### 23.3 What this means

**Same firms. Same net income. Three divisors. Three different answers.**

Under revenue scaling there is a clean, significant notch in both directions, at all three
bin widths. Under assets, nothing significant. Under book equity, nothing significant.

This is the Durtschi–Easton argument appearing in 2016–2025 data as an empirical fact rather
than a theoretical objection. **The presence of a detectable notch is partly a property of
the scaling choice, not purely of the earnings themselves.**

It also means that a researcher who only ran the revenue specification would report a
strong, publishable finding — and would be reporting something that does not hold under the
other two equally reasonable scalars.

### 23.4 The caveat I volunteer

There are two possible explanations and **I cannot fully separate them.**

**Explanation A — revenue behaves differently as a divisor.** Revenue and assets are
genuinely different quantities, and dividing by one rather than the other reshapes the
distribution in a different way.

**Explanation B — the revenue sample is a different set of companies.** Notice the sample
sizes: 16,018 with assets, 13,452 with revenue. Revenue is the messiest XBRL concept
(Chapter 8.4), and companies without cleanly tagged revenue drop out. If those companies
differ systematically, I am comparing two populations, not two scalars.

Both explanations are consistent with the critique — the critique names scaling *and*
sample selection — but they are different mechanisms, and honesty requires saying I have
not distinguished them. Doing so would need a matched-sample design: restrict to companies
that have all three denominators, then compare. That is the first thing I would run with
more time.

### 23.5 The missing fourth scalar

Market value of equity is absent, for the reason in Chapter 16.3: SEC filing data contains
no share prices. I tested it on the 300-ticker prototype and got 237 observations, which is
too few to inform anything. I report this as a gap rather than presenting three scalars as
though they were the complete set I planned.

### In one sentence

Holding companies, years, and method fixed and changing only the divisor produces three
different answers — revenue gives a clean significant notch at every width, assets and book
equity give nothing — which is the critique arriving as an empirical fact, with the caveat
that the revenue sample is not quite the same set of companies.

---

## Chapter 24 — Robustness 2: is it a small-company effect?

### 24.1 The prediction being tested

Durtschi and Easton argue the artifact is driven by small companies, whose tiny denominators
produce extreme and unstable ratios. That is a specific, falsifiable prediction: **if the
notch is an artifact, it should be strongest among small firms.**

### 24.2 The design

> **Tercile** — one of three equal groups formed by sorting on some quantity. The bottom
> third, middle third, and top third.

I sorted every firm-year by beginning-of-year total assets, split into three equal groups,
and ran the identical test within each.

### 24.3 The results

At bin width 0.005:

| Tercile | Median assets | N | z below | p | z above | p |
|---|---:|---:|---:|---:|---:|---:|
| Small | $196m | 5,340 | −0.25 | 0.80 | +1.38 | 0.17 |
| Medium | $1.5bn | 5,339 | −0.26 | 0.79 | +1.23 | 0.22 |
| Large | $9.6bn | 5,339 | −0.91 | 0.36 | +0.73 | 0.46 |

### 24.4 What this means

**No concentration in small companies.** If anything the mild deficit below zero is largest
in the *biggest* tercile, which is the opposite of the artifact prediction.

That cuts against the specific small-firm mechanism. It does not rescue the management
interpretation, because nothing here is significant, but it does mean this particular
alternative explanation is not supported by my data.

### 24.5 The honest limitation

Splitting into three reduces each group to about a third of the sample, which reduces the
ability to detect anything.

> **Statistical power** — the probability a test detects an effect that is genuinely there.
> Smaller samples have less power.

With nothing significant in any tercile, this check cannot strongly distinguish between
explanations. It is weak evidence against the small-firm story rather than strong evidence
against it, and I would not lean on it hard.

### In one sentence

Splitting by company size shows no concentration of the effect among small firms — if
anything the reverse — which cuts against that specific artifact story, though with nothing
significant in any group the check has limited power.

---

## Chapter 25 — Robustness 3: does my own threshold matter?

### 25.1 Why this check exists

The $10m size floor is the only parameter I chose myself rather than inheriting from
convention or from the data. That makes it the most obvious place for a reader to suspect
I tuned something.

The answer to that suspicion is not an argument. It is a table.

### 25.2 The design

I re-ran the **entire filter chain and test** at six different floors. Not just the test —
the whole pipeline, so every downstream count is correct at each threshold.

### 25.3 The results

At bin width 0.005:

| Floor on lagged assets | Panel N | Window N | z below | z above |
|---|---:|---:|---:|---:|
| $0 (no floor) | 39,242 | 16,480 | −0.72 | +1.93 |
| $1m | 34,941 | 16,386 | −0.82 | +1.95 |
| **$10m (headline)** | 31,240 | 16,018 | −0.79 | +1.95 |
| $50m | 26,315 | 14,929 | −1.09 | +2.08 |
| $100m | 23,782 | 14,193 | −0.74 | +1.85 |
| $500m | 16,572 | 11,384 | −0.75 | +1.46 |

### 25.4 What this means

**Flat.** Across a fifty-fold range of thresholds, z below zero stays between −0.72 and
−1.09. The largest floor removes more than half the panel and moves the statistic by about
0.3 standard errors.

So the $10m choice is not doing any work. I could have picked $1m or $100m and written the
same conclusion. That is exactly what you want to be able to say about a parameter you
chose yourself.

**One small observation worth noting rather than hiding.** At the $50m floor, z above zero
reaches +2.08, which crosses 1.96. If I were hunting for significance I could report that
specification and claim a significant surplus above zero.

I am not going to, and the reason matters. It is one cell out of eighteen. Testing many
specifications and reporting the one that crosses a threshold is precisely the p-hacking
described in Chapter 10.2. The honest reading of this table is that the above-zero
statistic hovers around 1.9 regardless of the floor, occasionally tipping over the line by
chance. Reporting the full table is what makes that reading possible.

### In one sentence

Re-running the entire pipeline at six size floors from $0 to $500m moves the result
hardly at all, so the threshold I chose myself is not driving anything — and the one cell
that crosses the significance line is reported rather than promoted.

---

## Chapter 26 — Robustness 4: the cash-flow placebo

This is the most important chapter in the guide. It is where the project stopped being a
replication and became something with its own finding.

### 26.1 The logic, restated

From Chapter 2: net income contains accruals, which can be moved by revising an estimate.
Cash flow from operations contains no accruals and cannot.

So run the identical test on cash flow, with the identical denominator — beginning-of-year
total assets — changing only the numerator.

**Three possible outcomes, and what each would mean:**

| Outcome | Interpretation |
|---|---|
| Notch in net income, none in cash flow | Effect is specific to accrual earnings. Supports the management story. |
| Notch in both, same direction | Something common to both is producing it. Suspect the scaling or the method. |
| Something else | Would need explaining. |

I expected one of the first two.

### 26.2 What actually happened

| Measure | Bin width | z below | p | z above | p |
|---|---|---:|---:|---:|---:|
| Net income | 0.0025 | −0.31 | 0.75 | +1.91 | 0.057 |
| Net income | 0.005 | −0.79 | 0.43 | +1.95 | 0.051 |
| Net income | 0.01 | −0.87 | 0.38 | +1.73 | 0.083 |
| Cash flow | 0.0025 | +0.45 | 0.65 | −0.58 | 0.56 |
| **Cash flow** | 0.005 | **+2.04** | **0.042** | −1.79 | 0.074 |
| **Cash flow** | 0.01 | **+3.55** | **<0.001** | **−3.59** | **<0.001** |

The third outcome. Cash flow shows a break at zero that is **larger than the one in net
income and points in the opposite direction** — a *surplus* just below zero and a *deficit*
just above.

At the widest bin width it is highly significant in both directions: z = +3.55 and −3.59,
both p below 0.001. The side-by-side figure is `figures/cfo_placebo.png`.

### 26.3 Why this is not the "shared artifact" result

If a common scaling artifact were producing the net income notch, it should push both
measures the *same* way, since both use the same denominator. It does not. The signs are
opposite.

So the simple version of the critique — "the scaling creates the notch" — is not what is
happening here, at least not in this form.

### 26.4 What it actually tells us, which is worse

Here is the real implication, and it took me a while to see it.

**The test's core assumption is failing.**

The neighbour method assumes the distribution is locally straight, so the middle of three
bins should sit near the average of its neighbours. Cash flow from operations cannot have
been managed into an opposite-signed break at zero — there is no accrual mechanism to do
it, and no reason managers would target a zero cash flow anyway.

Yet the test reports a highly significant break there.

So the test produces significant "discontinuities" in data that cannot contain a genuine
one. **And it is the same machinery, applied to the same window with the same denominator,
that produced the marginal z-scores for net income.**

That is why the placebo does not merely fail to confirm the hypothesis. It undermines
confidence in the instrument that produced the headline number.

### 26.5 The clue in the bin-width pattern

Look at how the cash-flow effect changes as bins widen:

```
width 0.0025  →  z = +0.45
width 0.005   →  z = +2.04
width 0.01    →  z = +3.55
```

**It grows monotonically.** That pattern is itself diagnostic.

A genuine knife-edge discontinuity at exactly zero would behave the opposite way. Widening
bins dilutes a narrow feature by mixing it with unaffected neighbours, so the statistic
should *weaken*.

Something that strengthens with width is not a knife-edge feature. It is consistent with
**curvature** in the distribution being mistaken for a break. Here is why. The neighbour
method assumes local straightness. If the curve is actually bending, the average of two
neighbours misses the middle — and wider bins reach further out, into regions where the
curve bends more, so the miss grows. Exactly the pattern observed.

This is the payoff from the guardrail in Chapter 20.2. With a single bin width I would have
had one number and no way to interpret it. Three widths turned a number into a mechanism.

### 26.6 What I cannot claim

To be careful about the limits of this finding:

- I have **not proven** the net income result is spurious. I have shown the method produces
  false positives on a related measure, which is grounds for caution, not a demonstration.
- I have **not identified** what exactly creates the cash-flow break. Curvature is my best
  explanation and the bin-width pattern supports it, but I have not modelled the density to
  confirm it.
- A distribution of cash flow scaled by assets may have genuine structure near zero for
  reasons I have not considered.

What I can say is narrower and still important: **the smoothness null is not safe on this
kind of data, and any result resting on it deserves less weight than its p-value suggests.**

### In one sentence

Cash flow, which cannot be managed through accruals, shows a larger and opposite-signed
break at zero than net income does — growing with bin width in the way curvature would and a
genuine discontinuity would not — which means the test's smoothness assumption is unreliable
here, and the same machinery produced the headline number.

---

## Chapter 27 — Putting it all together

### 27.1 The four findings

**One. The main test is weak and directionally consistent.** The sign is right at every bin
width. The deficit below zero never approaches significance. The surplus above zero sits on
the 0.05 line.

**Two. The result depends on the divisor.** Revenue scaling gives a clean, significant notch
at all three widths. Assets and book equity give nothing. Same companies, same years.

**Three. It is not a small-company artifact.** No concentration in the small tercile, and
flat across size floors from $0 to $500m. The specific mechanism Durtschi and Easton
emphasise is not supported here.

**Four. The placebo breaks the test.** Cash flow shows a larger, opposite-signed break that
cannot be earnings management, growing with bin width in a way that points at curvature
rather than a genuine discontinuity.

### 27.2 The conclusion

**I did not find statistically significant evidence that companies bend earnings to avoid
reporting a loss, in recent SEC filing data.**

The direction matches the classical result, which is worth reporting. But the deficit below
zero is not significant under the headline specification, the one clearly significant
version is denominator-specific, and the placebo shows the method itself generating
significant breaks in data that cannot contain one.

### 27.3 Why this is a real contribution rather than a failure

Read as a **measurement study**, the project answers a different but genuine question:
*how much does this classical result depend on choices that are usually made in passing?*

The answer is: a great deal. The scalar changes whether you find anything. The statistical
null fails on a control variable. Both are things a researcher would want to know before
building on the literature, and neither is visible if you run one specification and report
it.

There is also a structural point. I designed the project so that a null would still be
complete — the plan was always "here is the distribution near zero in this period, here is
how it responds to bin width, scaling, and filters, here is what would have to be true for
the classical result to hold here." That plan produces a finished piece of work regardless
of which way the numbers fall. If I had designed it to only be interesting if the answer was
yes, I would have been under quiet pressure to find a yes.

### 27.4 What would have changed my mind

Worth stating explicitly, because a hypothesis you cannot imagine rejecting is not being
tested.

I would have concluded the effect was real if **all three** of the following held:

1. A deficit below zero significant at all three bin widths
2. Surviving all three denominators
3. **Absent** from the cash-flow placebo

I got none of the three. I would also have wanted the effect not to grow monotonically with
bin width, for the reason in Chapter 26.5.

### In one sentence

The direction matches the classical result but the magnitude does not reach significance,
the one significant version depends on the divisor, and the placebo shows the method
producing false breaks — so the honest conclusion is a null, reported as a measurement
study of how much the classical finding depends on choices usually made in passing.

---

# PART VIII — HONESTY

---

## Chapter 28 — Limitations

Every one of these is in the README and the writeup as well. Stating limitations before
being asked is how you establish that the ones you did not state are not being hidden.

### 28.1 Observations are not independent

Covered fully in Chapter 13. Companies appear 5.82 times on average, and a company
profitable last year is likely profitable this year. My tests treat firm-years as
independent, so **my p-values are somewhat too small** and the results look slightly more
certain than they are.

The bias runs toward finding significance, and my headline finding is a null, so correcting
for it would make the null more null rather than less.

### 28.2 The period is 2016–2025 only

This is the limitation I would raise first if someone asked what is missing.

The original result was found on 1976–1994 data. Mine covers 2016–2025. Those are
different eras, and several things changed in between:

> **Sarbanes-Oxley Act (2002)** — US legislation passed after the Enron and WorldCom
> scandals. It required executives to personally certify financial statements, strengthened
> auditor independence, and added criminal penalties for certification failures.

If Sarbanes-Oxley made earnings management riskier and more costly — which is what it was
designed to do — then the notch may genuinely have faded. **In that case a null today is
*compatible* with Burgstahler and Dichev rather than a refutation of them.** Both could be
correct about their own periods.

**I cannot test this,** and that is the frustrating part. Testing it would mean running the
same analysis decade by decade and looking for a trend. The SEC's structured data begins in
2009, so I cannot reach the pre-Sarbanes-Oxley period at all. It would require a different
data source, which is a separate project.

### 28.3 The null hypothesis is the weak link

This is the deepest methodological limitation, and my own placebo exposed it.

Neighbour-averaging assumes local linearity. Chapter 26 shows that assumption failing badly
on cash flow, and there is no reason to think it holds perfectly for net income either.

**What a better design would do.** Fit a flexible model to the entire density, then test
whether the bins at zero depart from it. That has two advantages over neighbour-averaging:
it uses information from the whole distribution rather than two adjacent bins, and it can
accommodate curvature instead of assuming it away.

It would also allow a **confidence interval** on the size of the notch rather than only a
test against zero, which is more informative. "The deficit is between −3% and +1% of the
expected count" tells you more than "not significantly different from zero."

My held-out polynomial test (Chapter 19) is a step in that direction but only a step: it
tests two bins rather than modelling the density properly.

### 28.4 Coverage and survivorship

> **Survivorship bias** — a distortion caused by studying only the subjects that survived
> some selection process.

My data includes only companies that filed with XBRL tags between 2017 and 2026. Companies
that went bankrupt, were acquired, or deregistered before 2017 never appear.

Why that could matter here specifically: companies that post losses are more likely to
disappear. If the sample systematically under-represents loss-making companies, the region
just below zero is affected more than the region just above. That would push in the
direction of an apparent notch, and I cannot measure how large the effect is.

### 28.5 Revenue tagging is inconsistent

Covered in Chapters 8.4 and 23.4. Revenue has five plausible XBRL tags and filers do not use
them uniformly. The revenue-scaled sample (13,452) is therefore a somewhat different set of
companies than the asset-scaled one (16,018), which means I cannot cleanly separate "revenue
behaves differently as a scalar" from "the revenue subsample is a different population."

### 28.6 Market value of equity was not tested at scale

Covered in Chapter 16.3. SEC filing data contains no share prices. Book equity substitutes
on the main sample; market value was tested only on a 237-observation prototype, which is
far too small to be informative.

### 28.7 10-K only, amendments excluded

I used original annual filings and excluded amended ones (10-K/A) rather than merging them.
An amendment sometimes corrects a material number, so in principle the amended figure is
more accurate. Merging correctly is fiddly — you must match amendment to original and decide
which figures are superseded — and I judged the gain small relative to the risk of
introducing errors. It is a simplification, and I state it as one.

### 28.8 What I am not limited by

Worth noting, since limitation sections can leave the impression that nothing survives:

- **Sample size is adequate.** 16,018 observations in the test window is comparable to the
  original paper's, and enough to detect an effect of the reported magnitude.
- **The data is primary.** Straight from the SEC, not a vendor's cleaned version, so no
  third party has made undocumented decisions on my behalf.
- **Every exclusion is counted.** Nothing left the sample silently.
- **The result is fully reproducible.** The cleaned panel is committed; the notebooks run
  offline and produce every number in this guide.

### In one sentence

The binding limitations are non-independent observations, a period that cannot reach before
2009, a null hypothesis my own placebo showed to be unsafe, and survivorship in the XBRL
era — none of which are fixed by more careful work on the same data.

---

## Chapter 29 — The discipline of not overclaiming

### 29.1 The phrase that is allowed

> **"Consistent with earnings management."**

This is the ceiling of what a distributional test can support, and here is precisely why.

The test detects an **anomaly in the shape of a distribution**. That is all it observes. It
never sees:

- a manager
- a decision
- a journal entry
- a single company's reasoning

If a notch exists, earnings management is *one* explanation. It is not the only one. Others
include the scaling effects of Chapter 6.2, the sample-selection effects of Chapter 28.4,
and whatever produces the cash-flow break in Chapter 26 — which is definitely not earnings
management, and which I still cannot fully explain.

"Consistent with" states that the evidence does not contradict a hypothesis. It does not
claim the hypothesis is established.

### 29.2 The phrase that is banned

> **"Proves managers manipulate earnings."**

Three separate errors packed into five words.

**"Proves."** Statistics does not prove. It quantifies how compatible data are with a
hypothesis. Even p < 0.001 means "this would be rare if nothing were happening," not "this
is settled."

**"Manipulate."** Implies wrongdoing. Earnings management, as defined in Chapter 3.1, is
legal and takes place inside the rules. Using the language of fraud to describe legal
discretion is a serious mischaracterisation.

**"Managers."** Attributes an aggregate pattern to individual intent. Even a real notch
across 16,018 firm-years would say nothing about any particular manager.

I do not use this phrasing, and if someone described my result that way I would correct
them.

### 29.3 Why this matters beyond etiquette

Three practical reasons.

**It is what the evidence supports.** Claiming more than you can defend is the fastest way
to lose credibility with anyone who checks.

**It protects the null.** If I would not accept "proves management" as a conclusion from a
positive result, I equally cannot accept "proves there is no management" from my null. My
result is "I did not find evidence," not "there is no effect." Absence of evidence is not
evidence of absence — particularly with a marginal result and acknowledged limitations.

**It is testable by a reader.** Anyone can search my README, writeup, and this guide for
overclaiming language. I ran that check myself: the only occurrences of "proves" in this
document are in the sentence explaining why I never use it, and in describing what the
placebo showed about the *method* rather than about managers.

### 29.4 Applying it to the actual result

Written out carefully:

> In 16,018 firm-years of SEC filing data from fiscal years 2016–2025, the distribution of
> net income scaled by beginning-of-year total assets shows a deficit immediately below
> zero and a surplus immediately above at all three bin widths tested. Neither is
> statistically significant under the headline specification. The pattern is **consistent
> with** earnings management to avoid reporting losses, and is also consistent with several
> alternative explanations that the robustness checks cannot rule out. A cash-flow placebo
> test shows the statistical method producing significant breaks in a measure that cannot
> plausibly be managed, which reduces the weight that can be placed on the headline result.

Long, hedged, and accurate. That is what the evidence supports.

### In one sentence

"Consistent with earnings management" is the ceiling because the test sees a distribution
and never a decision; "proves managers manipulate earnings" packs three errors into five
words; and the same discipline applies to my null, which means "I did not find evidence,"
not "there is no effect."

---

# PART IX — HOW IT IS BUILT

---

## Chapter 30 — The code

### 30.1 Stack and scale

Python 3.13, with pandas and numpy for data handling, scipy for the statistical
distributions, matplotlib for figures, and pyarrow for parquet. Roughly **3,200 lines**
across `src/` and `tests/`, with **35 unit tests**.

Repository: `github.com/riddhi-shedge/earnings-discontinuity`

### 30.2 Layout

```
src/     sec_loader       downloads and reduces the 37 quarterly archives
         panel            the filters, the drop log, the scaled variables
         binning          bin edges — enforces zero-on-a-boundary
         discontinuity    the neighbour test, z-statistics, chi-square
         plotting         the publication figures
         build_panel      one command to rebuild the cached panel
         export_*         PDF, dashboard, deck and explainer exporters
notebooks/  01_explore · 02_main_test · 03_robustness
data/    panel.parquet (committed), drop_log.csv, result tables
figures/ headline histogram and robustness figures — PNG, SVG and PDF
tests/   35 unit tests
```

The separation is deliberate. Loading, filtering, binning, and testing are four different
concerns, and keeping them apart means I can unit-test binning without touching the SEC
files, and re-run a test without re-parsing 20 GB.

### 30.3 The drop log as a first-class object

The most important design decision in the codebase.

`apply_filters()` does not return just the cleaned data. It returns a tuple:

```python
clean_panel, drop_log = apply_filters(raw)
```

The drop log is a table with one row per filter, recording its name, its written rationale,
rows before, rows dropped, rows after, and companies remaining.

Three consequences:

1. **The README table is generated from it,** not typed by hand. The documentation cannot
   drift from what the code did.
2. **A test verifies the chain is arithmetically consistent** — each step's "before" must
   equal the previous step's "after." A filter cannot silently lose rows.
3. **Adding a filter without documenting it is awkward,** because the function signature
   requires a rationale string. The structure enforces the discipline rather than relying
   on me remembering.

### 30.4 What the 35 tests actually protect

Tests that only confirm code runs are not worth much. These target the specific ways this
analysis can be silently wrong.

**Zero-on-a-boundary.** Parameterised across all three bin widths and awkward extras like
0.003 and 0.0001, where the window is not an even multiple. Also checks that exactly one bin
is flagged on each side of zero, that a value of exactly 0.0 lands in the bin above, and
that −0.000000001 lands in the bin below.

**The lagged denominator.** A synthetic company with $100 of assets in year one and $400 in
year two, earning $20 in year two. The test asserts ROA is 0.20, not 0.05. If anyone ever
switches to the end-of-year figure, this fails immediately. Companion tests confirm that a
company's first year has no lag, that a *gap* year does not silently become the lag, and
that lags never cross between companies.

**Drop-log accounting.** The chain consistency check described above.

**Does the test actually detect a notch?** This is the one I would point at if asked how I
know the statistics are right. I generate 200,000 random observations from a smooth
distribution, then move half the observations from the bin below zero into the bin above —
injecting a notch of known size. The test asserts the method detects it strongly in both
directions (z below −5, z above +5).

**And the mirror: does it stay quiet when it should?** On smooth random data with no
injected notch, the test asserts |z| stays below 3. A method that fires on clean data would
be useless.

Together those two are the closest thing to a proof that the implementation works: it finds
what is there, and it does not find what is not.

### 30.5 Reproducibility

Four things make this genuinely reproducible rather than nominally so.

**The cleaned panel is committed.** `data/panel.parquet` is in the repository, so the
notebooks run without downloading 2 GB from the SEC. Anyone can verify every number in this
guide by cloning and running.

**Raw archives are gitignored.** 2 GB of public downloadable data does not belong in version
control.

**Seeds are fixed.** The random ticker draw uses seed 42; the notebooks set a seed. Anything
random produces the same result every run.

**Versions are pinned.** `requirements.txt` lists exact versions, verified against the
environment the analysis actually ran in.

### 30.6 Other deliverables

The analysis produced more than a result:

- A publication-quality headline figure, plus robustness figures, in PNG, SVG, and vector PDF
- A 4-page writeup and this guide
- A 19-slide presentation with full speaker notes
- An Excel workbook where the histograms are live `COUNTIFS` formulas over the panel, so
  changing a number moves the charts
- A Google Sheets edition where expected counts, z-scores and p-values are live spreadsheet
  formulas, verified to match the Python output to three decimal places

### In one sentence

About 3,200 lines of Python across separated loading, filtering, binning and testing
modules, with a drop log that generates its own documentation and 35 tests that protect the
lagged denominator, the zero-on-a-boundary rule, the exclusion accounting, and the test's
ability to find an injected notch while staying quiet on clean data.

---

# PART X — QUESTIONS AND ANSWERS

---

## Chapter 31 — Questions I expect, with answers

Grouped by theme. Answers are written to be said out loud rather than read.

### About the result

**"So did you find anything?"**

Not a significant result, and that is the honest headline. The direction matched the
prediction at every bin width — fewer small losses, more small profits — but the deficit
below zero was never significant and the surplus above was borderline, right around p equals
0.05. What I did find is more interesting than that: the result depends heavily on what you
divide profit by, and a placebo test on cash flow showed the statistical method itself
producing false breaks. So my conclusion is a measurement one rather than a behavioural one.

**"Isn't a null result a failure?"**

It would be if I had designed the project to only work if the answer was yes. I did not. I
planned for the null from the start, because the alternative is being tempted to torture the
data until something appears. What I ended up with is a complete measurement study: here is
the distribution, here is how it responds to every choice I made, and here is what would
have to be true for the classical result to hold in this sample. And the two findings that
came out of it — the denominator dependence and the placebo failure — are more useful than a
marginal confirmation would have been.

**"Why do you think you didn't find it when the 1997 paper did?"**

Three candidate explanations, and I cannot fully distinguish them. First, period: they used
1976 to 1994, I used 2016 to 2025, and it is plausible the notch genuinely faded after
Sarbanes-Oxley raised the cost of earnings management. Second, method: my placebo suggests
the neighbour-smoothness test is unreliable on this kind of data, which raises a question
about the original test too. Third, sample: XBRL-era filers are a different population from
the Compustat universe of the 1980s. If I had more time the time-trend split is the check I
would run first, but the SEC structured data does not reach before 2009, so it would need a
different source.

**"Which of your findings are you most confident in?"**

The denominator sensitivity. It is a within-sample comparison — same companies, same years,
same code, only the divisor changes — so it is not confounded by period or sample
construction the way a comparison to a 1997 paper would be. And it reproduces at all three
bin widths. The caveat I would add unprompted is that the revenue sample is not quite the
same set of companies, so I cannot separate the scalar effect from a sample effect.

**"Your surplus above zero is p equals 0.051. Isn't that basically significant?"**

It is basically *nothing*, and that is the point. A result at 0.051 and one at 0.049 are
the same piece of evidence; only one gets a label. If I treated 0.051 as a discovery, I
would be doing exactly the borderline reasoning that fills the literature with results that
do not replicate. What makes me comfortable calling it marginal rather than significant is
not the number itself but the context: the other side of zero shows nothing, and the
placebo shows the method generating false positives.

### About the method

**"Explain the test to someone non-technical."**

Line every company up by profit as a percentage of its size, and count how many fall in each
narrow band. For any band, ask: if the pattern were smooth, how many should be here? The
natural answer is the average of the two bands either side. Then compare that to what is
actually there. If a band is much emptier than its neighbours suggest, something unusual is
happening there. The z-score just measures "much" in units of how much random variation you
would expect anyway.

**"Why three bin widths?"**

Because bin width is an analytical choice that changes the answer, and reporting only one
invites the question "did you pick the flattering one?" Too wide smooths the notch away, too
narrow makes every bin noise. Running all three and reporting all three removes the
question. It also turned out to be diagnostic: the cash-flow effect grew steadily with bin
width, which is the signature of curvature rather than a genuine discontinuity. I would
never have spotted that from a single width.

**"Why does zero have to be on a bin edge?"**

Because the whole hypothesis is about a break at exactly zero. If a bin ran from −0.0025 to
+0.0025, the missing losses and the extra profits would land in the same bar and average
each other out. I would be deleting the signal before measuring it. My bin edges are integer
multiples of the width so zero is always a boundary, and there is a test that fails if that
ever changes.

**"Where does the standard error formula come from?"**

Each observation either lands in a given bin or it does not, so counts follow a binomial
distribution, whose variance is N times p times one minus p. The prediction is built from
two neighbouring counts, which are also random, so their variance adds — and because I use
the average of the two rather than the sum, that term gets a factor of one quarter. Add the
two variances and take the square root. It is the standard approach in this literature, and
I also ran a second test that does not depend on the neighbour assumption at all: fit a
smooth curve with the two zero-adjacent bins held out, then test those bins against the fit.

**"How do you know your test actually works?"**

I tested it on data where I know the answer. I take random smooth data, move half the
observations from the bin below zero into the bin above — injecting a notch of known size —
and assert the test detects it strongly in both directions. Then the mirror: on smooth data
with no injected notch, it must not fire. Both are unit tests that run on every change.

**"What would have convinced you the effect was real?"**

A deficit below zero significant at all three bin widths, surviving all three denominators,
and absent from the cash-flow placebo. I got none of the three. I would also have wanted the
effect not to grow monotonically with bin width, because that pattern points at curvature
rather than a break at zero.

### About the data

**"Why SEC data rather than a commercial database?"**

It is free, it is the primary source, and it is fully reproducible by anyone without a
licence, which matters for a project someone might want to check. The trade-off is that it
only goes back to 2009 and covers XBRL-era filers only. That is a real limitation, and it is
one of the candidate explanations for my null.

**"How did you handle the volume?"**

113 million rows across 37 archives. I parse the numbers file by hand rather than with
read_csv, because the files are around 550 MB each and have a free-text footnote field that
breaks naive quoting. Splitting on tabs and filtering to my six tags before materialising
anything keeps memory flat and lets me count malformed lines exactly rather than silently
skipping them. Zero malformed across all 37 quarters, which is a verified fact rather than
an assumption.

**"Why 10-Ks only? Didn't that throw away data?"**

It threw away quarterly filings, yes, but it bought me the thing I most needed. A 10-K shows
last year's balance sheet next to this year's, so one filing gives me both the profit and
the beginning-of-year assets figure I divide by, from the same audited document. No
cross-filing join, no risk of mismatching a company to the wrong prior year. Given that the
lagged denominator is the most important measurement decision in the project, that was worth
the trade.

**"You dropped banks — that's 14,590 observations, a quarter of your data."**

Because total assets does not mean the same thing for them. A bank's assets are its loan
book; an insurer's are its investment portfolio. Both are an order of magnitude larger
relative to earnings than a manufacturer's factories and inventory, so ROA is not comparable
across that boundary. Including them would mean the distribution I am testing is a mixture
of two populations with different natural scales, and a kink at the join between them would
be my own construction rather than a finding. It is standard in this literature, and it is
in the drop log with a count so nobody has to take my word for how much it removed.

**"What about survivorship bias?"**

It is real and I cannot measure it. My data only includes companies that filed with XBRL
tags between 2017 and 2026, so anything that went bankrupt or deregistered before 2017 never
appears. Loss-making companies are more likely to disappear, so the region just below zero
is probably affected more than the region above, which would push toward an apparent notch.
I flag it in the limitations rather than pretending the sample is complete.

### About the critique

**"What's the Durtschi–Easton critique, in one sentence?"**

That a discontinuity in scaled earnings can be produced by the scaling and by sample
selection rather than by managers, so the shape of the distribution is not evidence of
manipulation by itself.

**"How did your design respond to it?"**

Four ways, which map onto my four robustness checks. Alternate denominators test the scaling
directly. Size terciles test their specific prediction that the effect should concentrate in
small firms. Size-floor sensitivity tests whether my own arbitrary cutoff is doing work. And
the cash-flow placebo tests whether whatever produces the break could plausibly be earnings
management at all. Three of the four came back pointing away from a management
interpretation.

**"Did your results support the critique?"**

Partly, and not in the way I expected. The denominator sensitivity supports it directly —
the notch appears under revenue scaling and not under assets or equity. But the size checks
cut against the specific small-firm mechanism they emphasise. And the placebo found
something neither paper predicts: a significant opposite-signed break in cash flow, which
suggests the smoothness assumption itself is unreliable here, independent of scaling.

**"If the method is unreliable, does that invalidate the 1997 paper?"**

I would not go that far, and I want to be careful here. What I showed is that this method
produces a significant break in a control variable on *my* data, in *my* period, with *my*
filters. That is grounds for caution about results resting on the same assumption, including
mine. It is not a demonstration that the original finding was wrong — they had a different
period, a different sample, and a much larger effect. The honest statement is that the null
hypothesis deserves more scrutiny than it usually gets, and I would want to see the placebo
run on their data before saying anything stronger.

### About judgment and process

**"What was the hardest decision?"**

Which denominator to make the headline. Revenue gives the significant, publishable-looking
result. Assets is the convention in this literature, it is what the original paper used, and
it is what I had committed to before seeing any output. I went with assets and reported
revenue as a robustness finding. If I had flipped that after seeing the results, the whole
project would have been a p-hacking exercise with extra steps — and the thing that makes the
denominator finding interesting is precisely that I did not choose the flattering one.

**"What would you do differently?"**

Model the density properly. The neighbour-averaging null is the weak link, and my own
placebo proved it. I would fit a smooth model to the whole distribution and test a break
against that, which would also let me put a confidence interval on the size of the notch
rather than only testing against zero. Second, I would build a matched sample that has all
three denominators available, so I could separate "revenue behaves differently as a scalar"
from "the revenue subsample is a different set of companies." Third, I would try harder on
market value of equity, probably by joining company IDs to a price source.

**"How long did this take, and what was the sequence?"**

I built it in phases with a gate at each one. First a crude 300-ticker prototype to see
whether the effect was even visible — it was not conclusive, but that was the point of doing
it cheaply before committing. Then the reusable modules and the unit tests. Then the SEC
pipeline and the documented sample. Then the main test at all three widths. Then the
robustness checks. Then the writeup and figures. The order matters: the filters and the
guardrails were committed to code before any result existed.

**"What are you most proud of?"**

That the project is honest under pressure. Every exclusion is counted, every specification is
reported, the phrasing never exceeds the evidence, and when the placebo came back pointing
the wrong way I wrote it up as the most interesting finding instead of burying it. The code
enforces the discipline too — the zero-on-a-boundary rule and the lagged denominator are both
protected by tests rather than by my memory.

**"If I gave you this dataset and a week, what else would you look at?"**

The other threshold from the original paper: zero *change* in earnings year over year, which
is a second place managers are said to avoid crossing. It uses the same machinery with a
different variable, so it is a cheap extension and a genuinely independent test. If the notch
appeared there but not at zero profit, that would be interesting; if neither appeared, that
would strengthen the null. After that, the time trend, if I could find a source reaching back
past 2009.

**"What did you learn?"**

Three things. First, decide your filters before you look, because it is the difference
between a study and a fishing trip. Second, plan for a null — I built this so that a clean
"no" would still be a complete piece of work, and it was. Third, build the placebo early.
Cash flow was one extra column of data, and it changed how I read everything else in the
project.

---

## Cheat sheet — every number on one page

**Data pipeline**

- 37 quarterly SEC archives, 2017 Q1 to 2026 Q1
- 113,203,537 fact rows scanned, 0 malformed
- 244,697 total submissions, of which 53,156 annual 10-Ks were used
- About 3,200 lines of Python; 35 unit tests, all passing

**Sample**

- 57,407 raw firm-years → **31,240** after filters, from **5,366** companies
- **16,018** firm-years from **3,582** companies inside the ±10% test window
- Fiscal years 2016–2025; 5.82 years per company on average
- Median beginning-of-year assets: $615m
- Share of firm-years reporting a loss: 50.0%
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

- Lagged and end-of-year assets identical in only 0.02% of firm-years
- Median absolute difference in the resulting ratio: 0.0093, about 2 bins at width 0.005

**Citations — verified against publishers, not quoted from memory**

- Burgstahler, D., & Dichev, I. (1997). *Journal of Accounting and Economics*, 24(1), 99–126.
- Durtschi, C., & Easton, P. (2005). *Journal of Accounting Research*, 43(4), 557–592.

---

## Glossary

**Accrual** — an accounting entry recording revenue or expense before the corresponding cash
moves. The gap between profit and cash is made of accruals, and they are where most
legitimate discretion lives.

**Accrual accounting** — recording revenue when earned and expenses when incurred, rather
than when cash moves. Required for public companies. Contrast with cash accounting.

**Audited** — examined by an independent accounting firm that has issued an opinion on
whether the numbers fairly represent the company's position.

**Balance sheet** — a statement of what a company owns and owes at one exact moment. A
snapshot, not a period.

**Bin** — one interval in a histogram, with a left and a right edge. Written `[left, right)`
because the left edge belongs to the bin and the right edge belongs to the next one.

**Binomial distribution** — the distribution of the number of successes in N independent
yes-or-no trials. Its variance is N·p·(1−p), which is where the standard error comes from.

**Book equity** — assets minus liabilities as reported. Distinct from market equity, which
is share price times shares outstanding.

**Cash flow from operations (CFO)** — cash generated by the company's actual business.
Contains no accruals, which is what makes it a valid placebo.

**Chi-square statistic** — a goodness-of-fit measure summing squared differences between
observed and expected counts, divided by expected.

**CIK (Central Index Key)** — the SEC's permanent identifier for a filing entity. The key
this project joins on.

**Debt covenant** — a condition in a loan agreement, such as staying profitable. Breaching
one can let the lender demand repayment.

**Degrees of freedom** — the number of independent pieces of information in a test.
Determines how large a statistic must be to count as surprising.

**Discontinuity (notch)** — a sharp break in an otherwise smooth distribution. Here, the dip
below zero and bump above it.

**Distribution** — the pattern of how often each value occurs across a group.

**Earnings management** — using legitimate discretion within accounting rules to influence
reported results. Not fraud.

**EDGAR** — the SEC's public database of company filings.

**Firm-year** — one company observed for one fiscal year. The unit of analysis here.

**Fiscal year** — a company's own twelve-month reporting period, which need not match the
calendar year.

**Goodness-of-fit test** — compares observed counts to what a model predicts across many
bins at once.

**Histogram** — a chart of a distribution, drawn by counting observations into bins.

**Income statement** — a statement of what a company earned over a period. Ends in net
income.

**Lagged** — taken from the previous period. "Lagged assets" means the prior year's closing
balance sheet, which is this year's opening one.

**Liabilities** — what a company owes: loans, bonds, unpaid bills.

**Net income** — bottom-line profit after all expenses, interest and tax. The numerator of
this project.

**Null hypothesis (H₀)** — the default assumption that nothing unusual is happening. Assumed
true unless the data are very unlikely under it.

**Panel** — a dataset with multiple subjects observed over multiple periods. One row per
company per year.

**Parquet** — a compressed, column-oriented file format that preserves data types. Used to
cache the cleaned panel.

**p-hacking** — trying many analytical choices and keeping the most favourable result.
Inflates apparent significance.

**Placebo test** — running the same analysis on something that should show no effect. If an
effect appears, the method is suspect.

**Pooling** — treating every firm-year as a separate observation regardless of which company
it came from. Inflates apparent precision.

**p-value** — the probability of a result at least this extreme if the null hypothesis were
true. Not the probability the hypothesis is true.

**Revenue** — total money earned from sales before costs. The top line of the income
statement.

**ROA (return on assets)** — net income divided by total assets. The main measure here,
always with lagged assets.

**ROE (return on equity)** — net income divided by shareholders' equity.

**Sampling variation** — the wobble in any measurement based on a limited number of
observations, present even when nothing underneath is changing.

**Sarbanes-Oxley Act (2002)** — US legislation passed after the Enron and WorldCom scandals,
requiring executive certification of financial statements and strengthening auditor
independence.

**Scaling** — dividing by a measure of size so companies of different sizes can be compared.

**Shareholders' equity** — what would remain for owners after selling everything and paying
every debt. Assets minus liabilities.

**SIC code** — Standard Industrial Classification, a four-digit industry code. Used here to
exclude financial firms (6000–6999) and utilities (4900–4949).

**Significance level** — the threshold below which a result is called significant.
Conventionally 0.05.

**Standard error** — the typical amount a statistic varies from randomness alone. The
yardstick a gap is measured against.

**Statistical power** — the probability a test detects an effect that is genuinely there.
Smaller samples have less.

**Survivorship bias** — distortion from studying only the subjects that survived some
selection process.

**Total assets** — everything a company owns that has value. The standard measure of company
size and the denominator here.

**Type I error (false positive)** — concluding something is happening when nothing is.

**Type II error (false negative)** — concluding nothing is happening when something is.

**Variance** — the square of the standard deviation. A measure of spread. Variances of
independent quantities add.

**XBRL** — the tagging standard that makes numbers in SEC filings machine-readable. Phased
in from around 2009.

**z-score** — how many standard errors an observation sits from its expected value. |z| above
1.96 is the 5% significance threshold.

---

*Riddhi Shedge · UCLA, Statistics and Data Science*
*Code, data and figures: github.com/riddhi-shedge/earnings-discontinuity*
