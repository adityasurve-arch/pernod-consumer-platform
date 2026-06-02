# Quarter — Behavioral Data Platform

**→ [Live dashboard](https://adityasurve-arch.github.io/pernod-consumer-platform/dashboard.html)**

Quarter is a behavioral data platform for alcohol brands, built from the consumer side of the bar.

---

## The problem

Bars are getting quieter. House parties have stopped being a thing. People my age would rather stay home with reels and Netflix than go out. The new generation isn't drinking less because they hate alcohol. They're drinking less because they've stopped socialising the way the last generation did.

That's a structural problem for an entire industry. Spirits companies have surveys, scanner data, and consultants. What they don't have is a way to watch a 20-year-old in Paris or Lisbon or Vienna actually choose a brand, in real money, at the moment they choose it.

A lot of young consumers aren't lost to the category. They just can't afford premium brands yet. "I'll buy the good stuff when I start working." Brands don't know this because they've never been able to measure it. Quarter is built to close that gap.

---

## How it works

What follows describes the production model. Right now it's a prototype: simulated data and a working dashboard, built to test whether the logic holds before any venues come on board.

Quarter operates a venue network — five partner bars across **Paris, Milan, Barcelona, Vienna, and Lisbon**. Student-dense European cities where premium drinking habits are forming.

When a consumer walks in, they join via a free membership app (Nightlight), verified for legal drinking age and GDPR-compliant. Every drink they order is logged against their member ID: which brand, what category, at what price, with whom, on what day.

Brands get something they've never had before: real revealed-preference data from the consumers who'll define their market in five years.

To make pricing behaviour measurable, prices for tracked brands rotate weekly — at parity with house, at a premium, at a discount. That's how Quarter measures how much price premium a brand can actually carry, in real consumer decisions rather than surveys.

---

## What's in this repo

**A working interactive dashboard** with five analytical views:

* Brand equity by city — where brands win and where they don't
* Vodka head-to-head — competitive share at price parity
* Price elasticity — the actual demand curve, measured in real decisions
* Gen Z trade-up curve — how a 19-year-old becomes a premium drinker over time
* Single-city drill-down — Paris, Milan, Barcelona, Vienna, Lisbon

→ **Live:** [adityasurve-arch.github.io/pernod-consumer-platform/dashboard.html](https://adityasurve-arch.github.io/pernod-consumer-platform/dashboard.html)

**A simulated dataset** — 25,000 members, 541,000 visits, 1.57M logged drinks across five cities, 18 months of behavioral history. Patterns are calibrated to real industry research; methodology is identical to what would run on live POS data in production.

**The code that built it** — three Python scripts that generate the dataset and pre-compute all dashboard metrics. Fully reproducible.

---

**Aditya Surve** · ESCP Business School · aditya.surve@edu.escp.eu
