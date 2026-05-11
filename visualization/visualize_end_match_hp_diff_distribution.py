import numpy as np
import matplotlib.pyplot as plt

from scipy.stats import gaussian_kde

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
# MATCHUPS
# =====================================================

MATCHUPS = [
    "red_vs_red",
    "red_vs_blue",
    "blue_vs_red",
    "blue_vs_blue"
]

# =====================================================
# CHARACTER MAX HP
# =====================================================

MAX_HP = {
    "red": 1000,
    "blue": 950
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

baseline_rounds = group_by_round(
    baseline_data
)

rl_rounds = group_by_round(
    rl_data
)

# =====================================================
# COMPUTE FINAL HP DIFF
# =====================================================

def compute_match_end_hp_diff_by_matchup(rounds):

    result = {}

    for matchup in MATCHUPS:

        result[matchup] = []

    for round_id, samples in rounds.items():

        if len(samples) == 0:
            continue

        matchup = samples[0].get(
            "matchup",
            "unknown"
        ).lower()

        if matchup not in MATCHUPS:
            continue

        # =============================================
        # FIND TERMINAL SAMPLE
        # =============================================

        terminal_sample = None

        for sample in reversed(samples):

            if sample["next_state"].get(
                "done",
                False
            ):

                terminal_sample = sample

                break

        if terminal_sample is None:
            continue

        state = terminal_sample["next_state"]

        # =============================================
        # CHARACTER
        # =============================================

        p1_char = state[
            "p1_character"
        ].lower()

        p2_char = state[
            "p2_character"
        ].lower()

        p1_max_hp = MAX_HP[p1_char]
        p2_max_hp = MAX_HP[p2_char]

        # =============================================
        # REAL HP
        # =============================================

        p1_hp = (
            state["p1_hp_ratio"]
            * p1_max_hp
        )

        p2_hp = (
            state["p2_hp_ratio"]
            * p2_max_hp
        )

        # =============================================
        # HP DIFF
        # =============================================

        hp_diff = p1_hp - p2_hp

        result[matchup].append(
            hp_diff
        )

    return result

# =====================================================
# PROCESS
# =====================================================

baseline_result = compute_match_end_hp_diff_by_matchup(
    baseline_rounds
)

rl_result = compute_match_end_hp_diff_by_matchup(
    rl_rounds
)

# =====================================================
# OVERALL ARRAYS
# =====================================================

overall_baseline = []

overall_rl = []

for matchup in MATCHUPS:

    overall_baseline.extend(
        baseline_result[matchup]
    )

    overall_rl.extend(
        rl_result[matchup]
    )

overall_baseline = np.array(
    overall_baseline
)

overall_rl = np.array(
    overall_rl
)

# =====================================================
# KDE X RANGE
# =====================================================

x = np.linspace(
    -1000,
    1000,
    1000
)

# =====================================================
# THEME
# =====================================================

bg_color = "#07111f"

# =====================================================
# OVERALL GRAPH
# =====================================================

fig, ax = plt.subplots(
    figsize=(12, 6)
)

fig.patch.set_facecolor(
    bg_color
)

ax.set_facecolor(
    bg_color
)

# =====================================================
# BALANCE LINE
# =====================================================

ax.axvline(
    x=0,
    color="white",
    alpha=0.25,
    linestyle=":"
)

# =====================================================
# KDE
# =====================================================

baseline_kde = gaussian_kde(
    overall_baseline
)

rl_kde = gaussian_kde(
    overall_rl
)

# =====================================================
# BASELINE
# =====================================================

ax.plot(
    x,
    baseline_kde(x),
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
    rl_kde(x),
    linestyle="-",
    linewidth=3,
    color="#81d4fa",
    label="RL Inference"
)

# =====================================================
# LABELS
# =====================================================

ax.set_title(
    "Overall Match End HP Difference Distribution",
    color="white",
    fontsize=16
)

ax.set_xlabel(
    "Final HP Difference (P1 HP - P2 HP)",
    color="white",
    fontsize=12
)

ax.set_ylabel(
    "Density",
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
# SHOW OVERALL
# =====================================================

plt.tight_layout()

plt.show()

# =====================================================
# MATCHUP SUBPLOTS
# =====================================================

fig, axes = plt.subplots(
    2,
    2,
    figsize=(14, 10)
)

fig.patch.set_facecolor(
    bg_color
)

axes = axes.flatten()

# =====================================================
# EACH MATCHUP
# =====================================================

for ax, matchup in zip(axes, MATCHUPS):

    ax.set_facecolor(
        bg_color
    )

    baseline_values = np.array(
        baseline_result[matchup]
    )

    rl_values = np.array(
        rl_result[matchup]
    )

    # =============================================
    # KDE
    # =============================================

    if len(baseline_values) > 1:

        baseline_kde = gaussian_kde(
            baseline_values
        )

        ax.plot(
            x,
            baseline_kde(x),
            linestyle="--",
            linewidth=2.5,
            color="#4fc3f7",
            label="Baseline"
        )

    if len(rl_values) > 1:

        rl_kde = gaussian_kde(
            rl_values
        )

        ax.plot(
            x,
            rl_kde(x),
            linestyle="-",
            linewidth=3,
            color="#81d4fa",
            label="RL Inference"
        )

    # =============================================
    # BALANCE LINE
    # =============================================

    ax.axvline(
        x=0,
        color="white",
        alpha=0.25,
        linestyle=":"
    )

    # =============================================
    # LABELS
    # =============================================

    ax.set_title(
        matchup,
        color="white",
        fontsize=13
    )

    ax.set_xlabel(
        "Final HP Difference",
        color="white"
    )

    ax.set_ylabel(
        "Density",
        color="white"
    )

    # =============================================
    # AXIS COLORS
    # =============================================

    ax.tick_params(
        axis="x",
        colors="white"
    )

    ax.tick_params(
        axis="y",
        colors="white"
    )

    # =============================================
    # GRID
    # =============================================

    ax.grid(
        True,
        alpha=0.15,
        color="white"
    )

    # =============================================
    # LEGEND
    # =============================================

    legend = ax.legend()

    for text in legend.get_texts():

        text.set_color("white")

    # =============================================
    # SPINES
    # =============================================

    for spine in ax.spines.values():

        spine.set_color("white")

# =====================================================
# MAIN TITLE
# =====================================================

fig.suptitle(
    "Match End HP Difference Distribution by Matchup",
    color="white",
    fontsize=18
)

# =====================================================
# SHOW SUBPLOTS
# =====================================================

plt.tight_layout()

plt.show()
