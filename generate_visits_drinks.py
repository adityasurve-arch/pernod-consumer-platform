"""
Generate visits and drinks data for the Pernod venue network demo.
Runs on top of members.json. Produces visits.json and drinks.json.

Bakes in realistic patterns:
- Visit frequency varies by member archetype (heavy/medium/light/dormant)
- Weekend clustering, term-time vs holiday dips
- Group size distribution
- Brand preference varies by city (Absolut strong in Vienna/Paris, weak in Lisbon)
- Price elasticity (parity / premium / discount weeks)
- Cohort trade-up over tenure
"""

import json
import random
from datetime import datetime, timedelta
from collections import Counter

random.seed(42)

# Load members
with open("members.json") as f:
    MEMBERS = json.load(f)

# Lookup for fast access
MEMBERS_BY_ID = {m["member_id"]: m for m in MEMBERS}

TODAY = datetime(2026, 5, 10)
NETWORK_LAUNCH = datetime(2024, 11, 1)
CITY_LAUNCH_OFFSETS = {
    "Paris": 0, "Milan": 60, "Barcelona": 120, "Vienna": 180, "Lisbon": 240,
}

# ============================================================
# MEMBER ARCHETYPES (visit frequency)
# ============================================================
ARCHETYPES = {
    "heavy":   {"weight": 0.10, "visits_per_month": 4.5},
    "medium":  {"weight": 0.50, "visits_per_month": 2.2},
    "light":   {"weight": 0.30, "visits_per_month": 1.0},
    "dormant": {"weight": 0.10, "visits_per_month": 0.2},
}

def assign_archetype():
    return random.choices(
        list(ARCHETYPES.keys()),
        weights=[a["weight"] for a in ARCHETYPES.values()],
        k=1
    )[0]

# ============================================================
# DAY-OF-WEEK PATTERN (weekend skew)
# ============================================================
# Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6
DOW_WEIGHTS = [0.05, 0.07, 0.10, 0.18, 0.25, 0.25, 0.10]

# ============================================================
# SEASONAL / HOLIDAY DIPS (multiplier per ISO week)
# ============================================================
def seasonal_multiplier(date):
    week = date.isocalendar()[1]
    # Christmas / NYE break: late Dec & early Jan
    if date.month == 12 and date.day >= 20:
        return 0.4
    if date.month == 1 and date.day <= 5:
        return 0.4
    # Summer: students leave town, big dip Aug
    if date.month == 8:
        return 0.5
    # Late July also weaker
    if date.month == 7 and date.day >= 20:
        return 0.7
    # Exam crunch (May, late Jan): slight dip
    if date.month == 5 and 10 <= date.day <= 25:
        return 0.85
    if date.month == 1 and 15 <= date.day <= 28:
        return 0.85
    return 1.0

# ============================================================
# WEATHER (simplified per city by month)
# ============================================================
# Realistic monthly avg temp (C) per city
MONTHLY_TEMPS = {
    "Paris":     {1: 5, 2: 6, 3: 9, 4: 12, 5: 16, 6: 19, 7: 22, 8: 22, 9: 18, 10: 13, 11: 8, 12: 6},
    "Milan":     {1: 3, 2: 5, 3: 10, 4: 14, 5: 19, 6: 23, 7: 25, 8: 25, 9: 20, 10: 14, 11: 8, 12: 4},
    "Barcelona": {1: 11, 2: 12, 3: 14, 4: 16, 5: 19, 6: 23, 7: 26, 8: 26, 9: 23, 10: 19, 11: 14, 12: 12},
    "Vienna":    {1: 1, 2: 3, 3: 8, 4: 13, 5: 18, 6: 21, 7: 23, 8: 23, 9: 18, 10: 12, 11: 6, 12: 2},
    "Lisbon":    {1: 12, 2: 13, 3: 15, 4: 17, 5: 19, 6: 22, 7: 24, 8: 24, 9: 23, 10: 19, 11: 15, 12: 12},
}

def get_temp(city, date):
    base = MONTHLY_TEMPS[city][date.month]
    return base + random.randint(-3, 3)

# ============================================================
# DRINK MENU & BRAND PREFERENCE BY CITY
# ============================================================
# Spirits, beer, wine, soft. Roughly 70% spirits per the design.
# Each drink has: category, brand, brand_owner, base_price (EUR)

