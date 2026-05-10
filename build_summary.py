"""
Read members.json, visits.json, drinks.json from the same folder.
Pre-compute all dashboard metrics into a small summary.json file.

V2: Adds competitor breakdown (Absolut vs Smirnoff vs Grey Goose vs House) per city.
"""

import json
from datetime import datetime
from collections import defaultdict, Counter

print("Loading data...")
with open("members.json") as f:
    members = json.load(f)
with open("visits.json") as f:
    visits = json.load(f)
with open("drinks.json") as f:
    drinks = json.load(f)

print(f"  {len(members):,} members")
print(f"  {len(visits):,} visits")
print(f"  {len(drinks):,} drinks")

NETWORK_LAUNCH = datetime(2024, 11, 1)
TODAY = datetime(2026, 5, 10)
CITIES = ["Paris", "Milan", "Barcelona", "Vienna", "Lisbon"]
EXPERIMENT_BRANDS = ["Absolut", "Beefeater", "Jameson", "Havana Club"]

members_by_id = {m["member_id"]: m for m in members}

print("\nReconstructing price schedule...")
price_schedule = {}
for d in drinks:
    if d["price_mode"] is None:
        continue
    drink_date = datetime.fromisoformat(d["timestamp"].rstrip("Z"))
    week = (drink_date.date() - NETWORK_LAUNCH.date()).days // 7
    price_schedule[(d["city"], d["brand"], week)] = d["price_mode"]


print("\nComputing overview KPIs...")
overview = {
    "total_members": len(members),
    "total_visits": len(visits),
    "total_drinks": len(drinks),
    "active_members_last_30d": 0,
    "drinks_last_week": 0,
    "avg_drinks_per_visit": round(len(drinks) / len(visits), 2),
    "pernod_share": round(
        100 * sum(1 for d in drinks if d["brand_owner"] == "Pernod") / len(drinks), 1
    ),
}
recent_members = set()
recent_drinks = 0
cutoff_30 = TODAY.timestamp() - 30 * 86400
cutoff_7 = TODAY.timestamp() - 7 * 86400
for v in visits:
    arrival = datetime.fromisoformat(v["arrival_timestamp"].rstrip("Z")).timestamp()
    if arrival >= cutoff_30:
        recent_members.add(v["member_id"])
for d in drinks:
    ts = datetime.fromisoformat(d["timestamp"].rstrip("Z")).timestamp()
    if ts >= cutoff_7:
        recent_drinks += 1
overview["active_members_last_30d"] = len(recent_members)
overview["drinks_last_week"] = recent_drinks


print("Computing brand equity by city...")
brand_equity_by_city = {}
for city in CITIES:
    parity_n, absolut_n = 0, 0
    for d in drinks:
        if d["city"] != city or d["category"] != "vodka":
            continue
        drink_date = datetime.fromisoformat(d["timestamp"].rstrip("Z"))
        week = (drink_date.date() - NETWORK_LAUNCH.date()).days // 7
        mode = price_schedule.get((city, "Absolut", week), "parity")
        if mode == "parity":
            parity_n += 1
            if d["brand"] == "Absolut":
                absolut_n += 1
    brand_equity_by_city[city] = {
        "absolut_share": round(100 * absolut_n / max(1, parity_n), 1),
        "house_share": round(100 * (parity_n - absolut_n) / max(1, parity_n), 1),
        "sample_size": parity_n,
    }


