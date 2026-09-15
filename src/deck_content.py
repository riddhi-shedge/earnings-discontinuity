"""Slide content and speaker notes for the presentation. One source of truth:
``export_deck.py`` renders it to PowerPoint (notes in the notes pane) and to
``slides/speaker_notes.md`` (the same script, readable on its own).

Notes are written to be said out loud: first person, plain words, short sentences.
"""

from __future__ import annotations

AUTHOR = "Riddhi Shedge"
AFFIL = "UCLA · Statistics & Data Science"

SLIDES: list[dict] = [
    {
        "kind": "title",
        "title": "Do companies bend their earnings to avoid reporting a loss?",
        "subtitle": "What I found in 16,018 company-years of SEC filings — and why the honest answer is “not clearly”",
        "notes": (
            "Hi, I’m Riddhi. This is a project I built to answer a question that sounds simple: when a company is "
            "about to report a tiny loss, does it find a way to report a tiny profit instead?\n\n"
            "I’ll walk through what I tested, how I tested it, what came out, and — this is the part I’m most proud of — "
            "the checks I ran to try to break my own result. About ten minutes, then questions.\n\n"
            "One thing up front: the answer is not a clean yes. I’ll show you exactly why, because the reason turned out to "
            "be more interesting than a yes would have been."
        ),
    },
    {
        "kind": "image",
        "kicker": "THE QUESTION",
        "title": "If nobody touched the numbers, there’s no reason for a break at exactly zero.",
        "image": "figures/explain_notch.png",
        "notes": (
            "Here’s the idea in one picture. Take every public company, work out its profit as a fraction of its size, "
            "and line them all up from biggest loss to biggest profit. You get a curve. On the left, that curve is smooth "
            "through zero — a company with a profit of plus 0.1% is about as common as one with minus 0.1%. There’s no "
            "economic reason for a cliff at exactly zero.\n\n"
            "But zero is a psychologically loaded line. A loss, even a tiny one, is a headline. And managers have some "
            "discretion — when to book a write-off, how to estimate a reserve, whether a sale counts this quarter or next. "
            "If some of them use that discretion to turn a tiny loss into a tiny profit, you get the picture on the right: "
            "too few companies just left of zero, too many just right of it. That dip-and-bump is what people call a notch.\n\n"
            "So the question is: is the notch there in real data? And if it is, is it really evidence of what it looks like?"
        ),
    },
    {
        "kind": "bullets",
        "kicker": "WHY THIS IS INTERESTING",
        "title": "A famous 1997 paper found the notch. A 2005 paper argued the test can be fooled.",
        "bullets": [
            ("Burgstahler & Dichev, 1997", "Looked at U.S. companies from 1976–1994 and found exactly this dip-and-bump. "
                                            "It became one of the most cited results in accounting: evidence that companies manage earnings to avoid losses."),
            ("Durtschi & Easton, 2005", "Pushed back hard. Their point: you don’t see raw profit, you see profit divided by something. "
                                         "The dividing — and the choice of which companies make it into the sample — can create a notch "
                                         "on its own, with no manager doing anything."),
            ("So my job had two halves", "First, replicate the classic test on today’s filings. Second, run the checks that would "
                                          "tell a real notch apart from an artifact of the method."),
        ],
        "notes": (
            "Two papers frame this whole project.\n\n"
            "The first, Burgstahler and Dichev in 1997, found the notch in decades of U.S. data and read it as earnings "
            "management. It’s a big result — people teach it.\n\n"
            "The second, Durtschi and Easton in 2005, said: wait. Nobody looks at raw dollars of profit, because a million "
            "dollars means something different to a startup than to Apple. You divide by size first. And they showed that "
            "the act of dividing, plus the choice of which companies end up in your sample, can manufacture a notch even "
            "when nobody is managing anything.\n\n"
            "I found that argument really compelling, and it changed the shape of my project. Replicating the notch is a "
            "small task. Finding out whether it survives the critique is the real one. So every design decision from here "
            "on is about making the test hard to fool."
        ),
    },
    {
        "kind": "image",
        "kicker": "THE DATA",
        "title": "16,018 company-years, taken straight from SEC filings.",
        "image": "figures/explain_funnel.png",
        "notes": (
            "The data comes from the SEC’s Financial Statement Data Sets — free, public flat files that the SEC builds from "
            "every XBRL-tagged filing. I pulled 37 quarterly archives, from early 2017 through the first quarter of 2026, and "
            "scanned about 113 million rows of facts to pick out the handful of line items I needed: net income, total "
            "assets, revenue, cash flow from operations, and the industry code.\n\n"
            "I only used annual 10-K filings, for a specific reason I’ll get to on the next slide.\n\n"
            "This chart is my exclusion log. I start with 57,407 company-years. I drop banks, insurers and utilities, "
            "because their balance sheets don’t compare to a normal company’s — that’s the biggest single cut. I drop "
            "anything missing net income or a starting balance sheet. I drop the very smallest companies, under ten million "
            "in assets, because tiny denominators produce wild ratios. That leaves 31,240. Then the test itself only looks at "
            "companies within ten percent of zero either way, which is 16,018 company-years from about 3,600 companies.\n\n"
            "Every one of those cuts is counted and has a written reason in the repo. I decided the filters before I ran "
            "anything, so I couldn’t tune them to get a result."
        ),
    },
    {
        "kind": "bullets",
        "kicker": "THE ONE MEASUREMENT DECISION THAT MATTERS MOST",
        "title": "I divide each year’s profit by the assets the company started the year with.",
        "bullets": [
            ("Why divide at all", "Raw net income can’t be compared across firms. $1m is enormous for a small company and a "
                                  "rounding error for a giant. Scaling by size puts everyone on the same axis."),
            ("Why beginning-of-year assets", "End-of-year assets already contain this year’s profit. Divide by them and you’ve "
                                             "put the thing you’re measuring into its own denominator — it quietly smooths the "
                                             "exact break you’re looking for."),
            ("Where the number comes from", "Every 10-K shows last year’s balance sheet next to this year’s. I take the prior "
                                            "year straight from the same filing — the company’s own comparative figure, no cross-filing guesswork."),
        ],
        "notes": (
            "If I had to pick one technical decision that makes or breaks this analysis, it’s this one.\n\n"
            "The measure I use is net income divided by total assets — return on assets. But which total assets? Companies "
            "report assets at the end of the year, and that end-of-year number already includes this year’s profit. If I "
            "divide by it, I’m dividing profit by something that contains profit. That mechanically shrinks the very break "
            "I’m looking for. It’s the number one way this analysis goes wrong, and it’s easy to do by accident.\n\n"
            "So I use the assets the company started the year with. And the nice thing about 10-Ks is that each one shows "
            "last year’s balance sheet right next to this year’s, so I get the prior-year figure from the same filing. "
            "That’s actually why I restricted to 10-Ks — quarterly filings don’t give you that.\n\n"
            "I also wrote a unit test that fails if the code ever uses the end-of-year number by mistake."
        ),
    },
    {
        "kind": "image",
        "kicker": "HOW THE TEST WORKS",
        "title": "Each bin is judged against its two neighbours.",
        "image": "figures/explain_neighbor_test.png",
        "notes": (
            "The statistical test is simple enough to explain with three bars.\n\n"
            "I chop the range into bins — here each bin is half a percent of assets wide. For any bin, I ask: if the curve "
            "were smooth, how many companies would I expect here? The natural guess is the average of the two neighbours. "
            "The bin before has 409, the bin after has 550, so I’d expect about 480 in the middle.\n\n"
            "I actually observe 459. That’s 20 fewer than expected — a small dip, in the direction the story predicts.\n\n"
            "Then I ask how surprising 20 is. Counts bounce around by chance, so I divide the gap by its standard error — "
            "that gives a z-score. Roughly: a z of two or more is unusual, a z under one is noise. Here it’s minus 0.79. "
            "Not nothing, but well inside what chance would produce.\n\n"
            "I run this for the bin just below zero and the bin just above zero, because the story needs both: a dip below "
            "and a bump above."
        ),
    },
    {
        "kind": "bullets",
        "kicker": "RULES I SET BEFORE LOOKING",
        "title": "Three commitments, fixed in code before I saw a single result.",
        "bullets": [
            ("Zero always sits on a bin edge", "Never in the middle of a bin. A bin that straddled zero would average the dip "
                                               "and the bump together and hide the thing I’m testing for. Enforced by a unit test."),
            ("Three bin widths, all reported", "0.0025, 0.005 and 0.01. A result that only appears at one width is a choice, "
                                               "not a finding — so I show all three every time."),
            ("Both sides of zero, every time", "The hypothesis predicts a deficit below AND a surplus above. Finding only one "
                                               "is weak evidence, and I say so rather than leading with the better-looking side."),
        ],
        "notes": (
            "This slide is about not fooling myself.\n\n"
            "First: zero sits on a bin boundary, always. My bin edges are exact multiples of the bin width, so zero is "
            "always an edge. If it sat inside a bin, the dip and the bump would land in the same bar and cancel out. There’s "
            "a test in the codebase that fails if that ever changes.\n\n"
            "Second: bin width is a real choice, and it matters. Too wide and you smooth the notch away; too narrow and "
            "every bin is noise. So I don’t pick one. I run everything at three widths and report all three. If a result "
            "appears at only one, that tells you something about the width, not the companies.\n\n"
            "Third: I always report both sides of zero. It would be easy to show just the side that looks better. The "
            "hypothesis needs both, so I show both, every time.\n\n"
            "And underneath all of it: the sample filters were written down before I ran anything, with counts."
        ),
    },
    {
        "kind": "image",
        "kicker": "THE HEADLINE",
        "title": "The dip below zero is there — but it’s small.",
        "image": "figures/headline_histogram.png",
        "notes": (
            "Here’s the main picture. 16,018 company-years, bin width half a percent, zero marked as the black line "
            "sitting on a bin edge. The two orange bars are the bins that touch zero, and the little dashed lines are what "
            "the neighbours predict for each.\n\n"
            "Just below zero: 459 observed, 480 predicted. A dip of about 20. Just above zero: 550 observed, 496 predicted. "
            "A bump of about 54.\n\n"
            "So the shape is the shape the story predicts. Fewer small losses than the curve implies, more small profits. "
            "The direction is right.\n\n"
            "But look at how small it is relative to the bars. This isn’t the dramatic cliff in the textbook picture. The "
            "bump above zero is on the edge of what you’d call significant — p of about 0.05 — and the dip below is not "
            "significant at all. I’ll put the numbers on the next slide."
        ),
    },
    {
        "kind": "table",
        "kicker": "ALL THREE BIN WIDTHS",
        "title": "The direction is right at every width. The significance isn’t.",
        "columns": ["bin width", "below zero: seen / expected", "z", "p", "above zero: seen / expected", "z", "p"],
        "col_widths": [1.5, 2.9, 1.0, 1.0, 2.9, 1.0, 1.8],
        "rows": [
            ["0.0025", "246 / 252", "−0.31", "0.75", "291 / 253", "+1.91", "0.057"],
            ["0.005", "459 / 480", "−0.79", "0.43", "550 / 496", "+1.95", "0.051"],
            ["0.01", "868 / 899", "−0.87", "0.38", "1,083 / 1,017", "+1.73", "0.083"],
        ],
        "caption": "N = 16,018 firm-years. z is the standardized gap between observed and neighbour-predicted counts; |z| > 1.96 is significant at 5%.",
        "notes": (
            "Same test, three bin widths. Read down the columns.\n\n"
            "Below zero, the z is negative at every width — there are fewer small losses than expected. But it never gets "
            "past minus one. The p-values are 0.75, 0.43, 0.38. That’s noise territory.\n\n"
            "Above zero, the z is positive at every width — more small profits than expected — and it sits right at the "
            "edge: 1.91, 1.95, 1.73. p-values of 0.057, 0.051, 0.083. Borderline.\n\n"
            "So here’s my honest read of the main test: weak, consistent in direction, not significant. If I stopped here I "
            "would say ‘there’s a hint of something, mostly on the profit side.’ But I didn’t stop here, and the next three "
            "slides are why."
        ),
    },
    {
        "kind": "image_table",
        "kicker": "ROBUSTNESS 1 — THE SCALAR",
        "title": "Same companies, three ways of scaling, three different answers.",
        "image": "figures/robustness_denominators.png",
        "columns": ["profit divided by…", "N", "below z", "above z"],
        "col_widths": [2.5, 0.8, 0.8, 0.8],
        "rows": [
            ["beginning-of-year assets", "16,018", "−0.79", "+1.95"],
            ["revenue", "13,452", "−2.97", "+4.62"],
            ["beginning-of-year book equity", "7,177", "−1.20", "+1.61"],
        ],
        "caption": "Bin width 0.005. Revenue scaling is significant at all three widths (z below = −3.31 / −2.97 / −3.25).",
        "notes": (
            "Remember the 2005 critique — that the dividing can create the notch. This is me testing exactly that.\n\n"
            "I took the same companies and the same years and just changed what I divide profit by. Divided by assets: "
            "weak, what you saw. Divided by book equity: nothing. Divided by revenue: a clean, significant notch — z of "
            "minus three below zero, plus four and a half above, and it holds at all three bin widths.\n\n"
            "Same firms. Same net income. Three scalars, three answers, and one of them is what you’d call publishable.\n\n"
            "For me this is the single most important finding in the project. It means the notch is partly a property of "
            "the scaling choice, not just of the earnings. Which is precisely what Durtschi and Easton argued twenty years "
            "ago — here it is, showing up empirically in 2016-to-2025 data.\n\n"
            "If someone asks why revenue behaves differently: revenue is tagged inconsistently across filers, so the "
            "revenue-scaled sample is a somewhat different set of firms. I can’t fully separate the scaling effect from "
            "the sample effect, and I say that in the writeup."
        ),
    },
    {
        "kind": "image",
        "kicker": "ROBUSTNESS 2 — COMPANY SIZE",
        "title": "It isn’t a small-company artifact.",
        "image": "figures/robustness_size_floor.png",
        "notes": (
            "The artifact story makes a prediction: if the notch comes from tiny denominators, it should be strongest among "
            "small companies. So I checked two ways.\n\n"
            "First, I split the sample into thirds by size. The z below zero is minus 0.25 for small companies, minus 0.26 "
            "for medium, minus 0.91 for large. No concentration in the small ones — if anything the opposite.\n\n"
            "Second, this chart: I re-ran the whole thing with different minimum sizes, from no floor at all up to half a "
            "billion in assets. Each dot pair is one re-run. They barely move. The result doesn’t depend on whether the "
            "smallest companies are in or out.\n\n"
            "So the ten-million-dollar floor I chose isn’t doing any work, and size isn’t where the action is. That "
            "mildly cuts against the artifact story — though with nothing significant in any size group, this check "
            "can’t distinguish very much."
        ),
    },
    {
        "kind": "image",
        "kicker": "ROBUSTNESS 3 — THE PLACEBO",
        "title": "Cash flow shows a bigger break than earnings does — in the opposite direction.",
        "image": "figures/cfo_placebo.png",
        "notes": (
            "This was the check I was most excited about, and it gave me the most unexpected result.\n\n"
            "The logic: earnings can be nudged through accounting judgment — timing, estimates, accruals. Cash flow from "
            "operations is much harder to nudge that way; cash either came in or it didn’t. So if I run the identical test "
            "on cash flow, scaled by the identical denominator, the management story predicts no notch. If I see a notch "
            "there too, something other than management is creating it.\n\n"
            "Left panel: net income, the weak result you’ve seen. Right panel: cash flow. There’s a break at zero — and "
            "it’s bigger than the earnings one, and it points the other way. A surplus just below zero, a deficit just "
            "above. At the widest bin it’s z of plus 3.5 and minus 3.6, very significant.\n\n"
            "Cash flow can’t have been managed into that shape. So what I’m really seeing is that the test’s core "
            "assumption — that the curve is locally smooth — breaks down in this kind of data. And that same assumption is "
            "what produced the borderline z-scores for earnings. The placebo doesn’t just fail to confirm; it undercuts "
            "the tool.\n\n"
            "One more clue: the cash-flow effect grows steadily as the bins get wider. That’s the fingerprint of curvature "
            "in the distribution being mistaken for a cliff, not of a genuine cliff at zero."
        ),
    },
    {
        "kind": "bullets",
        "kicker": "WHAT I CONCLUDE",
        "title": "No clear evidence that companies bend earnings to dodge a loss — and a useful reason why.",
        "bullets": [
            ("The direction matches the classic result", "Fewer small losses and more small profits than a smooth curve "
                                                          "predicts, at every bin width. But the deficit below zero is never "
                                                          "significant, and the surplus above is borderline."),
            ("The one significant version is denominator-specific", "Scale by revenue and you get a textbook notch. Scale by "
                                                                     "assets or equity and you don’t. Same firms."),
            ("The placebo breaks the test’s own null", "Cash flow shows a larger, opposite-signed ‘discontinuity’ that cannot be "
                                                        "earnings management. Neighbour-smoothness is not a safe assumption here."),
            ("Where a notch appears, ‘consistent with earnings management’ is as far as I can go",
             "This test detects a distributional anomaly. It doesn’t identify a manager, a decision, or an accrual."),
        ],
        "notes": (
            "So, the bottom line, said plainly.\n\n"
            "I did not find statistically significant evidence that companies bend earnings to avoid reporting a loss, in "
            "recent SEC data. The direction matches the famous result — fewer small losses, more small profits — but the "
            "deficit below zero never reaches significance and the surplus above zero is borderline.\n\n"
            "The one version that is clearly significant appears only when I scale by revenue. Same companies, different "
            "denominator, different answer. That’s the critique showing up in the data.\n\n"
            "And the placebo — cash flow, which can’t be managed into shape — shows a bigger break than earnings does. "
            "Which tells me the test itself is picking up curvature, not manipulation.\n\n"
            "I want to be careful about the phrasing, because it’s easy to overclaim here. Where a notch does appear, the "
            "most I can say is that it is consistent with earnings management. This is a test of the shape of a "
            "distribution. It doesn’t see a manager, a decision, or a journal entry. Consistent with is the ceiling."
        ),
    },
    {
        "kind": "bullets",
        "kicker": "LIMITATIONS",
        "title": "What this can’t tell you.",
        "bullets": [
            ("Companies repeat across years", "About 5.8 years per company on average. Those observations aren’t independent, "
                                              "so my p-values are somewhat optimistic."),
            ("The period is 2016–2025 only", "The classic result was on 1976–1994 data. If the notch genuinely faded after "
                                             "Sarbanes-Oxley and XBRL, a null today is compatible with the original finding, not a refutation."),
            ("The null hypothesis is the weak link", "Neighbour-averaging assumes the curve is locally straight. The placebo shows "
                                                     "it isn’t. A stronger design would fit the whole curve and test the break against that."),
            ("Market value of equity wasn’t testable at scale", "SEC flat files carry no share prices. Book equity stands in; market "
                                                                 "value was checked only on a small prototype sample, too small to inform anything."),
        ],
        "notes": (
            "I want to be upfront about what this can’t do.\n\n"
            "Companies appear multiple times — about six years each on average — and those years aren’t independent. My "
            "p-values treat them as if they were, so they’re a bit optimistic. Pooling is the standard choice in this "
            "literature and I say so rather than hide it.\n\n"
            "The period is only 2016 to 2025, because that’s what the SEC’s structured data covers. The original paper "
            "used 1976 to 1994. If the notch really did fade after Sarbanes-Oxley made earnings management riskier, then "
            "finding nothing today is compatible with the original result, not a contradiction of it. This project "
            "doesn’t test that.\n\n"
            "The biggest methodological limitation is the one the placebo exposed: the test assumes the curve is locally "
            "straight, and it isn’t. If I did this again I’d fit a smooth curve to the whole distribution and test the "
            "break against that instead.\n\n"
            "And one honest deviation from my original plan: I wanted to scale by market value of equity too, but SEC "
            "flat files don’t have share prices. I used book equity instead and tested market value only on a small "
            "prototype sample."
        ),
    },
    {
        "kind": "bullets",
        "kicker": "WHAT I LEARNED",
        "title": "What I’d tell someone starting this project.",
        "bullets": [
            ("Decide the filters before you look", "Every exclusion in this project has a count and a reason that I wrote "
                                                   "before running the test. It’s the only way to be sure you didn’t tune the sample to the answer."),
            ("A null result is a result", "I built the project so that a clean ‘no’ would still be complete. It was — and the "
                                          "checks that produced the ‘no’ turned out to be the most interesting part."),
            ("Build the placebo first", "One extra column of data — cash flow — did more to shape my conclusion than every "
                                        "other robustness check combined."),
            ("Next step", "Fit the full distribution and test the break against a proper smooth model; extend the panel back "
                          "before 2009 to test whether the notch faded over time."),
        ],
        "notes": (
            "A few things I’d pass on.\n\n"
            "First, decide your filters before you look at anything. It sounds obvious, but it’s the difference between "
            "a study and a fishing trip. Every company I dropped has a count and a reason that I wrote down first.\n\n"
            "Second, plan for a null. I built this so that if the notch wasn’t there, I’d still have a complete piece of "
            "work: here’s the distribution, here’s how it responds to bin width, scaling, and sample. That’s what I ended "
            "up with, and honestly the checks that produced the null are the most interesting part of the project.\n\n"
            "Third, build the placebo first. Cash flow was one extra column in the data, and it changed how I read "
            "everything else.\n\n"
            "If I had another month: fit the whole distribution with a smooth model and test the break against that, "
            "and extend the data back before 2009 to see whether the notch faded over time. Both are in the writeup as "
            "next steps.\n\n"
            "Thanks — happy to take questions. The code, the data, and every number here are in the repo."
        ),
    },
    {
        "kind": "table",
        "kicker": "APPENDIX A — FULL MAIN RESULTS",
        "title": "Main test with goodness-of-fit statistics.",
        "columns": ["bin width", "N", "below: seen", "below: exp.", "z", "p", "above: seen", "above: exp.", "z", "p", "held-out χ² p"],
        "col_widths": [1.1, 0.9, 1.1, 1.35, 0.8, 0.8, 1.1, 1.35, 0.8, 0.8, 1.4], "font": 11,
        "rows": [
            ["0.0025", "16,018", "246", "252.0", "−0.31", "0.753", "291", "252.5", "+1.91", "0.057", "0.0009"],
            ["0.005", "16,018", "459", "479.5", "−0.79", "0.429", "550", "496.0", "+1.95", "0.051", "0.0052"],
            ["0.01", "16,018", "868", "898.5", "−0.87", "0.383", "1,083", "1,017.0", "+1.73", "0.083", "0.0044"],
        ],
        "caption": "Held-out χ²: a degree-4 polynomial is fitted to the window with the two zero-adjacent bins removed, then those two bins are tested against the fit (2 df). It rejects smoothness, but the rejection is driven by the surplus above zero.",
        "notes": (
            "Backup slide. This is the main test with the goodness-of-fit statistic added. The held-out chi-square fits "
            "a smooth polynomial to everything except the two bins touching zero, then asks whether those two bins fit "
            "the curve. It rejects at every width — but almost entirely because of the surplus above zero, not a "
            "deficit below. That’s consistent with everything else."
        ),
    },
    {
        "kind": "table",
        "kicker": "APPENDIX B — ROBUSTNESS SUMMARY",
        "title": "Every check at bin width 0.005.",
        "columns": ["check", "specification", "N", "below z", "p", "above z", "p"],
        "col_widths": [1.6, 3.7, 1.5, 1.4, 1.1, 1.4, 1.3], "font": 11,
        "rows": [
            ["6.1 denominator", "net income / lagged assets", "16,018", "−0.79", "0.43", "+1.95", "0.051"],
            ["6.1 denominator", "net income / revenue", "13,452", "−2.97", "0.003", "+4.62", "<0.001"],
            ["6.1 denominator", "net income / lagged book equity", "7,177", "−1.20", "0.23", "+1.61", "0.11"],
            ["6.2 size tercile", "small (median $196m)", "5,340", "−0.25", "0.80", "+1.38", "0.17"],
            ["6.2 size tercile", "medium (median $1.5bn)", "5,339", "−0.26", "0.79", "+1.23", "0.22"],
            ["6.2 size tercile", "large (median $9.6bn)", "5,339", "−0.91", "0.36", "+0.73", "0.46"],
            ["6.3 size floor", "$0 → $500m (6 floors)", "16,480 → 11,384", "−0.72 … −1.09", "all > 0.27", "+1.46 … +2.08", "0.04 – 0.14"],
            ["6.4 placebo", "cash flow from operations / lagged assets", "13,719", "+2.04", "0.042", "−1.79", "0.074"],
            ["6.4 placebo", "same, at bin width 0.01", "13,719", "+3.55", "<0.001", "−3.59", "<0.001"],
        ],
        "caption": "Full tables at all three widths: data/robustness_results.csv in the repository.",
        "notes": (
            "Backup slide with every robustness check in one place, at the middle bin width. The full tables at all "
            "three widths are in the repository."
        ),
    },
    {
        "kind": "table",
        "kicker": "APPENDIX C — EXCLUSION LOG",
        "title": "Every filter, in order, with its count.",
        "columns": ["step", "dropped", "remaining firm-years", "remaining firms"],
        "col_widths": [5.2, 1.6, 2.6, 2.6],
        "rows": [
            ["0. raw 10-K firm-years", "—", "57,407", "10,304"],
            ["1. fiscal years 2016–2025 only", "141", "57,266", "10,276"],
            ["2. drop missing industry code", "550", "56,716", "10,078"],
            ["3. drop financial firms (SIC 6000–6999)", "14,590", "42,126", "7,251"],
            ["4. drop utilities (SIC 4900–4949)", "1,404", "40,722", "7,034"],
            ["5. drop missing net income", "703", "40,019", "6,979"],
            ["6. drop missing / non-positive lagged assets", "764", "39,255", "6,882"],
            ["7. size floor: lagged assets ≥ $10m", "8,011", "31,244", "5,366"],
            ["8. one filing per firm-year", "4", "31,240", "5,366"],
            ["analysis window |ROA| ≤ 0.10", "15,222", "16,018", "3,582"],
        ],
        "caption": "Filters were fixed before any result was inspected. Rationale for each is in the README.",
        "notes": (
            "Backup slide: the complete exclusion log. If anyone wants to know where a specific cut came from, this is "
            "it, and the README has a written reason for each row."
        ),
    },
    {
        "kind": "bullets",
        "kicker": "APPENDIX D — REPRODUCIBILITY",
        "title": "Everything here can be re-run from the repository.",
        "bullets": [
            ("Code and data", "github.com/astronomy-lover/earnings-discontinuity — Python 3.13, pandas, numpy, scipy, matplotlib. "
                              "The cleaned panel is committed as parquet, so the notebooks run without touching SEC servers."),
            ("Notebooks", "01_explore (sample + sanity checks), 02_main_test (the test at three widths), 03_robustness (all four checks)."),
            ("Tests", "35 unit tests: lagged-denominator logic, zero-on-a-bin-edge, exclusion-log accounting, and detection of an injected notch."),
            ("Dashboard", "Excel workbook with the panel and live COUNTIFS histograms; Google Sheets edition with the test statistics as live formulas."),
            ("Sources", "Burgstahler & Dichev (1997), J. Accounting & Economics 24(1) 99–126 · Durtschi & Easton (2005), J. Accounting Research 43(4) 557–592 · SEC Financial Statement Data Sets."),
        ],
        "notes": (
            "Last backup slide: where everything lives. The repo has the code, the cleaned data, the notebooks, the "
            "tests, the figures, this deck, and the writeup. Both papers I cited are listed with volume and page numbers "
            "that I verified against the publishers, not from memory."
        ),
    },
]
