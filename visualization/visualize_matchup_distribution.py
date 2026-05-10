import matplotlib.pyplot as plt

from collections import Counter

from utils import (
    load_dataset,
    group_by_round
)

# =====================================================
# DATASET
# =====================================================

DATASET = "dataset_v2_clean.jsonl"

# =====================================================
# LOAD
# =====================================================

data = load_dataset(DATASET)

rounds = group_by_round(data)

# =====================================================
# COUNT MATCHUPS BY ROUND
# =====================================================

counter = Counter()

for round_id, samples in rounds.items():

    if len(samples) == 0:
        continue

    matchup = samples[0].get(
        "matchup",
        "unknown"
    ).lower()

    counter[matchup] += 1

# =====================================================
# LABELS
# =====================================================

labels = []
sizes = []

total_rounds = sum(counter.values())

for matchup, count in counter.items():

    percent = (
        count / total_rounds
    ) * 100

    label = (
        f"{matchup}\n"
        f"{percent:.1f}%\n"
        f"({count} rounds)"
    )

    labels.append(label)

    sizes.append(count)

# =====================================================
# PIE CHART
# =====================================================

plt.figure(figsize=(8, 8))

plt.pie(
    sizes,
    labels=labels,
    autopct="%1.1f%%"
)

plt.title(
    "Matchup Distribution by Round"
)

plt.show()
