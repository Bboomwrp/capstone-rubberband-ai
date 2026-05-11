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
# THEME
# =====================================================

bg_color = "#07111f"

pie_colors = [
    "#1565c0",
    "#81d4fa"
]

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
# COMPUTE WINRATE
# =====================================================

def compute_winrate(rounds):

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

        matchup = samples[0][
            "matchup"
        ]

        final_state = samples[-1][
            "next_state"
        ]

        if final_state[
            "p1_hp_ratio"
        ] <= 0:

            overall["P2"] += 1

            matchup_winrate[
                matchup
            ]["P2"] += 1

        elif final_state[
            "p2_hp_ratio"
        ] <= 0:

            overall["P1"] += 1

            matchup_winrate[
                matchup
            ]["P1"] += 1

    return overall, matchup_winrate

# =====================================================
# PROCESS
# =====================================================

baseline_overall, baseline_matchup = compute_winrate(
    baseline_rounds
)

rl_overall, rl_matchup = compute_winrate(
    rl_rounds
)

# =====================================================
# OVERALL COMPARISON
# =====================================================

fig, axes = plt.subplots(
    1,
    2,
    figsize=(12, 6)
)

fig.patch.set_facecolor(
    bg_color
)

# =====================================================
# BASELINE PIE
# =====================================================

axes[0].set_facecolor(
    bg_color
)

axes[0].pie(
    [
        baseline_overall["P1"],
        baseline_overall["P2"]
    ],
    labels=[
        "P1 Wins",
        "P2 Wins"
    ],
    autopct="%1.1f%%",
    colors=pie_colors,
    textprops={
        "color": "white",
        "fontsize": 11
    }
)

axes[0].set_title(
    "Baseline Overall Win Rate",
    color="white",
    fontsize=14
)

# =====================================================
# RL PIE
# =====================================================

axes[1].set_facecolor(
    bg_color
)

axes[1].pie(
    [
        rl_overall["P1"],
        rl_overall["P2"]
    ],
    labels=[
        "P1 Wins",
        "P2 Wins"
    ],
    autopct="%1.1f%%",
    colors=pie_colors,
    textprops={
        "color": "white",
        "fontsize": 11
    }
)

axes[1].set_title(
    "RL Overall Win Rate",
    color="white",
    fontsize=14
)

plt.tight_layout()

plt.show()

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
# PER MATCHUP
# =====================================================

for matchup in MATCHUPS:

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(12, 6)
    )

    fig.patch.set_facecolor(
        bg_color
    )

    baseline_values = baseline_matchup[
        matchup
    ]

    rl_values = rl_matchup[
        matchup
    ]

    # =================================================
    # BASELINE
    # =================================================

    axes[0].set_facecolor(
        bg_color
    )

    axes[0].pie(
        [
            baseline_values["P1"],
            baseline_values["P2"]
        ],
        labels=[
            "P1 Wins",
            "P2 Wins"
        ],
        autopct="%1.1f%%",
        colors=pie_colors,
        textprops={
            "color": "white",
            "fontsize": 11
        }
    )

    axes[0].set_title(
        f"Baseline - {matchup}",
        color="white",
        fontsize=13
    )

    # =================================================
    # RL
    # =================================================

    axes[1].set_facecolor(
        bg_color
    )

    axes[1].pie(
        [
            rl_values["P1"],
            rl_values["P2"]
        ],
        labels=[
            "P1 Wins",
            "P2 Wins"
        ],
        autopct="%1.1f%%",
        colors=pie_colors,
        textprops={
            "color": "white",
            "fontsize": 11
        }
    )

    axes[1].set_title(
        f"RL - {matchup}",
        color="white",
        fontsize=13
    )

    plt.tight_layout()

    plt.show()

    # =================================================
    # PRINT
    # =================================================

    print("\n==============================")
    print(matchup.upper())
    print("==============================")

    print("Baseline:")
    print(baseline_values)

    print("RL:")
    print(rl_values)
