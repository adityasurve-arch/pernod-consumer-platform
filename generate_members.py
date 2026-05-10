"""
Generate synthetic member dataset for the Pernod venue network demo.
25,000 members across 5 cities, with realistic demographic patterns.
"""

import json
import random
from datetime import datetime, timedelta
from collections import Counter

random.seed(42)  # reproducible output

# City allocation (justified in the pitch)
CITY_ALLOCATION = {
    "Paris": 6000,
    "Milan": 4000,
    "Barcelona": 6500,
    "Vienna": 5000,
    "Lisbon": 3500,
}

# Nationality distributions per city
# Based on Campus France data, Bocconi international stats, BCN/UB international,
# Vienna's CEE student inflow, Lisbon's growing international base
NATIONALITY_MIX = {
    "Paris": {
        "France": 0.62, "Italy": 0.04, "Spain": 0.04, "Germany": 0.03,
        "Morocco": 0.05, "Algeria": 0.03, "Senegal": 0.02, "Tunisia": 0.02,
        "China": 0.04, "USA": 0.02, "UK": 0.02, "Brazil": 0.02,
        "Lebanon": 0.01, "India": 0.02, "Other": 0.02,
    },
    "Milan": {
        "Italy": 0.74, "Spain": 0.03, "France": 0.02, "Germany": 0.02,
        "Greece": 0.02, "Turkey": 0.02, "Romania": 0.02, "China": 0.03,
        "India": 0.02, "USA": 0.02, "UK": 0.01, "Brazil": 0.01,
        "Russia": 0.01, "Other": 0.03,
    },
    "Barcelona": {
        "Spain": 0.66, "Italy": 0.05, "France": 0.04, "Germany": 0.03,
        "Mexico": 0.03, "Argentina": 0.02, "Colombia": 0.02, "Brazil": 0.02,
        "Chile": 0.01, "USA": 0.03, "UK": 0.02, "China": 0.02,
        "Morocco": 0.01, "India": 0.01, "Other": 0.03,
    },
    "Vienna": {
        "Austria": 0.58, "Germany": 0.08, "Italy": 0.03, "Hungary": 0.04,
        "Romania": 0.03, "Serbia": 0.03, "Croatia": 0.02, "Bulgaria": 0.02,
        "Turkey": 0.03, "Poland": 0.02, "Russia": 0.02, "Iran": 0.02,
        "China": 0.02, "India": 0.02, "Ukraine": 0.02, "Other": 0.02,
    },
    "Lisbon": {
        "Portugal": 0.59, "Brazil": 0.10, "Angola": 0.03, "Cape Verde": 0.02,
        "Mozambique": 0.02, "France": 0.04, "Italy": 0.03, "Spain": 0.03,
        "Germany": 0.02, "USA": 0.03, "UK": 0.02, "China": 0.02,
        "India": 0.02, "Other": 0.03,
    },
}

# Universities per city — top 4-6 institutions
UNIVERSITIES = {
    "Paris": ["Sciences Po", "Sorbonne", "Paris Dauphine", "Assas",
              "ESCP Paris", "Paris-Cite", "ESSEC", "HEC", "Other"],
    "Milan": ["Bocconi", "Politecnico di Milano", "Univ. degli Studi di Milano",
              "Cattolica", "IULM", "Bicocca", "Other"],
    "Barcelona": ["Univ. de Barcelona", "Pompeu Fabra", "Univ. Autonoma BCN",
                  "IESE", "ESADE", "ESCI-UPF", "Ramon Llull", "Other"],
    "Vienna": ["Univ. of Vienna", "WU Wien", "TU Wien", "BOKU",
               "MedUni Vienna", "FH Wien", "Other"],
    "Lisbon": ["Univ. de Lisboa", "Nova SBE", "Catolica Lisbon",
               "ISCTE-IUL", "ISEG", "Univ. Nova de Lisboa", "Other"],
}

# Weighting: top schools get more weight (where students actually concentrate
# and have spending power for premium venues)
UNI_WEIGHTS = {
    "Paris":     [0.18, 0.20, 0.10, 0.10, 0.12, 0.18, 0.04, 0.04, 0.04],
    "Milan":     [0.30, 0.22, 0.20, 0.10, 0.08, 0.06, 0.04],
    "Barcelona": [0.30, 0.18, 0.12, 0.12, 0.12, 0.06, 0.06, 0.04],
    "Vienna":    [0.40, 0.22, 0.16, 0.06, 0.06, 0.06, 0.04],
    "Lisbon":    [0.32, 0.20, 0.18, 0.12, 0.08, 0.06, 0.04],
}

VENUE_IDS = {
    "Paris": "PAR-001", "Milan": "MIL-001", "Barcelona": "BCN-001",
    "Vienna": "VIE-001", "Lisbon": "LIS-001",
}

