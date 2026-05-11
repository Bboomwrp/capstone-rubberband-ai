import numpy as np
import matplotlib.pyplot as plt

from collections import defaultdict

from utils import (
    load_dataset,
    group_by_round
)

# =====================================================
# DATASETS
# =====================================================

BASELINE_DATASET = "dataset_v2_clean.jsonl"
RL_DATASET = "dataset_rl_clean.jsonl"

MAX_ROUND_TIME = 99

# =====================================================
# LOAD
# =====================================================

baseline_data = load_dataset(BASELINE_DATASET)
rl_data = load_dataset(RL_DATASET)

baseline_rounds = group_by_round(baseline_data)
rl_rounds = group_by_round(rl_data)

# =====================================================
# COMPUTE AVG DURATION
# =====================================================

def compute_matchup_avg(rounds):

    matchup_duration = defaultdict(list)

    for round_id, samples in rounds.items():

        if len(samples) < 2:
            continue

        matchup = samples[0]["matchup"]

        end_time = samples[-1][
            "next_state"
        ]["time"]

        remaining_seconds = (
            end_time
            * MAX_ROUND_TIME
        )

        duration = (
            MAX_ROUND_TIME
            - remaining_seconds
        )

        matchup_duration[
            matchup
        ].append(duration)

    avg_dict = {}

    for matchup, values in matchup_duration.items():

        avg_dict[matchup] = (
            sum(values)
            / len(values)
        )

    return avg_dict

# =====================================================
# AVERAGES
# =====================================================

baseline_avg = compute_matchup_avg(
    baseline_rounds
)

rl_avg = compute_matchup_avg(
    rl_rounds
)

# =====================================================
# MATCHUPS
# =====================================================

matchups = [
    "red_vs_red",
    "red_vs_blue",
    "blue_vs_red",
    "blue_vs_blue"
]

baseline_values = [
    baseline_avg.get(m, 0)
    for m in matchups
]

rl_values = [
    rl_avg.get(m, 0)
    for m in matchups
]

# =====================================================
# PLOT
# =====================================================

fig, ax = plt.subplots(
    figsize=(12, 6)
)

# =====================================================
# BACKGROUND
# =====================================================

bg_color = "#07111f"

fig.patch.set_facecolor(bg_color)
ax.set_facecolor(bg_color)

# =====================================================
# BAR POSITIONS
# =====================================================

x = np.arange(len(matchups))

width = 0.35

# =====================================================
# BARS
# =====================================================

bars1 = ax.bar(
    x - width/2,
    baseline_values,
    width,
    color="#1565c0",
    label="Baseline"
)

bars2 = ax.bar(
    x + width/2,
    rl_values,
    width,
    color="#4fc3f7",
    label="RL Inference"
)

# =====================================================
# LABELS
# =====================================================

ax.set_title(
    "Average Round Duration by Matchup",
    color="white",
    fontsize=16
)

ax.set_xlabel(
    "Matchup",
    color="white",
    fontsize=12
)

ax.set_ylabel(
    "Average Round Duration (s)",
    color="white",
    fontsize=12
)

# =====================================================
# X TICKS
# =====================================================

ax.set_xticks(x)

ax.set_xticklabels(
    matchups,
    color="white"
)

# =====================================================
# Y TICKS
# =====================================================

ax.tick_params(
    axis="y",
    colors="white"
)

# =====================================================
# GRID
# =====================================================

ax.grid(
    True,
    axis="y",
    alpha=0.15,
    color="white"
)

# =====================================================
# LEGEND
# =====================================================

legend = ax.legend()

for text in legend.get_texts():

    text.set_color("white")

# =====================================================
# SPINES
# =====================================================

for spine in ax.spines.values():

    spine.set_color("white")

# =====================================================
# VALUE LABELS
# =====================================================

for bars in [bars1, bars2]:

    for bar in bars:

        height = bar.get_height()

        ax.text(
            bar.get_x()
            + bar.get_width()/2,
            height + 0.5,
            f"{height:.1f}",
            ha="center",
            color="white",
            fontsize=10
        )

# =====================================================
# SHOW
# =====================================================

plt.tight_layout()

plt.show()
