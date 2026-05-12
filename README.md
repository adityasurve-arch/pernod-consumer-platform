# Pernod Consumer Behavior Platform

A behavioral data prototype for Pernod Ricard, built by a 23 year old who's exactly the kind of consumer Pernod is trying to figure out.

---

## The thing I keep noticing

Bars are getting quieter. House parties have stopped being a thing. People my age would rather stay home with reels and Netflix than go out. The new generation isn't drinking less because they hate alcohol. They're drinking less because they've stopped socialising the way the last generation did.

That's a structural problem for an entire industry, and it's a strategic problem for Pernod Ricard specifically. Their stock is down roughly fifty percent over two years. Spirits houses are being compared to tobacco companies in serious financial press. Every Gen Z survey says young people are sober-curious, brand-indifferent, and lost to the category.

But here's the thing the surveys miss: a lot of us aren't sober-curious. We just can't afford Absolut yet. I'm a student in Europe. When I want a vodka soda, I'm picking house vodka because alcohol is taxed, premium brands are expensive, and I'm not earning. Plenty of people I know think exactly this way: "I'll buy the good stuff when I start working." We're not lost to Pernod. We're the customers they'll have in five years and they have no idea what we currently think.

Pernod has surveys, scanner data, and consultants. They don't have a way to watch a 22-year-old in Paris or Lisbon or Vienna actually choose a brand, in real money, at the moment they choose it. That's the gap this project is about.

---

## Why I built it instead of just applying

I applied to Pernod eight times. Got rejected each time, with one interview that didn't go well. The standard advice is: tailor your CV harder, write better cover letters, pass the ATS, hope someone reads it among the two hundred other applications.

I got tired of that. I'm not a Pernod analyst, I'm not from the spirits industry, and I'm not going to out-credential the people they actually shortlist. But I am the customer they want to understand. So I sat down with that perspective and built what I'd want to see if I were them.

This project is the result. It's a working prototype of a data infrastructure that would let Pernod see, week by week, what students like me are actually choosing, not what we say in surveys.

---

## How it would actually work

The dashboard is the output. The thing that produces the data is the input, and that's the part of the proposal that matters most.

The idea: Pernod opens five venues, one each in **Paris, Milan, Barcelona, Vienna, and Lisbon**. Student-dense European cities where premium drinking culture is forming. Each venue is partnered, not owned outright. They serve Pernod's full portfolio alongside competitors and house brands, because exclusivity isn't the point.

The point is membership. When a student walks in, they sign up for a free membership card, verified to be of legal drinking age, GDPR-compliant, opt-in. They tap it once when they arrive. Every drink they order during their visit is logged against their member ID: which brand, what category, at what price, with how many friends, on what day, in what mood the night seems to be in.

That's the entire mechanism. A normal bar with a card that opens the tab. The student gets a small reward (a free birthday drink, masterclass access, members-only events) for being identified. Pernod gets something they've never had: real revealed behavior from the consumers who'll define their market in five years.

The venues don't need to be profitable. They're not a hospitality business. They're a data and brand-anchoring asset, financed as marketing infrastructure. The bar P&L target is small loss; the value sits in the data flywheel and the cultural presence in each city.

To make the platform observable, prices for Pernod's headline brands get randomised each week. Absolut at parity with house vodka, sometimes at a premium, sometimes at a discount. That's how you measure how much price premium a brand can actually carry, in real money decisions. It's what the **Price elasticity for Absolut** view in the dashboard shows.

---

## What's in here

**A working interactive dashboard.** Five views, real-feeling data:

* Brand equity by city. Where Absolut wins and where it doesn't.
* Vodka head-to-head. Pernod vs Diageo vs Bacardi at parity prices.
* Price elasticity for Absolut. The actual demand curve.
* Gen Z trade-up curve. How a 19-year-old becomes a 25-year-old premium drinker, over time.
* Single-city drill-down. Paris, Milan, Barcelona, Vienna, Lisbon, each with its own story.

→ **Live dashboard:** [adityasurve-arch.github.io/pernod-consumer-platform/dashboard.html](https://adityasurve-arch.github.io/pernod-consumer-platform/dashboard.html)

**A simulated dataset.** 25,000 student members, 541,000 visits, 1.57 million logged drinks across five European cities, eighteen months of behavioral history. The numbers are synthetic but the patterns are calibrated to real industry research and the methodology is exactly what would be applied to real POS data in production.

**The code that built it.** Three Python scripts that generate the dataset and pre-compute the dashboard's metrics. Reproducible. Anyone can clone this and rebuild the exact same data.

---

## A note on what I am and what I'm not

I'm a masters in management student at ESCP. I'm not from the spirits industry, and I'm not going to pretend I understand it better than the people who've spent twenty years inside it. What I have is a perspective from the other side of the bar. The consumer perspective Pernod is currently guessing about.

This project is what that perspective looks like when it tries to build something useful. The methodology is honest, the limitations are documented, and the strategic questions it asks are the ones I think Pernod is actually facing.

If you want to talk about any of it: aditya.surve@edu.escp.eu

---

**Aditya Surve**


