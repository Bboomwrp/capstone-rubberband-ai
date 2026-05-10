import matplotlib.pyplot as plt

from collections import defaultdict

from utils import (
    load_dataset,
    group_by_round
)

DATASET = "dataset_v2_clean.jsonl"

data = load_dataset(DATASET)

rounds = group_by_round(data)

overall = {
    "P1": 0,
    "P2": 0
}

matchup_winrate = defaultdict(
    lambda: {
        "P1": 0,
        "P2": 0
    }
)

for round_id, samples in rounds.items():

    if len(samples) == 0:
        continue

    matchup = samples[0]["matchup"]

    final_state = samples[-1]["next_state"]

    if final_state["p1_hp_ratio"] <= 0:

        overall["P2"] += 1
        matchup_winrate[matchup]["P2"] += 1

    elif final_state["p2_hp_ratio"] <= 0:

        overall["P1"] += 1
        matchup_winrate[matchup]["P1"] += 1

# =====================================================
# OVERALL
# =====================================================

plt.figure(figsize=(6, 6))

plt.pie(
    [
        overall["P1"],
        overall["P2"]
    ],
    labels=[
        "P1 Wins",
        "P2 Wins"
    ],
    autopct="%1.1f%%"
)

plt.title("Overall Win Rate Balance")

plt.show()

# =====================================================
# PER MATCHUP
# =====================================================

for matchup, values in matchup_winrate.items():

    plt.figure(figsize=(6, 6))

    plt.pie(
        [
            values["P1"],
            values["P2"]
        ],
        labels=[
            "P1 Wins",
            "P2 Wins"
        ],
        autopct="%1.1f%%"
    )

    plt.title(
        f"Win Rate Balance - {matchup}"
    )

    plt.show()

    print(matchup)
    print(values)
