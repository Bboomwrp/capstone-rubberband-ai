import json
import os
import numpy as np

# =====================================================
# PATHS
# =====================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATASET_DIR = os.path.join(
    BASE_DIR,
    "dataset"
)

RAW_DATASET = os.path.join(
    DATASET_DIR,
    "dataset_v3_raw.jsonl"
)

OUTPUT_DATASET = os.path.join(
    DATASET_DIR,
    "dataset_v3_rewarded.jsonl"
)

# =====================================================
# WEIGHTS
# =====================================================

W_COMEBACK = 0.35
W_DAMAGE = 0.25
W_RESOURCE = 0.15
W_PACING = 0.15
W_TERMINAL = 0.10

# =====================================================
# COMPUTE REWARD
# =====================================================

def compute_reward(
    state,
    next_state
):

    # =============================================
    # HP LOSSES
    # =============================================

    p1_loss = (

        state["p1_hp_ratio"] - next_state["p1_hp_ratio"]
    )

    p2_loss = (

        state["p2_hp_ratio"] - next_state["p2_hp_ratio"]
    )

    # =============================================
    # GAP REDUCTION
    # =============================================

    prev_gap = abs(
        state["hp_ratio_diff"]
    )

    next_gap = abs(
        next_state["hp_ratio_diff"]
    )

    gap_reduction = (
        prev_gap - next_gap
    )

    comeback_reward = np.clip(
        gap_reduction,
        -1.0,
        1.0
    )

    # =============================================
    # DAMAGE BALANCE
    # =============================================

    net_damage = (
        p2_loss - p1_loss
    )

    damage_reward = np.clip(
        net_damage,
        -1.0,
        1.0
    )

    # =============================================
    # RESOURCE MOMENTUM
    # =============================================

    p1_resource = (

        (next_state["p1_gauge_ratio"] - state["p1_gauge_ratio"])

        +

        (next_state["p1_ultra_gauge_ratio"] - state["p1_ultra_gauge_ratio"])
    )

    p2_resource = (

        (next_state["p2_gauge_ratio"] - state["p2_gauge_ratio"])

        +

        (next_state["p2_ultra_gauge_ratio"] - state["p2_ultra_gauge_ratio"])
    )

    resource_reward = np.clip(
        p1_resource + p2_resource,
        -1.0,
        1.0
    )

    # =============================================
    # PACING / INTERACTION
    # =============================================

    interaction = (

        abs(p1_loss)
        + abs(p2_loss)

        +

        abs(p1_resource)
        + abs(p2_resource)
    )

    pacing_reward = np.clip(
        interaction,
        0.0,
        1.0
    )

    # =============================================
    # TERMINAL QUALITY
    # =============================================

    terminal_reward = 0.0

    if next_state.get(
        "done",
        False
    ):

        final_gap = abs(
            next_state[
                "hp_ratio_diff"
            ]
        )

        terminal_reward = np.clip(
            1.0 - final_gap,
            0.0,
            1.0
        )

    # =============================================
    # FINAL
    # =============================================

    reward = (

        comeback_reward
        * W_COMEBACK

        +

        damage_reward
        * W_DAMAGE

        +

        resource_reward
        * W_RESOURCE

        +

        pacing_reward
        * W_PACING

        +

        terminal_reward
        * W_TERMINAL
    )

    reward = np.clip(
        reward,
        -1.0,
        1.0
    )

    return float(reward)

# =====================================================
# PROCESS DATASET
# =====================================================

with open(RAW_DATASET, "r") as f:

    lines = f.readlines()

processed = []

for line in lines:

    sample = json.loads(line)

    reward = compute_reward(
        sample["state"],
        sample["next_state"]
    )

    sample["reward"] = reward

    processed.append(sample)

# =====================================================
# SAVE
# =====================================================

with open(OUTPUT_DATASET, "w") as f:

    for sample in processed:

        f.write(
            json.dumps(sample)
            + "\n"
        )

print("✅ Rewarded dataset saved")
print(OUTPUT_DATASET)