SPIRITS = {
    # Vodka
    "Absolut":         {"category": "vodka", "owner": "Pernod", "base_price": 8.5},
    "Smirnoff":        {"category": "vodka", "owner": "Diageo", "base_price": 8.0},
    "Grey Goose":      {"category": "vodka", "owner": "Bacardi", "base_price": 11.0},
    "House vodka":     {"category": "vodka", "owner": "House", "base_price": 6.5},
    # Gin
    "Beefeater":       {"category": "gin", "owner": "Pernod", "base_price": 8.5},
    "Monkey 47":       {"category": "gin", "owner": "Pernod", "base_price": 12.0},
    "Bombay Sapphire": {"category": "gin", "owner": "Bacardi", "base_price": 9.0},
    "Tanqueray":       {"category": "gin", "owner": "Diageo", "base_price": 9.0},
    "House gin":       {"category": "gin", "owner": "House", "base_price": 6.5},
    # Whiskey
    "Jameson":         {"category": "whiskey", "owner": "Pernod", "base_price": 9.0},
    "Chivas":          {"category": "whiskey", "owner": "Pernod", "base_price": 10.0},
    "Ballantine's":    {"category": "whiskey", "owner": "Pernod", "base_price": 9.0},
    "Jack Daniel's":   {"category": "whiskey", "owner": "Brown-Forman", "base_price": 9.5},
    "Johnnie Walker":  {"category": "whiskey", "owner": "Diageo", "base_price": 9.5},
    "House whiskey":   {"category": "whiskey", "owner": "House", "base_price": 7.0},
    # Rum
    "Havana Club":     {"category": "rum", "owner": "Pernod", "base_price": 8.5},
    "Malibu":          {"category": "rum", "owner": "Pernod", "base_price": 8.0},
    "Bacardi":         {"category": "rum", "owner": "Bacardi", "base_price": 8.0},
    "House rum":       {"category": "rum", "owner": "House", "base_price": 6.5},
    # Tequila
    "Olmeca":          {"category": "tequila", "owner": "Pernod", "base_price": 8.5},
    "Avion":           {"category": "tequila", "owner": "Pernod", "base_price": 11.0},
    "Jose Cuervo":     {"category": "tequila", "owner": "Becle", "base_price": 8.5},
    # Cognac / brandy
    "Martell":         {"category": "cognac", "owner": "Pernod", "base_price": 14.0},
    # Aperitif
    "Lillet":          {"category": "aperitif", "owner": "Pernod", "base_price": 7.5},
    "Aperol":          {"category": "aperitif", "owner": "Campari", "base_price": 7.5},
    "Campari":         {"category": "aperitif", "owner": "Campari", "base_price": 7.5},
    "Pernod":          {"category": "aperitif", "owner": "Pernod", "base_price": 7.5},
    "Ricard":          {"category": "aperitif", "owner": "Pernod", "base_price": 7.5},
    # Champagne
    "Mumm":            {"category": "champagne", "owner": "Pernod", "base_price": 16.0},
    "Perrier-Jouet":   {"category": "champagne", "owner": "Pernod", "base_price": 18.0},
    "House cava":      {"category": "champagne", "owner": "House", "base_price": 9.0},
}

NON_SPIRITS = {
    "Local lager":     {"category": "beer", "owner": "Local", "base_price": 5.0},
    "Craft IPA":       {"category": "beer", "owner": "Local", "base_price": 6.5},
    "House red wine":  {"category": "wine", "owner": "House", "base_price": 6.0},
    "House white wine":{"category": "wine", "owner": "House", "base_price": 6.0},
    "Soft drink":      {"category": "non_alc", "owner": "Coca-Cola", "base_price": 3.5},
    "Sparkling water": {"category": "non_alc", "owner": "Local", "base_price": 3.0},
    "Coffee":          {"category": "non_alc", "owner": "Local", "base_price": 3.0},
}

