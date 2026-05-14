import numpy as np
import matplotlib.pyplot as plt

from collections import defaultdict

from utils import load_dataset

# =====================================================
# DATASETS
# =====================================================

BASELINE_DATASET = "dataset_v2_clean.jsonl"
RL_DATASET = "dataset_rl_clean_3.jsonl"

# =====================================================
# SETTINGS
# =====================================================

NUM_BINS = 20

MATCHUPS = [
    "red_vs_red",
    "red_vs_blue",
    "blue_vs_red",
    "blue_vs_blue"
]

# =====================================================
# LOAD
# =====================================================

baseline_data = load_dataset(BASELINE_DATASET)
rl_data = load_dataset(RL_DATASET)

# =====================================================
# PROCESS FUNCTION
# =====================================================

def process_dataset(data):

    matchup_bins = {}

    for matchup in MATCHUPS:

        matchup_bins[matchup] = {
            "sum": np.zeros(NUM_BINS),
            "count": np.zeros(NUM_BINS)
        }

    for sample in data:

        matchup = sample["matchup"]

        if matchup not in MATCHUPS:
            continue

        # =================================================
        # ROUND PROGRESS
        # =================================================

        time_remaining = sample["state"]["time"]

        MAX_ROUND_TIME = 99

        remaining_time = (
            sample["state"]["time"]
            * MAX_ROUND_TIME
        )

        remaining_time = max(
            0,
            min(MAX_ROUND_TIME, remaining_time)
        )

        progress_ratio = (
            remaining_time
            / MAX_ROUND_TIME
        )

        bin_index = int(
            (1.0 - progress_ratio)
            * (NUM_BINS - 1)
        )

        # =================================================
        # HP DIFF
        # =================================================

        hp_diff = abs(
            sample["state"]["hp_ratio_diff"]
        )

        matchup_bins[matchup]["sum"][bin_index] += hp_diff

        matchup_bins[matchup]["count"][bin_index] += 1

    # =====================================================
    # AVERAGE
    # =====================================================

    result = {}

    for matchup in MATCHUPS:

        sums = matchup_bins[matchup]["sum"]
        counts = matchup_bins[matchup]["count"]

        avg = []

        for s, c in zip(sums, counts):

            if c == 0:
                avg.append(np.nan)

            else:
                avg.append(s / c)

        result[matchup] = avg

    return result

# =====================================================
# PROCESS
# =====================================================

baseline_result = process_dataset(
    baseline_data
)

rl_result = process_dataset(
    rl_data
)

# =====================================================
# X AXIS
# =====================================================

x = np.linspace( 99, 0, NUM_BINS )

# =====================================================
# PLOT
# =====================================================

bg_color = "#07111f"

for matchup in MATCHUPS:

    fig, ax = plt.subplots(
        figsize=(10, 5)
    )

    # =================================================
    # BACKGROUND
    # =================================================

    fig.patch.set_facecolor(
        bg_color
    )

    ax.set_facecolor(
        bg_color
    )

    # =================================================
    # BASELINE
    # =================================================

    ax.plot(
        x,
        baseline_result[matchup],
        linestyle="--",
        linewidth=2.5,
        color="#4fc3f7",
        label="Baseline"
    )

    # =================================================
    # RL
    # =================================================

    ax.plot(
        x,
        rl_result[matchup],
        linestyle="-",
        linewidth=3,
        color="#81d4fa",
        label="RL Inference"
    )

    # =================================================
    # LABELS
    # =================================================

    ax.set_xlabel(
        "Remaining Round Time (Seconds)",
        color="white",
        fontsize=11
    )

    ax.set_ylabel(
        "Average HP Difference",
        color="white",
        fontsize=11
    )

    ax.set_title(
        f"HP Difference Timeline - {matchup}",
        color="white",
        fontsize=14
    )

    # =================================================
    # LIMITS
    # =================================================

    ax.set_ylim(0, 1)

    # =================================================
    # AXIS COLORS
    # =================================================

    ax.tick_params(
        axis="x",
        colors="white"
    )

    ax.tick_params(
        axis="y",
        colors="white"
    )

    # =================================================
    # GRID
    # =================================================

    ax.grid(
        True,
        alpha=0.15,
        color="white"
    )

    # =================================================
    # LEGEND
    # =================================================

    legend = ax.legend()

    for text in legend.get_texts():

        text.set_color("white")

    # =================================================
    # SPINES
    # =================================================

    for spine in ax.spines.values():

        spine.set_color("white")

    # =================================================
    # FIGHTING GAME STYLE
    # =================================================

    ax.invert_xaxis()

    # =================================================
    # SHOW
    # =================================================

    plt.tight_layout()

    plt.show()

