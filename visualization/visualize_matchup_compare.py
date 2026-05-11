import matplotlib.pyplot as plt

from collections import Counter

from utils import group_by_round, load_dataset

# =====================================================
# DATASETS
# =====================================================

BASELINE_DATASET = (
    "dataset_v2_clean.jsonl"
)

RL_DATASET = (
    "dataset_rl_clean.jsonl"
)

# =====================================================
# LOAD
# =====================================================

baseline_data = load_dataset(
    BASELINE_DATASET
)

rl_data = load_dataset(
    RL_DATASET
)

# =====================================================
# COUNT FUNCTION
# =====================================================

def count_matchups(data):

    counter = Counter()

    rounds = group_by_round(data)
    for round_id, samples in rounds.items():

        matchup = samples[0].get(
            "matchup",
            "unknown"
        ).lower()

        counter[matchup] += 1

    return counter

# =====================================================
# LABEL FUNCTION
# =====================================================

def build_labels(counter):

    labels = []
    sizes = []

    total = sum(counter.values())

    for matchup, count in counter.items():

        percent = (
            count / total
        ) * 100

        label = (
            f"{matchup}\n"
            f"{percent:.1f}%\n"
            f"({count} rounds)"
        )

        labels.append(label)

        sizes.append(count)

    return labels, sizes

# =====================================================
# PROCESS
# =====================================================

baseline_counter = count_matchups(
    baseline_data
)

rl_counter = count_matchups(
    rl_data
)

baseline_labels, baseline_sizes = (
    build_labels(baseline_counter)
)

rl_labels, rl_sizes = (
    build_labels(rl_counter)
)

# =====================================================
# PLOT
# =====================================================

fig, axes = plt.subplots(
    1,
    2,
    figsize=(14, 7)
)

# =====================================================
# BASELINE PIE
# =====================================================

axes[0].pie(
    baseline_sizes,
    labels=baseline_labels,
    autopct="%1.1f%%"
)

axes[0].set_title(
    "Baseline Dataset Matchup Distribution"
)

# =====================================================
# RL PIE
# =====================================================

axes[1].pie(
    rl_sizes,
    labels=rl_labels,
    autopct="%1.1f%%"
)

axes[1].set_title(
    "RL Dataset Matchup Distribution"
)

# =====================================================
# SHOW
# =====================================================

plt.tight_layout()

plt.show()
