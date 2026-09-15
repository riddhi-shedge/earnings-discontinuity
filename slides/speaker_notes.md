# Speaker notes — Earnings discontinuity at zero

Riddhi Shedge · UCLA · Statistics & Data Science

The same script that sits in the notes pane of `earnings_discontinuity.pptx`, one section per slide. Written to be said out loud. Roughly ten minutes for slides 1–15; 16–19 are backup.

## Slide 1 — Do companies bend their earnings to avoid reporting a loss?

*TITLE*

Hi, I’m Riddhi. This is a project I built to answer a question that sounds simple: when a company is about to report a tiny loss, does it find a way to report a tiny profit instead?

I’ll walk through what I tested, how I tested it, what came out, and — this is the part I’m most proud of — the checks I ran to try to break my own result. About ten minutes, then questions.

One thing up front: the answer is not a clean yes. I’ll show you exactly why, because the reason turned out to be more interesting than a yes would have been.

## Slide 2 — If nobody touched the numbers, there’s no reason for a break at exactly zero.

*THE QUESTION*

Here’s the idea in one picture. Take every public company, work out its profit as a fraction of its size, and line them all up from biggest loss to biggest profit. You get a curve. On the left, that curve is smooth through zero — a company with a profit of plus 0.1% is about as common as one with minus 0.1%. There’s no economic reason for a cliff at exactly zero.

But zero is a psychologically loaded line. A loss, even a tiny one, is a headline. And managers have some discretion — when to book a write-off, how to estimate a reserve, whether a sale counts this quarter or next. If some of them use that discretion to turn a tiny loss into a tiny profit, you get the picture on the right: too few companies just left of zero, too many just right of it. That dip-and-bump is what people call a notch.

So the question is: is the notch there in real data? And if it is, is it really evidence of what it looks like?

## Slide 3 — A famous 1997 paper found the notch. A 2005 paper argued the test can be fooled.

*WHY THIS IS INTERESTING*

Two papers frame this whole project.

The first, Burgstahler and Dichev in 1997, found the notch in decades of U.S. data and read it as earnings management. It’s a big result — people teach it.

The second, Durtschi and Easton in 2005, said: wait. Nobody looks at raw dollars of profit, because a million dollars means something different to a startup than to Apple. You divide by size first. And they showed that the act of dividing, plus the choice of which companies end up in your sample, can manufacture a notch even when nobody is managing anything.

I found that argument really compelling, and it changed the shape of my project. Replicating the notch is a small task. Finding out whether it survives the critique is the real one. So every design decision from here on is about making the test hard to fool.

## Slide 4 — 16,018 company-years, taken straight from SEC filings.

*THE DATA*

The data comes from the SEC’s Financial Statement Data Sets — free, public flat files that the SEC builds from every XBRL-tagged filing. I pulled 37 quarterly archives, from early 2017 through the first quarter of 2026, and scanned about 113 million rows of facts to pick out the handful of line items I needed: net income, total assets, revenue, cash flow from operations, and the industry code.

I only used annual 10-K filings, for a specific reason I’ll get to on the next slide.

This chart is my exclusion log. I start with 57,407 company-years. I drop banks, insurers and utilities, because their balance sheets don’t compare to a normal company’s — that’s the biggest single cut. I drop anything missing net income or a starting balance sheet. I drop the very smallest companies, under ten million in assets, because tiny denominators produce wild ratios. That leaves 31,240. Then the test itself only looks at companies within ten percent of zero either way, which is 16,018 company-years from about 3,600 companies.

Every one of those cuts is counted and has a written reason in the repo. I decided the filters before I ran anything, so I couldn’t tune them to get a result.

## Slide 5 — I divide each year’s profit by the assets the company started the year with.

*THE ONE MEASUREMENT DECISION THAT MATTERS MOST*

If I had to pick one technical decision that makes or breaks this analysis, it’s this one.

The measure I use is net income divided by total assets — return on assets. But which total assets? Companies report assets at the end of the year, and that end-of-year number already includes this year’s profit. If I divide by it, I’m dividing profit by something that contains profit. That mechanically shrinks the very break I’m looking for. It’s the number one way this analysis goes wrong, and it’s easy to do by accident.

So I use the assets the company started the year with. And the nice thing about 10-Ks is that each one shows last year’s balance sheet right next to this year’s, so I get the prior-year figure from the same filing. That’s actually why I restricted to 10-Ks — quarterly filings don’t give you that.

I also wrote a unit test that fails if the code ever uses the end-of-year number by mistake.

## Slide 6 — Each bin is judged against its two neighbours.

*HOW THE TEST WORKS*

The statistical test is simple enough to explain with three bars.

I chop the range into bins — here each bin is half a percent of assets wide. For any bin, I ask: if the curve were smooth, how many companies would I expect here? The natural guess is the average of the two neighbours. The bin before has 409, the bin after has 550, so I’d expect about 480 in the middle.