# === NEW V2 SECTION: full vodka competitor breakdown ===
print("Computing competitor breakdown by city...")
competitor_breakdown_by_city = {}
for city in CITIES:
    counter = Counter()
    total = 0
    for d in drinks:
        if d["city"] != city or d["category"] != "vodka":
            continue
        drink_date = datetime.fromisoformat(d["timestamp"].rstrip("Z"))
        week = (drink_date.date() - NETWORK_LAUNCH.date()).days // 7
        mode = price_schedule.get((city, "Absolut", week), "parity")
        if mode == "parity":
            counter[d["brand"]] += 1
            total += 1
    if total == 0:
        continue
    competitor_breakdown_by_city[city] = {
        "Absolut": round(100 * counter.get("Absolut", 0) / total, 1),
        "Smirnoff": round(100 * counter.get("Smirnoff", 0) / total, 1),
        "Grey Goose": round(100 * counter.get("Grey Goose", 0) / total, 1),
        "House vodka": round(100 * counter.get("House vodka", 0) / total, 1),
        "sample_size": total,
    }

print("Computing network competitor share...")
network_counter = Counter()
network_total = 0
for d in drinks:
    if d["category"] != "vodka":
        continue
    drink_date = datetime.fromisoformat(d["timestamp"].rstrip("Z"))
    week = (drink_date.date() - NETWORK_LAUNCH.date()).days // 7
    mode = price_schedule.get((d["city"], "Absolut", week), "parity")
    if mode == "parity":
        network_counter[d["brand"]] += 1
        network_total += 1

network_competitor_share = {
    "Absolut": round(100 * network_counter.get("Absolut", 0) / max(1, network_total), 1),
    "Smirnoff": round(100 * network_counter.get("Smirnoff", 0) / max(1, network_total), 1),
    "Grey Goose": round(100 * network_counter.get("Grey Goose", 0) / max(1, network_total), 1),
    "House vodka": round(100 * network_counter.get("House vodka", 0) / max(1, network_total), 1),
    "sample_size": network_total,
}


print("Computing price elasticity...")
elasticity_buckets = {"discount": [0, 0], "parity": [0, 0], "premium": [0, 0]}
for d in drinks:
    if d["category"] != "vodka":
        continue
    drink_date = datetime.fromisoformat(d["timestamp"].rstrip("Z"))
    week = (drink_date.date() - NETWORK_LAUNCH.date()).days // 7
    mode = price_schedule.get((d["city"], "Absolut", week), "parity")
    elasticity_buckets[mode][0] += 1
    if d["brand"] == "Absolut":
        elasticity_buckets[mode][1] += 1
price_elasticity = {}
for mode, (total, absolut) in elasticity_buckets.items():
    price_elasticity[mode] = {
        "absolut_share": round(100 * absolut / max(1, total), 1),
        "sample_size": total,
    }


print("Computing cohort trade-up...")
tenure_buckets = {"0-3mo": [0, 0], "3-6mo": [0, 0], "6-9mo": [0, 0], "9-12mo": [0, 0], "12mo+": [0, 0]}
for d in drinks:
    if d["category"] != "vodka":
        continue
    m = members_by_id.get(d["member_id"])
    if not m:
        continue
    signup = datetime.strptime(m["signup_date"], "%Y-%m-%d")
    drink_date = datetime.fromisoformat(d["timestamp"].rstrip("Z"))
    months = (drink_date - signup).days / 30
    if months < 3: bucket = "0-3mo"
    elif months < 6: bucket = "3-6mo"
    elif months < 9: bucket = "6-9mo"
    elif months < 12: bucket = "9-12mo"
    else: bucket = "12mo+"
    tenure_buckets[bucket][0] += 1
    if d["brand"] == "Absolut":
        tenure_buckets[bucket][1] += 1
cohort_curve = {}
for bucket, (total, absolut) in tenure_buckets.items():
    cohort_curve[bucket] = {
        "absolut_share": round(100 * absolut / max(1, total), 1),
        "sample_size": total,
    }


print("Computing portfolio share by city...")
portfolio_by_city = {}
for city in CITIES:
    city_drinks = [d for d in drinks if d["city"] == city]
    total = len(city_drinks)
    pernod = sum(1 for d in city_drinks if d["brand_owner"] == "Pernod")
    portfolio_by_city[city] = {
        "pernod_share": round(100 * pernod / max(1, total), 1),
        "total_drinks": total,
    }