# Brand preference by city - this is the KEY pattern that drives the
# "brand equity by city" dashboard view.
# Multipliers applied to the *baseline* Pernod brand share.
# 1.0 = average, >1.0 = stronger Pernod preference, <1.0 = weaker.
CITY_BRAND_AFFINITY = {
    "Paris":     {"Absolut": 2.80, "Beefeater": 1.50, "Jameson": 1.80, "Havana Club": 1.50,
                  "Lillet": 2.50, "Pernod": 2.00, "Ricard": 2.00, "Mumm": 2.00,
                  "Martell": 1.80, "Chivas": 1.40},
    "Milan":     {"Absolut": 1.50, "Beefeater": 1.20, "Jameson": 1.40, "Havana Club": 1.20,
                  "Lillet": 1.40, "Aperol": 2.20, "Campari": 2.00, "Mumm": 1.50,
                  "Martell": 1.00, "Chivas": 1.10},
    "Barcelona": {"Absolut": 1.30, "Beefeater": 2.20, "Jameson": 1.30, "Havana Club": 1.80,
                  "Lillet": 1.10, "Pernod": 0.90, "Mumm": 1.30, "Martell": 1.00,
                  "Chivas": 1.30, "Olmeca": 1.50, "Avion": 1.30},
    "Vienna":    {"Absolut": 3.20, "Beefeater": 1.40, "Monkey 47": 2.50, "Jameson": 1.50,
                  "Havana Club": 1.30, "Mumm": 1.80, "Martell": 1.40, "Chivas": 1.60,
                  "Ballantine's": 1.40},
    "Lisbon":    {"Absolut": 0.65, "Beefeater": 1.60, "Jameson": 1.20, "Havana Club": 2.00,
                  "Lillet": 0.95, "Pernod": 0.85, "Mumm": 1.00, "Martell": 0.85,
                  "Chivas": 1.00},
}

# Wine and beer share differs by country culture
NON_SPIRITS_SHARE_BY_CITY = {
    "Paris":     {"beer": 0.10, "wine": 0.15, "non_alc": 0.05},
    "Milan":     {"beer": 0.08, "wine": 0.20, "non_alc": 0.05},
    "Barcelona": {"beer": 0.15, "wine": 0.10, "non_alc": 0.05},
    "Vienna":    {"beer": 0.18, "wine": 0.07, "non_alc": 0.05},
    "Lisbon":    {"beer": 0.12, "wine": 0.13, "non_alc": 0.05},
}

# ============================================================
# PRICE EXPERIMENT MODES (per week per city per brand)
# ============================================================
# Each week, each Pernod headline brand runs in one mode
PRICE_MODES = ["parity", "premium", "discount"]
PRICE_MODE_WEIGHTS = [0.50, 0.25, 0.25]
PRICE_MULTIPLIERS = {"parity": 1.00, "premium": 1.18, "discount": 0.92}

# Brands that participate in the price experiment (rotated)
EXPERIMENT_BRANDS = ["Absolut", "Beefeater", "Jameson", "Havana Club"]

def generate_price_schedule():
    """Build price schedule: dict[(city, brand, week)] -> mode"""
    schedule = {}
    for city in CITY_LAUNCH_OFFSETS:
        for brand in EXPERIMENT_BRANDS:
            for week in range(85):  # 18 months ~ 78 weeks, +buffer
                mode = random.choices(PRICE_MODES, weights=PRICE_MODE_WEIGHTS, k=1)[0]
                schedule[(city, brand, week)] = mode
    return schedule

PRICE_SCHEDULE = generate_price_schedule()

def get_price(city, brand_name, drink_date):
    """Return actual price for a brand on a given date in a city."""
    spec = SPIRITS.get(brand_name) or NON_SPIRITS.get(brand_name)
    if spec is None:
        return None
    base = spec["base_price"]
    if brand_name in EXPERIMENT_BRANDS:
        week = (drink_date - NETWORK_LAUNCH).days // 7
        mode = PRICE_SCHEDULE.get((city, brand_name, week), "parity")
        return round(base * PRICE_MULTIPLIERS[mode], 2)
    return round(base, 2)

def get_price_mode(city, brand_name, drink_date):
    """Return active price mode for a brand on a given date in a city."""
    if brand_name not in EXPERIMENT_BRANDS:
        return None
    week = (drink_date - NETWORK_LAUNCH).days // 7
    return PRICE_SCHEDULE.get((city, brand_name, week), "parity")

# ============================================================
# DRINK CHOICE LOGIC
# ============================================================
# Tenure factor: longer tenure = more likely to upgrade to premium
def tenure_premium_boost(member, visit_date):
    signup = datetime.strptime(member["signup_date"], "%Y-%m-%d")
    months_active = max(0, (visit_date - signup).days / 30)
    # 0 boost at month 0, +0.30 at month 12, capped at +0.40
    return min(0.40, months_active * 0.025)