I actually observe 459. That’s 20 fewer than expected — a small dip, in the direction the story predicts.

Then I ask how surprising 20 is. Counts bounce around by chance, so I divide the gap by its standard error — that gives a z-score. Roughly: a z of two or more is unusual, a z under one is noise. Here it’s minus 0.79. Not nothing, but well inside what chance would produce.

I run this for the bin just below zero and the bin just above zero, because the story needs both: a dip below and a bump above.

## Slide 7 — Three commitments, fixed in code before I saw a single result.

*RULES I SET BEFORE LOOKING*

This slide is about not fooling myself.

First: zero sits on a bin boundary, always. My bin edges are exact multiples of the bin width, so zero is always an edge. If it sat inside a bin, the dip and the bump would land in the same bar and cancel out. There’s a test in the codebase that fails if that ever changes.

Second: bin width is a real choice, and it matters. Too wide and you smooth the notch away; too narrow and every bin is noise. So I don’t pick one. I run everything at three widths and report all three. If a result appears at only one, that tells you something about the width, not the companies.

Third: I always report both sides of zero. It would be easy to show just the side that looks better. The hypothesis needs both, so I show both, every time.

And underneath all of it: the sample filters were written down before I ran anything, with counts.

## Slide 8 — The dip below zero is there — but it’s small.

*THE HEADLINE*

Here’s the main picture. 16,018 company-years, bin width half a percent, zero marked as the black line sitting on a bin edge. The two orange bars are the bins that touch zero, and the little dashed lines are what the neighbours predict for each.

Just below zero: 459 observed, 480 predicted. A dip of about 20. Just above zero: 550 observed, 496 predicted. A bump of about 54.

So the shape is the shape the story predicts. Fewer small losses than the curve implies, more small profits. The direction is right.

But look at how small it is relative to the bars. This isn’t the dramatic cliff in the textbook picture. The bump above zero is on the edge of what you’d call significant — p of about 0.05 — and the dip below is not significant at all. I’ll put the numbers on the next slide.

## Slide 9 — The direction is right at every width. The significance isn’t.

*ALL THREE BIN WIDTHS*

Same test, three bin widths. Read down the columns.

Below zero, the z is negative at every width — there are fewer small losses than expected. But it never gets past minus one. The p-values are 0.75, 0.43, 0.38. That’s noise territory.

Above zero, the z is positive at every width — more small profits than expected — and it sits right at the edge: 1.91, 1.95, 1.73. p-values of 0.057, 0.051, 0.083. Borderline.

So here’s my honest read of the main test: weak, consistent in direction, not significant. If I stopped here I would say ‘there’s a hint of something, mostly on the profit side.’ But I didn’t stop here, and the next three slides are why.

## Slide 10 — Same companies, three ways of scaling, three different answers.

*ROBUSTNESS 1 — THE SCALAR*

Remember the 2005 critique — that the dividing can create the notch. This is me testing exactly that.

I took the same companies and the same years and just changed what I divide profit by. Divided by assets: weak, what you saw. Divided by book equity: nothing. Divided by revenue: a clean, significant notch — z of minus three below zero, plus four and a half above, and it holds at all three bin widths.

Same firms. Same net income. Three scalars, three answers, and one of them is what you’d call publishable.

For me this is the single most important finding in the project. It means the notch is partly a property of the scaling choice, not just of the earnings. Which is precisely what Durtschi and Easton argued twenty years ago — here it is, showing up empirically in 2016-to-2025 data.

If someone asks why revenue behaves differently: revenue is tagged inconsistently across filers, so the revenue-scaled sample is a somewhat different set of firms. I can’t fully separate the scaling effect from the sample effect, and I say that in the writeup.

## Slide 11 — It isn’t a small-company artifact.

*ROBUSTNESS 2 — COMPANY SIZE*

The artifact story makes a prediction: if the notch comes from tiny denominators, it should be strongest among small companies. So I checked two ways.

First, I split the sample into thirds by size. The z below zero is minus 0.25 for small companies, minus 0.26 for medium, minus 0.91 for large. No concentration in the small ones — if anything the opposite.

Second, this chart: I re-ran the whole thing with different minimum sizes, from no floor at all up to half a billion in assets. Each dot pair is one re-run. They barely move. The result doesn’t depend on whether the smallest companies are in or out.

So the ten-million-dollar floor I chose isn’t doing any work, and size isn’t where the action is. That mildly cuts against the artifact story — though with nothing significant in any size group, this check can’t distinguish very much.

## Slide 12 — Cash flow shows a bigger break than earnings does — in the opposite direction.

*ROBUSTNESS 3 — THE PLACEBO*

This was the check I was most excited about, and it gave me the most unexpected result.