print("Computing top brands by city...")
top_brands_by_city = {}
for city in CITIES:
    counter = Counter()
    for d in drinks:
        if d["city"] == city:
            counter[d["brand"]] += 1
    top_brands_by_city[city] = [
        {"brand": b, "drinks": c} for b, c in counter.most_common(10)
    ]


print("Computing day-of-week pattern...")
dow_counts = Counter(v["day_of_week"] for v in visits)
dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
dow_pattern = [{"day": d, "visits": dow_counts[d]} for d in dow_order]


print("Computing demographics by city...")
demographics_by_city = {}
for city in CITIES:
    city_members = [m for m in members if m["signup_city"] == city]
    intl = sum(1 for m in city_members if m["is_international"])
    nat_counter = Counter(m["nationality"] for m in city_members)
    uni_counter = Counter(m["university"] for m in city_members)
    demographics_by_city[city] = {
        "total_members": len(city_members),
        "international_pct": round(100 * intl / len(city_members), 1),
        "top_nationalities": [
            {"nationality": n, "count": c, "pct": round(100*c/len(city_members), 1)}
            for n, c in nat_counter.most_common(5)
        ],
        "top_universities": [
            {"university": u, "count": c} for u, c in uni_counter.most_common(5)
        ],
    }


print("Computing brand equity over time...")
weekly_equity = {city: defaultdict(lambda: [0, 0]) for city in CITIES}
for d in drinks:
    if d["category"] != "vodka":
        continue
    drink_date = datetime.fromisoformat(d["timestamp"].rstrip("Z"))
    week = (drink_date.date() - NETWORK_LAUNCH.date()).days // 7
    mode = price_schedule.get((d["city"], "Absolut", week), "parity")
    if mode != "parity":
        continue
    weekly_equity[d["city"]][week][0] += 1
    if d["brand"] == "Absolut":
        weekly_equity[d["city"]][week][1] += 1
equity_over_time = {}
for city in CITIES:
    series = []
    for week in sorted(weekly_equity[city].keys())[-12:]:
        total, absolut = weekly_equity[city][week]
        if total >= 50:
            series.append({"week": week, "share": round(100 * absolut / total, 1)})
    equity_over_time[city] = series


summary = {
    "metadata": {
        "generated_at": TODAY.isoformat(),
        "network_launch": NETWORK_LAUNCH.isoformat(),
        "cities": CITIES,
        "experiment_brands": EXPERIMENT_BRANDS,
    },
    "overview": overview,
    "brand_equity_by_city": brand_equity_by_city,
    "competitor_breakdown_by_city": competitor_breakdown_by_city,
    "network_competitor_share": network_competitor_share,
    "price_elasticity": price_elasticity,
    "cohort_curve": cohort_curve,
    "portfolio_by_city": portfolio_by_city,
    "top_brands_by_city": top_brands_by_city,
    "dow_pattern": dow_pattern,
    "demographics_by_city": demographics_by_city,
    "equity_over_time": equity_over_time,
}

with open("summary.json", "w") as f:
    json.dump(summary, f, indent=2)

import os
size_kb = os.path.getsize("summary.json") / 1024
print(f"\nSaved summary.json ({size_kb:.1f} KB)")

print("\nCompetitor breakdown — vodka share at parity weeks:")
print(f"  {'City':<12} {'Absolut':>8} {'Smirnoff':>9} {'Grey Goose':>11} {'House':>8}")
for city in CITIES:
    c = competitor_breakdown_by_city[city]
    print(f"  {city:<12} {c['Absolut']:>7}%  {c['Smirnoff']:>7}%  {c['Grey Goose']:>9}%  {c['House vodka']:>6}%")
print("\nNetwork-wide:")
n = network_competitor_share
print(f"  Absolut {n['Absolut']}% | Smirnoff {n['Smirnoff']}% | Grey Goose {n['Grey Goose']}% | House {n['House vodka']}%")