def pick_drink(member, city, visit_date):
    """Pick what a single drink is, with realistic logic."""
    # First decide category mix
    non_spirit_share = NON_SPIRITS_SHARE_BY_CITY[city]
    cat_roll = random.random()
    cumulative = 0.0
    for cat, share in non_spirit_share.items():
        cumulative += share
        if cat_roll < cumulative:
            # Pick from non-spirits in this category
            options = [(n, s) for n, s in NON_SPIRITS.items() if s["category"] == cat]
            choice = random.choice(options)
            return choice[0], choice[1]
    # Otherwise spirits — pick a category, then a brand
    return pick_spirits(member, city, visit_date)

def pick_spirits(member, city, visit_date):
    """Pick a spirits brand based on city affinity, price experiments, and tenure."""
    # Pick spirits category first based on rough European preference
    category_weights = {
        "vodka": 0.20, "gin": 0.18, "whiskey": 0.18, "rum": 0.10,
        "tequila": 0.05, "cognac": 0.03, "aperitif": 0.18,
        "champagne": 0.06, "other": 0.02,
    }
    # Adjust for city (rough approximation)
    if city == "Milan":
        category_weights["aperitif"] = 0.32
        category_weights["vodka"] = 0.12
    if city == "Barcelona":
        category_weights["gin"] = 0.32
        category_weights["whiskey"] = 0.12
    if city == "Lisbon":
        category_weights["gin"] = 0.25
        category_weights["rum"] = 0.18
    if city == "Vienna":
        category_weights["vodka"] = 0.26
        category_weights["whiskey"] = 0.22

    cats = list(category_weights.keys())
    cat = random.choices(cats, weights=[category_weights[c] for c in cats], k=1)[0]
    if cat == "other":
        cat = "rum"

    # Get all brands in that category
    options = [(n, s) for n, s in SPIRITS.items() if s["category"] == cat]
    if not options:
        # Fallback: pick any spirit
        options = list(SPIRITS.items())

    # Build choice weights
    weights = []
    tenure_boost = tenure_premium_boost(member, visit_date)

    for name, spec in options:
        # Base weight
        w = 1.0

        # Pernod brands get city-affinity multiplier
        if spec["owner"] == "Pernod":
            affinity = CITY_BRAND_AFFINITY.get(city, {}).get(name, 1.0)
            w *= affinity
            # Tenure boost: longer-tenure members trade up to Pernod premium
            w *= (1.0 + tenure_boost)

        # House brands get a discount for being cheaper, boost for price-sensitive
        if spec["owner"] == "House":
            w *= 1.15  # somewhat popular due to price, but not dominant
            # Less attractive for tenured members who've traded up
            w *= (1.0 - tenure_boost * 0.6)

        # Price-experiment effect — strong elasticity
        if name in EXPERIMENT_BRANDS:
            mode = get_price_mode(city, name, visit_date)
            if mode == "discount":
                w *= 2.20  # discounts strongly boost share
            elif mode == "premium":
                w *= 0.35  # premium strongly hurts share
            # parity: no change

        weights.append(w)

    chosen_name = random.choices([n for n, _ in options], weights=weights, k=1)[0]
    return chosen_name, SPIRITS[chosen_name]

# ============================================================
# VISIT GENERATION
# ============================================================
def generate_visits_for_member(member, archetype):
    """Generate visit list for a single member."""
    signup = datetime.strptime(member["signup_date"], "%Y-%m-%d")
    end_date = TODAY
    months_active = max(0.5, (end_date - signup).days / 30)
    expected_visits = ARCHETYPES[archetype]["visits_per_month"] * months_active
    # Add Poisson-style noise
    actual_visits = max(0, int(random.gauss(expected_visits, expected_visits * 0.2)))

    visits = []
    for _ in range(actual_visits):
        visit_date = pick_visit_date(signup, end_date)
        if visit_date is None:
            continue
        visits.append(visit_date)
    return sorted(visits)

def pick_visit_date(start, end):
    """Pick a random date weighted by day-of-week and seasonality."""
    days_range = (end - start).days
    if days_range <= 0:
        return None
    for _ in range(20):  # try up to 20 times to find a valid date
        offset = random.randint(0, days_range - 1)
        candidate = start + timedelta(days=offset)
        dow_w = DOW_WEIGHTS[candidate.weekday()]
        season_w = seasonal_multiplier(candidate)
        if random.random() < dow_w * season_w:
            return candidate
    return start + timedelta(days=random.randint(0, days_range - 1))

