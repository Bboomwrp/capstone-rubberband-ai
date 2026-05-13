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

# =====================================================
# BOOST ACTIONS
# =====================================================

BOOST_ACTIONS = [
    "BOOST_ATTACK",
    "BOOST_DEFENSE",
    "BOOST_GAUGE"
]

# =====================================================
# THEME
# =====================================================

bg_color = "#07111f"

baseline_color = "#1565c0"

rl_color = "#81d4fa"

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
# COMPUTE AVG BOOSTS PER ROUND
# =====================================================

def compute_avg_boosts(rounds):

    boost_counts = defaultdict(int)

    total_rounds = len(rounds)

    for round_id, samples in rounds.items():

        for sample in samples:

            action = sample["action"]

            if action in BOOST_ACTIONS:

                boost_counts[action] += 1

    avg = {}

    for action in BOOST_ACTIONS:

        avg[action] = (
            boost_counts[action]
            / max(total_rounds, 1)
        )

    return avg

# =====================================================
# PROCESS
# =====================================================

baseline_avg = compute_avg_boosts(
    baseline_rounds
)

rl_avg = compute_avg_boosts(
    rl_rounds
)

# =====================================================
# BAR VALUES
# =====================================================

baseline_values = [
    baseline_avg[action]
    for action in BOOST_ACTIONS
]

rl_values = [
    rl_avg[action]
    for action in BOOST_ACTIONS
]

# =====================================================
# PLOT
# =====================================================

fig, ax = plt.subplots(
    figsize=(10, 6)
)

fig.patch.set_facecolor(
    bg_color
)

ax.set_facecolor(
    bg_color
)

# =====================================================
# BAR POSITIONS
# =====================================================

x = np.arange(
    len(BOOST_ACTIONS)
)

width = 0.35

# =====================================================
# BASELINE
# =====================================================

bars1 = ax.bar(
    x - width/2,
    baseline_values,
    width,
    color=baseline_color,
    label="Baseline"
)

# =====================================================
# RL
# =====================================================

bars2 = ax.bar(
    x + width/2,
    rl_values,
    width,
    color=rl_color,
    label="RL Inference"
)

# =====================================================
# LABELS
# =====================================================

ax.set_title(
    "Average Boost Actions Per Round",
    color="white",
    fontsize=16
)

ax.set_xlabel(
    "Boost Type",
    color="white",
    fontsize=12
)

ax.set_ylabel(
    "Average Boosts Per Round",
    color="white",
    fontsize=12
)

# =====================================================
# X TICKS
# =====================================================

ax.set_xticks(x)

ax.set_xticklabels(
    [
        "Attack",
        "Defense",
        "Gauge"
    ],
    color="white",
    fontsize=11
)

# =====================================================
# AXIS COLORS
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
            height + 0.03,
            f"{height:.2f}",
            ha="center",
            color="white",
            fontsize=10
        )

# =====================================================
# SHOW
# =====================================================

plt.tight_layout()

plt.show()
