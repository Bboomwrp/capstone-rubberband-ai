import matplotlib.pyplot as plt

from collections import defaultdict

from utils import load_dataset

DATASET = "dataset_v2_clean.jsonl"

data = load_dataset(DATASET)

mapping = {
    "BOOST_ATTACK": 1,
    "BOOST_DEFENSE": 2,
    "BOOST_GAUGE": 3
}

overall_time = []
overall_boost = []

matchup_data = defaultdict(
    lambda: {
        "times": [],
        "boosts": []
    }
)

for sample in data:

    action = sample["action"]

    if action == "NONE":
        continue

    if action not in mapping:
        continue

    matchup = sample["matchup"]

    MAX_ROUND_TIME = 99

    t = (
        sample["state"]["time"]
        * MAX_ROUND_TIME
    )

    b = mapping[action]

    overall_time.append(t)
    overall_boost.append(b)

    matchup_data[matchup]["times"].append(t)
    matchup_data[matchup]["boosts"].append(b)

# =====================================================
# OVERALL
# =====================================================

plt.figure(figsize=(10, 5))

plt.scatter(
    overall_time,
    overall_boost
)

plt.yticks(
    [1, 2, 3],
    [
        "ATTACK",
        "DEFENSE",
        "GAUGE"
    ]
)

plt.xlabel("Remaining Round Time (Seconds)")
plt.ylabel("Boost Type")

plt.title("Overall Boost Timeline")

plt.grid(True)

plt.show()

# =====================================================
# PER MATCHUP
# =====================================================

for matchup, values in matchup_data.items():

    plt.figure(figsize=(10, 5))

    plt.scatter(
        values["times"],
        values["boosts"]
    )

    plt.yticks(
        [1, 2, 3],
        [
            "ATTACK",
            "DEFENSE",
            "GAUGE"
        ]
    )

    plt.xlabel("Remaining Round Time (Seconds)")
    plt.ylabel("Boost Type")

    plt.title(
        f"Boost Timeline - {matchup}"
    )

    plt.grid(True)

    plt.gca().invert_xaxis()

    plt.show()