# ============================================================
# MAIN GENERATION
# ============================================================
def main():
    visits = []
    drinks = []

    # Assign archetypes
    for m in MEMBERS:
        m["_archetype"] = assign_archetype()

    visit_id = 1
    drink_id = 1

    print("Generating visits and drinks...")
    for i, m in enumerate(MEMBERS):
        if i % 2500 == 0:
            print(f"  {i:,} / {len(MEMBERS):,} members")

        member_visits = generate_visits_for_member(m, m["_archetype"])
        city = m["signup_city"]

        for vd in member_visits:
            # Visit details
            arrival_hour = random.choices(
                [18, 19, 20, 21, 22, 23, 0, 1],
                weights=[0.05, 0.10, 0.20, 0.25, 0.20, 0.12, 0.05, 0.03], k=1
            )[0]
            arrival = vd.replace(hour=arrival_hour, minute=random.randint(0, 59))
            duration_min = int(random.gauss(135, 35))
            duration_min = max(45, min(300, duration_min))
            departure = arrival + timedelta(minutes=duration_min)

            group_size = random.choices([1, 2, 3, 4, 5, 6, 7, 8],
                                         weights=[0.10, 0.20, 0.22, 0.20, 0.12, 0.08, 0.05, 0.03], k=1)[0]
            num_drinks = max(1, int(random.gauss(3.4, 1.0)))

            visit_record = {
                "visit_id": f"V-{visit_id:08d}",
                "member_id": m["member_id"],
                "venue_id": m["signup_venue"],
                "city": city,
                "arrival_timestamp": arrival.isoformat() + "Z",
                "departure_timestamp": departure.isoformat() + "Z",
                "day_of_week": arrival.strftime("%A"),
                "is_weekend": arrival.weekday() >= 4,
                "group_size": group_size,
                "weather_temp_c": get_temp(city, vd),
                "season_multiplier": round(seasonal_multiplier(vd), 2),
                "num_drinks": num_drinks,
                "archetype": m["_archetype"],
            }
            visits.append(visit_record)

            # Generate the drinks for this visit
            for round_num in range(1, num_drinks + 1):
                drink_time = arrival + timedelta(minutes=round_num * 25 + random.randint(-5, 5))
                drink_name, drink_spec = pick_drink(m, city, vd)
                price_paid = get_price(city, drink_name, vd)
                price_normal = round(drink_spec["base_price"], 2)
                price_mode = get_price_mode(city, drink_name, vd) if drink_name in EXPERIMENT_BRANDS else None

                drink_record = {
                    "drink_id": f"D-{drink_id:09d}",
                    "visit_id": visit_record["visit_id"],
                    "member_id": m["member_id"],
                    "city": city,
                    "venue_id": m["signup_venue"],
                    "timestamp": drink_time.isoformat() + "Z",
                    "round_number": round_num,
                    "brand": drink_name,
                    "category": drink_spec["category"],
                    "brand_owner": drink_spec["owner"],
                    "price_paid": price_paid,
                    "price_normal": price_normal,
                    "price_mode": price_mode,
                }
                drinks.append(drink_record)
                drink_id += 1

            visit_id += 1

    # Strip the temp _archetype field
    for m in MEMBERS:
        del m["_archetype"]

    # Save
    print(f"\nSaving {len(visits):,} visits and {len(drinks):,} drinks...")
    with open("visits.json", "w") as f:
        json.dump(visits, f)
    with open("drinks.json", "w") as f:
        json.dump(drinks, f)

    # Summary
    print(f"\nGenerated {len(visits):,} visits, {len(drinks):,} drinks")

    print("\nVisits per city:")
    city_visits = Counter(v["city"] for v in visits)
    for city, count in city_visits.most_common():
        print(f"  {city:12s} {count:>8,}")

    print("\nDay-of-week distribution:")
    dow_counts = Counter(v["day_of_week"] for v in visits)
    for dow in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
        c = dow_counts[dow]
        bar = "#" * (c // 800)
        print(f"  {dow:10s} {c:>7,} {bar}")

    print("\nTop 10 brands by drinks ordered (whole network):")
    brand_counts = Counter(d["brand"] for d in drinks)
    for brand, count in brand_counts.most_common(10):
        print(f"  {brand:18s} {count:>7,}")

    print("\nDrinks by category:")
    cat_counts = Counter(d["category"] for d in drinks)
    total = len(drinks)
    for cat, count in cat_counts.most_common():
        pct = 100 * count / total
        print(f"  {cat:12s} {count:>7,} ({pct:.1f}%)")

    print("\nDrinks by brand owner:")
    owner_counts = Counter(d["brand_owner"] for d in drinks)
    for owner, count in owner_counts.most_common():
        pct = 100 * count / total
        print(f"  {owner:14s} {count:>7,} ({pct:.1f}%)")

    print("\n--- Brand equity test: Absolut share at PARITY weeks, by city ---")
    for city in ["Paris", "Milan", "Barcelona", "Vienna", "Lisbon"]:
        # For each vodka drink, look up what mode Absolut was in that week in that city.
        # Then count Absolut share among vodka drinks during parity weeks.
        from datetime import datetime as dt
        parity_vodka = []
        absolut_in_parity = 0
        for d in drinks:
            if d["city"] != city or d["category"] != "vodka":
                continue
            drink_date = dt.fromisoformat(d["timestamp"].rstrip("Z"))
            week = (drink_date.date() - NETWORK_LAUNCH.date()).days // 7
            absolut_mode_that_week = PRICE_SCHEDULE.get((city, "Absolut", week), "parity")
            if absolut_mode_that_week == "parity":
                parity_vodka.append(d)
                if d["brand"] == "Absolut":
                    absolut_in_parity += 1
        if not parity_vodka:
            continue
        share = 100 * absolut_in_parity / len(parity_vodka)
        print(f"  {city:12s} {share:.1f}%  (n={len(parity_vodka):,})")

    print("\n--- Price elasticity test: Absolut share by price mode (network avg) ---")
    from datetime import datetime as dt
    for mode in ["discount", "parity", "premium"]:
        vodka_in_mode = []
        absolut_in_mode = 0
        for d in drinks:
            if d["category"] != "vodka":
                continue
            drink_date = dt.fromisoformat(d["timestamp"].rstrip("Z"))
            week = (drink_date.date() - NETWORK_LAUNCH.date()).days // 7
            absolut_mode_that_week = PRICE_SCHEDULE.get((d["city"], "Absolut", week), "parity")
            if absolut_mode_that_week == mode:
                vodka_in_mode.append(d)
                if d["brand"] == "Absolut":
                    absolut_in_mode += 1
        share = 100 * absolut_in_mode / max(1, len(vodka_in_mode))
        print(f"  {mode:10s} {share:.1f}%  (n={len(vodka_in_mode):,})")

    print("\n--- Cohort trade-up test: Absolut share among vodka drinkers, by tenure ---")
    from datetime import datetime as dt
    tenure_buckets = {"<3mo": [], "3-6mo": [], "6-9mo": [], "9-12mo": [], "12mo+": []}
    tenure_absolut = {"<3mo": 0, "3-6mo": 0, "6-9mo": 0, "9-12mo": 0, "12mo+": 0}
    for d in drinks:
        if d["category"] != "vodka":
            continue
        m = MEMBERS_BY_ID.get(d["member_id"])
        if not m:
            continue
        signup = dt.strptime(m["signup_date"], "%Y-%m-%d")
        drink_date = dt.fromisoformat(d["timestamp"].rstrip("Z"))
        months = (drink_date - signup).days / 30
        if months < 3:
            bucket = "<3mo"
        elif months < 6:
            bucket = "3-6mo"
        elif months < 9:
            bucket = "6-9mo"
        elif months < 12:
            bucket = "9-12mo"
        else:
            bucket = "12mo+"
        tenure_buckets[bucket].append(d)
        if d["brand"] == "Absolut":
            tenure_absolut[bucket] += 1
    for bucket in ["<3mo", "3-6mo", "6-9mo", "9-12mo", "12mo+"]:
        n = len(tenure_buckets[bucket])
        if n == 0:
            continue
        share = 100 * tenure_absolut[bucket] / n
        print(f"  {bucket:8s} {share:.1f}%  (n={n:,})")


if __name__ == "__main__":
    main()
