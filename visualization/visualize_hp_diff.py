import numpy as np
import matplotlib.pyplot as plt

from scipy.stats import gaussian_kde

from utils import load_dataset

# =====================================================
# DATASETS
# =====================================================

BASELINE_DATASET = "dataset_v2_clean.jsonl"
RL_DATASET = "dataset_rl_clean.jsonl"

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

baseline_data = load_dataset(BASELINE_DATASET)
rl_data = load_dataset(RL_DATASET)

# =====================================================
# CONVERT HP RATIO -> REAL HP DIFF
# =====================================================

def compute_real_hp_diff(sample):

    state = sample["state"]

    p1_char = state["p1_character"].lower()
    p2_char = state["p2_character"].lower()

    p1_max_hp = MAX_HP[p1_char]
    p2_max_hp = MAX_HP[p2_char]

    p1_hp = (
        state["p1_hp_ratio"]
        * p1_max_hp
    )

    p2_hp = (
        state["p2_hp_ratio"]
        * p2_max_hp
    )

    return p1_hp - p2_hp

# =====================================================
# BUILD ARRAYS
# =====================================================

baseline_hp_diff = np.array([
    compute_real_hp_diff(sample)
    for sample in baseline_data
])

rl_hp_diff = np.array([
    compute_real_hp_diff(sample)
    for sample in rl_data
])

# =====================================================
# KDE
# =====================================================

x = np.linspace(-1000, 1000, 1000)

baseline_kde = gaussian_kde(
    baseline_hp_diff
)

rl_kde = gaussian_kde(
    rl_hp_diff
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
# KDE LINES
# =====================================================

# BASELINE
ax.plot(
    x,
    baseline_kde(x),
    linestyle="--",
    linewidth=2.5,
    color="#4fc3f7",
    label="Baseline"
)

# RL
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
    "HP Difference Distribution",
    color="white",
    fontsize=16
)

ax.set_xlabel(
    "HP Difference (P1 HP - P2 HP)",
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
# SHOW
# =====================================================

plt.tight_layout()

plt.show()
