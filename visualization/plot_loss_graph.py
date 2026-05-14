import os
import json

import matplotlib.pyplot as plt

# =====================================================
# PATHS
# =====================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PROJECT_ROOT = os.path.dirname(BASE_DIR)

LOSS_FILE = os.path.join(
    PROJECT_ROOT,
    "python",
    "models",
    "loss_history.json"
)

OUTPUT_DIR = (
    r"D:\capstone-rubberband-ai"
    r"\visualization"
    r"\visualize_graphic_v3"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

OUTPUT_PATH = os.path.join(
    OUTPUT_DIR,
    "loss_graph.png"
)

# =====================================================
# LOAD
# =====================================================

with open(
    LOSS_FILE,
    "r"
) as f:

    history = json.load(f)

train_loss = history["train_loss"]

val_loss = history["val_loss"]

epochs = list(
    range(
        1,
        len(train_loss) + 1
    )
)

# =====================================================
# STYLE
# =====================================================

plt.style.use("seaborn-v0_8-whitegrid")

# =====================================================
# FIGURE
# =====================================================

plt.figure(figsize=(10, 6))

# =====================================================
# PLOT
# =====================================================

plt.plot(
    epochs,
    train_loss,
    marker="o",
    linewidth=2.5,
    markersize=5,
    label="Train Loss"
)

plt.plot(
    epochs,
    val_loss,
    marker="o",
    linewidth=2.5,
    markersize=5,
    label="Validation Loss"
)

# =====================================================
# LABELS
# =====================================================

plt.title(
    "Training and Validation Loss",
    fontsize=18,
    fontweight="bold"
)

plt.xlabel(
    "Epoch",
    fontsize=13
)

plt.ylabel(
    "Smooth L1 Loss",
    fontsize=13
)

# =====================================================
# X TICKS
# =====================================================

plt.xticks(
    [0, 5, 10, 15, 20, 25],
    fontsize=11
)

plt.yticks(
    fontsize=11
)

# =====================================================
# LEGEND
# =====================================================

plt.legend(
    fontsize=11
)

# =====================================================
# GRID
# =====================================================

plt.grid(
    alpha=0.3
)

# =====================================================
# LAYOUT
# =====================================================

plt.tight_layout()

# =====================================================
# SAVE
# =====================================================

plt.savefig(
    OUTPUT_PATH,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print()
print("=" * 60)
print("✅ LOSS GRAPH SAVED")
print("=" * 60)

print(f"OUTPUT: {OUTPUT_PATH}")
