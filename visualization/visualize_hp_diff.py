import matplotlib.pyplot as plt

from utils import load_dataset

DATASET = "dataset_v2_clean.jsonl"

data = load_dataset(DATASET)

hp_diffs = []

matchup_hp = {}

for sample in data:

    diff = abs(
        sample["next_state"]["hp_ratio_diff"]
    )

    hp_diffs.append(diff)

    matchup = sample["matchup"]

    if matchup not in matchup_hp:
        matchup_hp[matchup] = []

    matchup_hp[matchup].append(diff)

# =====================================================
# OVERALL
# =====================================================

plt.figure(figsize=(8, 5))

plt.hist(
    hp_diffs,
    bins=30
)

plt.xlabel("HP Ratio Difference")
plt.ylabel("Frequency")
plt.title("HP Difference Distribution")

plt.grid(True)

plt.show()

# =====================================================
# PER MATCHUP
# =====================================================

for matchup, values in matchup_hp.items():

    plt.figure(figsize=(8, 5))

    plt.hist(
        values,
        bins=20
    )

    plt.xlabel("HP Ratio Difference")
    plt.ylabel("Frequency")

    plt.title(
        f"HP Difference Distribution - {matchup}"
    )

    plt.grid(True)

    plt.show()