REFERRAL_SOURCES = ["walk_in", "friend_referral", "instagram_ad",
                    "tiktok_ad", "event", "campus_flyer", "tripadvisor"]
REFERRAL_WEIGHTS = [0.32, 0.28, 0.14, 0.10, 0.08, 0.05, 0.03]

# Today: Sunday May 10, 2026. Network has been live since Nov 2024 (~18 months)
TODAY = datetime(2026, 5, 10)
NETWORK_LAUNCH = datetime(2024, 11, 1)


def weighted_choice(options, weights):
    return random.choices(options, weights=weights, k=1)[0]


def generate_dob(target_age_distribution):
    """
    Student age distribution skewed toward 19-24, with smaller postgrad tail.
    Returns DOB string YYYY-MM-DD.
    """
    age = random.choices(
        [18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30],
        weights=[3, 12, 16, 16, 14, 12, 9, 6, 4, 3, 2, 2, 1],
        k=1
    )[0]
    # Random day-of-year offset
    day_offset = random.randint(0, 364)
    dob = TODAY - timedelta(days=age * 365 + day_offset)
    return dob.strftime("%Y-%m-%d")


def generate_signup_date(city):
    """
    Signup distribution: heavier in months 1-3 of city launch (acquisition push),
    steady afterward. Each city launched at a different time over 18 months.
    """
    city_launch_offsets = {
        "Paris": 0, "Milan": 60, "Barcelona": 120, "Vienna": 180, "Lisbon": 240,
    }
    launch = NETWORK_LAUNCH + timedelta(days=city_launch_offsets[city])
    days_since_launch = (TODAY - launch).days
    if days_since_launch <= 0:
        days_since_launch = 30

    # Front-loaded: more signups in first months
    weight_curve = [max(1, 30 - (i // 7)) for i in range(days_since_launch)]
    day_index = random.choices(range(days_since_launch), weights=weight_curve, k=1)[0]
    signup = launch + timedelta(days=day_index)
    return signup.strftime("%Y-%m-%d")


def generate_member(member_id, city):
    nationality = weighted_choice(
        list(NATIONALITY_MIX[city].keys()),
        list(NATIONALITY_MIX[city].values())
    )
    university = weighted_choice(UNIVERSITIES[city], UNI_WEIGHTS[city])
    gender = random.choices(
        ["female", "male", "non_binary", "prefer_not"],
        weights=[0.50, 0.46, 0.025, 0.015], k=1
    )[0]

    return {
        "member_id": f"M-{member_id:06d}",
        "signup_venue": VENUE_IDS[city],
        "signup_city": city,
        "signup_date": generate_signup_date(city),
        "date_of_birth": generate_dob(None),
        "nationality": nationality,
        "is_international": nationality != {
            "Paris": "France", "Milan": "Italy", "Barcelona": "Spain",
            "Vienna": "Austria", "Lisbon": "Portugal"
        }[city],
        "university": university,
        "gender": gender,
        "referral_source": weighted_choice(REFERRAL_SOURCES, REFERRAL_WEIGHTS),
        "email_opt_in": random.random() < 0.78,
        "sms_opt_in": random.random() < 0.34,
    }


def main():
    members = []
    member_id = 1
    for city, count in CITY_ALLOCATION.items():
        for _ in range(count):
            members.append(generate_member(member_id, city))
            member_id += 1

    random.shuffle(members)

    # Save full dataset
    with open("members.json", "w") as f:
        json.dump(members, f, indent=2)

    # Print summary
    print(f"Generated {len(members):,} members\n")
    print("Distribution by city:")
    city_counts = Counter(m["signup_city"] for m in members)
    for city, count in city_counts.most_common():
        pct = 100 * count / len(members)
        print(f"  {city:12s} {count:>5,}  ({pct:.1f}%)")

    print("\nInternational student share by city:")
    for city in CITY_ALLOCATION:
        city_members = [m for m in members if m["signup_city"] == city]
        intl = sum(1 for m in city_members if m["is_international"])
        pct = 100 * intl / len(city_members)
        print(f"  {city:12s} {pct:.1f}% international")

    print("\nAge distribution (whole network):")
    ages = []
    for m in members:
        dob = datetime.strptime(m["date_of_birth"], "%Y-%m-%d")
        age = (TODAY - dob).days // 365
        ages.append(age)
    age_counts = Counter(ages)
    for age in sorted(age_counts):
        bar = "#" * (age_counts[age] // 80)
        print(f"  age {age}: {age_counts[age]:>5,} {bar}")

    print("\nTop 5 nationalities (whole network):")
    nat_counts = Counter(m["nationality"] for m in members)
    for nat, count in nat_counts.most_common(5):
        pct = 100 * count / len(members)
        print(f"  {nat:12s} {count:>5,}  ({pct:.1f}%)")

    print("\nSample member record:")
    print(json.dumps(members[0], indent=2))


if __name__ == "__main__":
    main()
