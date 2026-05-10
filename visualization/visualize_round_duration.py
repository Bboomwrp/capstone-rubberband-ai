import matplotlib.pyplot as plt

from collections import defaultdict

from utils import (
    load_dataset,
    group_by_round
)

DATASET = "dataset_v2_clean.jsonl"

data = load_dataset(DATASET)

rounds = group_by_round(data)

overall = []

matchup_duration = defaultdict(list)

for round_id, samples in rounds.items():

    if len(samples) < 2:
        continue

    matchup = samples[0]["matchup"]

    MAX_ROUND_TIME = 99

    end_time = samples[-1]["next_state"]["time"]

    remaining_seconds = (
        end_time * MAX_ROUND_TIME
    )

    duration = (
        MAX_ROUND_TIME
        - remaining_seconds
    )

    overall.append(duration)

    matchup_duration[matchup].append(duration)

# =====================================================
# OVERALL
# =====================================================

plt.figure(figsize=(8, 5))

plt.hist(
    overall,
    bins=20
)

plt.xlabel("Round Duration")
plt.ylabel("Frequency")

plt.title("Overall Round Duration Distribution")

plt.grid(True)

plt.show()

# =====================================================
# PER MATCHUP
# =====================================================

for matchup, values in matchup_duration.items():

    plt.figure(figsize=(8, 5))

    plt.hist(
        values,
        bins=20
    )

    plt.xlabel("Round Duration (seconds)")
    plt.ylabel("Frequency")

    plt.title(
        f"Round Duration Distribution - {matchup}"
    )

    plt.grid(True)

    plt.show()

    avg = sum(values) / len(values)

    print(
        f"{matchup} "
        f"average duration: "
        f"{avg:.3f}"
    )
