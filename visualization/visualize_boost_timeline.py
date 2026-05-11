import numpy as np
import matplotlib.pyplot as plt

from utils import load_dataset

# =====================================================
# DATASETS
# =====================================================

BASELINE_DATASET = "dataset_v2_clean.jsonl"
RL_DATASET = "dataset_rl_clean.jsonl"

# =====================================================
# SETTINGS
# =====================================================

MAX_ROUND_TIME = 99

NUM_BINS = 25

BOOST_ACTIONS = {
    "BOOST_ATTACK",
    "BOOST_DEFENSE",
    "BOOST_GAUGE"
}

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
# BUILD TIMELINE
# =====================================================

def build_boost_timeline(data):

    bins = np.zeros(NUM_BINS)

    for sample in data:

        action = sample["action"]

        # skip non-boost
        if action not in BOOST_ACTIONS:
            continue

        # =============================================
        # TIME
        # =============================================

        remaining_time = (
            sample["state"]["time"]
            * MAX_ROUND_TIME
        )

        remaining_time = max(
            0,
            min(MAX_ROUND_TIME, remaining_time)
        )

        # =============================================
        # BIN
        # =============================================

        progress_ratio = (
            1.0
            - (remaining_time / MAX_ROUND_TIME)
        )

        bin_index = int(
            progress_ratio
            * (NUM_BINS - 1)
        )

        bins[bin_index] += 1

    return bins

# =====================================================
# TIMELINES
# =====================================================

baseline_bins = build_boost_timeline(
    baseline_data
)

rl_bins = build_boost_timeline(
    rl_data
)

# =====================================================
# X AXIS
# =====================================================

x = np.linspace(
    MAX_ROUND_TIME,
    0,
    NUM_BINS
)

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
# BASELINE
# =====================================================

ax.plot(
    x,
    baseline_bins,
    linestyle="--",
    linewidth=2.5,
    color="#4fc3f7",
    label="Baseline"
)

# =====================================================
# RL
# =====================================================

ax.plot(
    x,
    rl_bins,
    linestyle="-",
    linewidth=3,
    color="#81d4fa",
    label="RL Inference"
)

# =====================================================
# TITLE
# =====================================================

ax.set_title(
    "Boost Action Timeline",
    color="white",
    fontsize=16
)

# =====================================================
# LABELS
# =====================================================

ax.set_xlabel(
    "Remaining Round Time (Seconds)",
    color="white",
    fontsize=12
)

ax.set_ylabel(
    "Number of Boost Actions",
    color="white",
    fontsize=12
)

# =====================================================
# AXIS COLORS
# =====================================================

ax.tick_params(
    axis="x",
    colors="white"
)

ax.tick_params(
    axis="y",
    colors="white"
)

# =====================================================
# GRID
# =====================================================

ax.grid(
    True,
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
# FIGHTING GAME STYLE
# =====================================================

ax.invert_xaxis()

# =====================================================
# SHOW
# =====================================================

plt.tight_layout()

plt.show()
