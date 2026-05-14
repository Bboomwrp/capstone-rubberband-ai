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
    "dataset_v3_clean.jsonl"
)

OUTPUT_DATASET = os.path.join(
    DATASET_DIR,
    "dataset_v3_rewarded.jsonl"
)

# =====================================================
# WEIGHTS
# =====================================================

W_COMEBACK = 0.45
W_SNOWBALL = 0.25
W_PACING = 0.15
W_RESOURCE = 0.05
W_TERMINAL = 0.10

# =====================================================
# COMPUTE REWARD
# =====================================================

def compute_reward(action, state, next_state):
    # =================================================
    # HP GAP REDUCTION
    # =================================================

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

    # =================================================
    # SNOWBALL PENALTY
    # =================================================

    snowball_penalty = np.clip(
        next_gap - prev_gap,
        0.0,
        1.0
    )

    # =================================================
    # INTERACTION / PACING
    # =================================================

    p1_hp_change = abs(

        next_state["p1_hp_ratio"]
        -
        state["p1_hp_ratio"]
    )

    p2_hp_change = abs(

        next_state["p2_hp_ratio"]
        -
        state["p2_hp_ratio"]
    )

    p1_gauge_change = abs(

        next_state["p1_gauge_ratio"]
        -
        state["p1_gauge_ratio"]
    )

    p2_gauge_change = abs(

        next_state["p2_gauge_ratio"]
        -
        state["p2_gauge_ratio"]
    )

    interaction_strength = (

        p1_hp_change
        +
        p2_hp_change

        +
        0.5 * (
            p1_gauge_change
            +
            p2_gauge_change
        )
    )

    pacing_reward = np.clip(
        interaction_strength,
        0.0,
        1.0
    )

    # =================================================
    # RESOURCE ACTIVITY
    # =================================================

    resource_reward = np.clip(

        (
            p1_gauge_change
            +
            p2_gauge_change
        ),

        0.0,
        1.0
    )

    # =================================================
    # TERMINAL QUALITY
    # =================================================

    terminal_reward = 0.0

    if next_state.get(
        "done",
        False
    ):

        final_gap = abs(
            next_state["hp_ratio_diff"]
        )

        # closer ending = better balance

        terminal_reward = np.clip(
            1.0 - final_gap,
            0.0,
            1.0
        )

    # =================================================
    # FINAL WEIGHTED REWARD
    # =================================================

    reward = (

        W_COMEBACK
        * comeback_reward

        -

        W_SNOWBALL
        * snowball_penalty

        +

        W_PACING
        * pacing_reward

        +

        W_RESOURCE
        * resource_reward

        +

        W_TERMINAL
        * terminal_reward
    )

    # =====================================================
    # ACTION EFFECTIVENESS
    # =====================================================

    # determine boosted player
    # RLActionReceiver boosts disadvantaged side

    boosted_is_p1 = (
        state["p1_hp_ratio"]
        <
        state["p2_hp_ratio"]
    )

    if boosted_is_p1:

        boosted_hp_before = state["p1_hp_ratio"]
        boosted_hp_after = next_state["p1_hp_ratio"]

        opponent_hp_before = state["p2_hp_ratio"]
        opponent_hp_after = next_state["p2_hp_ratio"]

        boosted_gauge_before = (
            state["p1_gauge_ratio"]
            +
            state["p1_ultra_gauge_ratio"]
        )

        boosted_gauge_after = (
            next_state["p1_gauge_ratio"]
            +
            next_state["p1_ultra_gauge_ratio"]
        )

        boosted_hits_received_before = (
            state["p1_hits_received"]
        )

        boosted_hits_received_after = (
            next_state["p1_hits_received"]
        )

    else:

        boosted_hp_before = state["p2_hp_ratio"]
        boosted_hp_after = next_state["p2_hp_ratio"]

        opponent_hp_before = state["p1_hp_ratio"]
        opponent_hp_after = next_state["p1_hp_ratio"]

        boosted_gauge_before = (
            state["p2_gauge_ratio"]
            +
            state["p2_ultra_gauge_ratio"]
        )

        boosted_gauge_after = (
            next_state["p2_gauge_ratio"]
            +
            next_state["p2_ultra_gauge_ratio"]
        )

        boosted_hits_received_before = (
            state["p2_hits_received"]
        )

        boosted_hits_received_after = (
            next_state["p2_hits_received"]
        )

    # =====================================================
    # BOOST ATTACK
    # =====================================================

    if action == "BOOST_ATTACK":

        damage_done = max(
            0.0,
            opponent_hp_before
            -
            opponent_hp_after
        )

        reward += (
            damage_done
            * 0.25
        )

    # =====================================================
    # BOOST DEFENSE
    # =====================================================

    elif action == "BOOST_DEFENSE":

        damage_taken = max(
            0.0,
            boosted_hp_before
            -
            boosted_hp_after
        )

        pressure_taken = max(
            0,
            boosted_hits_received_after
            -
            boosted_hits_received_before
        )

        # reward only if actually pressured
        if pressure_taken > 0:

            defense_success = max(
                0.0,
                0.05 - damage_taken
            )

            reward += (
                defense_success
                * 0.12
            )

    # =====================================================
    # BOOST GAUGE
    # =====================================================

    elif action == "BOOST_GAUGE":

        gauge_gain = max(
            0.0,
            boosted_gauge_after
            -
            boosted_gauge_before
        )

        reward += (
            gauge_gain
            * 0.10
        )


    # =================================================
    # NORMALIZE
    # =================================================

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
        sample["action"],
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