The logic: earnings can be nudged through accounting judgment — timing, estimates, accruals. Cash flow from operations is much harder to nudge that way; cash either came in or it didn’t. So if I run the identical test on cash flow, scaled by the identical denominator, the management story predicts no notch. If I see a notch there too, something other than management is creating it.

Left panel: net income, the weak result you’ve seen. Right panel: cash flow. There’s a break at zero — and it’s bigger than the earnings one, and it points the other way. A surplus just below zero, a deficit just above. At the widest bin it’s z of plus 3.5 and minus 3.6, very significant.

Cash flow can’t have been managed into that shape. So what I’m really seeing is that the test’s core assumption — that the curve is locally smooth — breaks down in this kind of data. And that same assumption is what produced the borderline z-scores for earnings. The placebo doesn’t just fail to confirm; it undercuts the tool.

One more clue: the cash-flow effect grows steadily as the bins get wider. That’s the fingerprint of curvature in the distribution being mistaken for a cliff, not of a genuine cliff at zero.

## Slide 13 — No clear evidence that companies bend earnings to dodge a loss — and a useful reason why.

*WHAT I CONCLUDE*

So, the bottom line, said plainly.

I did not find statistically significant evidence that companies bend earnings to avoid reporting a loss, in recent SEC data. The direction matches the famous result — fewer small losses, more small profits — but the deficit below zero never reaches significance and the surplus above zero is borderline.

The one version that is clearly significant appears only when I scale by revenue. Same companies, different denominator, different answer. That’s the critique showing up in the data.

And the placebo — cash flow, which can’t be managed into shape — shows a bigger break than earnings does. Which tells me the test itself is picking up curvature, not manipulation.

I want to be careful about the phrasing, because it’s easy to overclaim here. Where a notch does appear, the most I can say is that it is consistent with earnings management. This is a test of the shape of a distribution. It doesn’t see a manager, a decision, or a journal entry. Consistent with is the ceiling.

## Slide 14 — What this can’t tell you.

*LIMITATIONS*

I want to be upfront about what this can’t do.

Companies appear multiple times — about six years each on average — and those years aren’t independent. My p-values treat them as if they were, so they’re a bit optimistic. Pooling is the standard choice in this literature and I say so rather than hide it.

The period is only 2016 to 2025, because that’s what the SEC’s structured data covers. The original paper used 1976 to 1994. If the notch really did fade after Sarbanes-Oxley made earnings management riskier, then finding nothing today is compatible with the original result, not a contradiction of it. This project doesn’t test that.

The biggest methodological limitation is the one the placebo exposed: the test assumes the curve is locally straight, and it isn’t. If I did this again I’d fit a smooth curve to the whole distribution and test the break against that instead.

And one honest deviation from my original plan: I wanted to scale by market value of equity too, but SEC flat files don’t have share prices. I used book equity instead and tested market value only on a small prototype sample.

## Slide 15 — What I’d tell someone starting this project.

*WHAT I LEARNED*

A few things I’d pass on.

First, decide your filters before you look at anything. It sounds obvious, but it’s the difference between a study and a fishing trip. Every company I dropped has a count and a reason that I wrote down first.

Second, plan for a null. I built this so that if the notch wasn’t there, I’d still have a complete piece of work: here’s the distribution, here’s how it responds to bin width, scaling, and sample. That’s what I ended up with, and honestly the checks that produced the null are the most interesting part of the project.

Third, build the placebo first. Cash flow was one extra column in the data, and it changed how I read everything else.

If I had another month: fit the whole distribution with a smooth model and test the break against that, and extend the data back before 2009 to see whether the notch faded over time. Both are in the writeup as next steps.

Thanks — happy to take questions. The code, the data, and every number here are in the repo.

## Slide 16 — Main test with goodness-of-fit statistics.

*APPENDIX A — FULL MAIN RESULTS*

Backup slide. This is the main test with the goodness-of-fit statistic added. The held-out chi-square fits a smooth polynomial to everything except the two bins touching zero, then asks whether those two bins fit the curve. It rejects at every width — but almost entirely because of the surplus above zero, not a deficit below. That’s consistent with everything else.

## Slide 17 — Every check at bin width 0.005.

*APPENDIX B — ROBUSTNESS SUMMARY*

Backup slide with every robustness check in one place, at the middle bin width. The full tables at all three widths are in the repository.

## Slide 18 — Every filter, in order, with its count.

*APPENDIX C — EXCLUSION LOG*

Backup slide: the complete exclusion log. If anyone wants to know where a specific cut came from, this is it, and the README has a written reason for each row.

## Slide 19 — Everything here can be re-run from the repository.

*APPENDIX D — REPRODUCIBILITY*

Last backup slide: where everything lives. The repo has the code, the cleaned data, the notebooks, the tests, the figures, this deck, and the writeup. Both papers I cited are listed with volume and page numbers that I verified against the publishers, not from memory.
