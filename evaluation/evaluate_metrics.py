import numpy as np

from utils import (
    load_dataset,
    group_by_round
)

# =====================================================
# CONFIG
# =====================================================

DATASET = "dataset_rl_clean_3.jsonl"

# close match:
# winner remaining hp <= 25%

CLOSE_MATCH_THRESHOLD = 0.25

# stomp / snowball:
# one side dominates heavily

SNOWBALL_START_THRESHOLD = 0.40
SNOWBALL_END_THRESHOLD = 0.60

# comeback:
# disadvantaged side nearly dead
# but wins

COMEBACK_LOW_HP = 0.15
COMEBACK_ENEMY_HP = 0.50
COMEBACK_END_DIFF = 0.20

# =====================================================
# LOAD
# =====================================================

data = load_dataset(DATASET)

rounds = group_by_round(data)

# =====================================================
# METRICS
# =====================================================

close_matches = 0

snowball_matches = 0

comeback_success = 0

end_hp_diffs = []

# =====================================================
# PER ROUND
# =====================================================

for round_id, samples in rounds.items():

    if len(samples) < 2:
        continue

    first_state = samples[0]["state"]

    middle_state = samples[
        len(samples) // 2
    ]["state"]

    final_state = samples[-1]["next_state"]

    # =================================================
    # END MATCH HP DIFF
    # =================================================

    final_gap = abs(
        final_state["p1_hp_ratio"]
        -
        final_state["p2_hp_ratio"]
    )

    end_hp_diffs.append(final_gap)

    # =================================================
    # CLOSE MATCH
    # =================================================

    winner_hp = max(
        final_state["p1_hp_ratio"],
        final_state["p2_hp_ratio"]
    )

    if winner_hp <= CLOSE_MATCH_THRESHOLD:

        close_matches += 1

    # =================================================
    # SNOWBALL
    # =================================================

    p1_mid_hp = middle_state["p1_hp_ratio"]
    p2_mid_hp = middle_state["p2_hp_ratio"]
    mid_gap = abs(middle_state["hp_ratio_diff"])

    if ( p1_mid_hp > 0.70 and mid_gap >= SNOWBALL_START_THRESHOLD ):

        if final_gap > SNOWBALL_END_THRESHOLD:

            snowball_matches += 1
    elif ( p2_mid_hp > 0.70 and mid_gap <= -SNOWBALL_START_THRESHOLD ):

        if final_gap < -SNOWBALL_END_THRESHOLD:

            snowball_matches += 1

    # =================================================
    # COMEBACK
    # =================================================

    p1_comeback_candidate = False
    p2_comeback_candidate = False

    # scan all states in round

    for sample in samples:

        state = sample["state"]

        p1_hp = state["p1_hp_ratio"]
        p2_hp = state["p2_hp_ratio"]

        # p1 heavily disadvantaged

        if (
            p1_hp < 0.40
            and
            (p2_hp - p1_hp) > 0.40
        ):

            p1_comeback_candidate = True

        # p2 heavily disadvantaged

        elif (
            p2_hp < 0.40
            and
            (p1_hp - p2_hp) > 0.40
        ):

            p2_comeback_candidate = True

    # =================================================
    # FINAL RESULT
    # =================================================

    p1_final_hp = final_state["p1_hp_ratio"]
    p2_final_hp = final_state["p2_hp_ratio"]

    # actual comeback win only

    if (
        p1_comeback_candidate
        and
        p1_final_hp > p2_final_hp
    ):

        comeback_success += 1

    elif (
        p2_comeback_candidate
        and
        p2_final_hp > p1_final_hp
    ):

        comeback_success += 1

# =====================================================
# FINAL METRICS
# =====================================================

total_rounds = len(rounds)

close_match_ratio = (
    close_matches
    /
    total_rounds
) * 100

snowball_ratio = (
    snowball_matches
    /
    total_rounds
) * 100

comeback_rate = (
    comeback_success
    /
    total_rounds
) * 100

avg_end_hp_diff = np.mean(end_hp_diffs)

median_end_hp_diff = np.median(end_hp_diffs)

std_end_hp_diff = np.std(end_hp_diffs)

# =====================================================
# PRINT
# =====================================================

print("=" * 60)
print("🎯 GAMEPLAY EVALUATION METRICS")
print("=" * 60)

print(f"📦 TOTAL ROUNDS : {total_rounds}")

print()

print("=" * 60)
print("⚔ CLOSE MATCH RATIO")
print("=" * 60)

print(
    f"CLOSE MATCHES : "
    f"{close_matches}"
)

print(
    f"CLOSE MATCH RATIO : "
    f"{close_match_ratio:.2f}%"
)

print()

print("=" * 60)
print("❄ SNOWBALL METRICS")
print("=" * 60)

print(
    f"SNOWBALL MATCHES : "
    f"{snowball_matches}"
)

print(
    f"SNOWBALL RATIO : "
    f"{snowball_ratio:.2f}%"
)

print()

print("=" * 60)
print("🔥 COMEBACK METRICS")
print("=" * 60)

print(
    f"COMEBACK SUCCESS : "
    f"{comeback_success}"
)

print(
    f"COMEBACK RATE : "
    f"{comeback_rate:.2f}%"
)

print()

print("=" * 60)
print("📉 MATCH-END HP DIFF")
print("=" * 60)

print(
    f"AVG HP DIFF    : "
    f"{avg_end_hp_diff:.4f}"
)

print(
    f"MEDIAN HP DIFF : "
    f"{median_end_hp_diff:.4f}"
)

print(
    f"STD HP DIFF    : "
    f"{std_end_hp_diff:.4f}"
)

print()

print("=" * 60)
print("✅ EVALUATION COMPLETE")
print("=" * 60)
