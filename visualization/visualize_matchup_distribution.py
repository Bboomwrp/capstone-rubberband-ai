import matplotlib.pyplot as plt

from collections import Counter

from utils import (
    load_dataset,
    group_by_round
)

# =====================================================
# DATASETS
# =====================================================

BASELINE_DATASET = "dataset_v2_clean.jsonl"

RL_DATASET = "dataset_rl_clean.jsonl"

# =====================================================
# LOAD
# =====================================================

baseline_data = load_dataset(
    BASELINE_DATASET
)

rl_data = load_dataset(
    RL_DATASET
)

baseline_rounds = group_by_round(
    baseline_data
)

rl_rounds = group_by_round(
    rl_data
)

# =====================================================
# COUNT MATCHUPS
# =====================================================

def count_matchups(rounds):

    counter = Counter()

    for round_id, samples in rounds.items():

        if len(samples) == 0:
            continue

        matchup = samples[0].get(
            "matchup",
            "unknown"
        ).lower()

        counter[matchup] += 1

    return counter

baseline_counter = count_matchups(
    baseline_rounds
)

rl_counter = count_matchups(
    rl_rounds
)

# =====================================================
# BUILD PIE DATA
# =====================================================

def build_pie(counter):

    labels = []
    sizes = []

    total_rounds = sum(
        counter.values()
    )

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

    return labels, sizes

baseline_labels, baseline_sizes = build_pie(
    baseline_counter
)

rl_labels, rl_sizes = build_pie(
    rl_counter
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
# BACKGROUND
# =====================================================

bg_color = "#07111f"

fig.patch.set_facecolor(bg_color)

for ax in axes:

    ax.set_facecolor(bg_color)

# =====================================================
# COLORS
# =====================================================

colors = [
    "#1565c0",
    "#1e88e5",
    "#42a5f5",
    "#81d4fa"
]

# =====================================================
# BASELINE PIE
# =====================================================

axes[0].pie(
    baseline_sizes,
    labels=baseline_labels,
    autopct="%1.1f%%",
    colors=colors,
    textprops={
        "color": "white",
        "fontsize": 10
    }
)

axes[0].set_title(
    "Baseline Matchup Distribution",
    color="white",
    fontsize=14
)

# =====================================================
# RL PIE
# =====================================================

axes[1].pie(
    rl_sizes,
    labels=rl_labels,
    autopct="%1.1f%%",
    colors=colors,
    textprops={
        "color": "white",
        "fontsize": 10
    }
)

axes[1].set_title(
    "RL Inference Matchup Distribution",
    color="white",
    fontsize=14
)

# =====================================================
# SHOW
# =====================================================

plt.tight_layout()

plt.show()
