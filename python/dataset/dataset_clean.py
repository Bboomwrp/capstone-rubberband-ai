import json
import math

INPUT_FILE = "dataset_rl_raw_3.jsonl"
OUTPUT_FILE = "dataset_rl_clean_3.jsonl"

required_fields = [
    "state",
    "next_state",
    "action"
]

def is_same_state(a, b):

    keys = [

        "time",

        "p1_hp_ratio",
        "p2_hp_ratio",

        "p1_gauge_ratio",
        "p2_gauge_ratio",

        "p1_ultra_gauge_ratio",
        "p2_ultra_gauge_ratio",

        "distance",

        "done"
    ]

    for k in keys:

        if a.get(k) != b.get(k):
            return False

    return True

def invalid_ratio(x):

    return (
        x is None
        or
        math.isnan(x)
        or
        x < 0.0
        or
        x > 1.0
    )


cleaned = []
removed = 0

with open(INPUT_FILE, "r", encoding="utf-8") as f:

    for line_num, line in enumerate(f):

        try:

            sample = json.loads(line)

        except:
            removed += 1
            continue

        # =================================================
        # REQUIRED FIELDS
        # =================================================

        valid = True

        for field in required_fields:

            if field not in sample:
                valid = False
                break

        if not valid:
            removed += 1
            continue

        state = sample["state"]
        next_state = sample["next_state"]

        # =================================================
        # INVALID RATIOS
        # =================================================

        ratio_keys = [
            "p1_hp_ratio",
            "p2_hp_ratio",
            "p1_gauge_ratio",
            "p2_gauge_ratio",
            "p1_ultra_gauge_ratio",
            "p2_ultra_gauge_ratio"
        ]

        bad_ratio = False

        for key in ratio_keys:

            if invalid_ratio(state.get(key, 0)):
                bad_ratio = True

            if invalid_ratio(next_state.get(key, 0)):
                bad_ratio = True

        if bad_ratio:
            removed += 1
            continue

        # =================================================
        # INVALID TIME FLOW
        # =================================================

        if next_state["done"] is False:

            if next_state["time"] > state["time"]:

                removed += 1
                continue

        # =================================================
        # DUPLICATE TERMINAL
        # =================================================

        if (
            state.get("done", False)
            and
            next_state.get("done", False)
        ):

            removed += 1
            continue

        # =================================================
        # IDENTICAL STATES
        # =================================================

        if is_same_state(state, next_state):

            removed += 1
            continue

        cleaned.append(sample)

# =====================================================
# REWRITE SAMPLE IDS
# =====================================================

for i, sample in enumerate(cleaned):

    sample["sample_id"] = i

# =====================================================
# SAVE CLEAN DATASET
# =====================================================

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:

    for sample in cleaned:

        f.write(
            json.dumps(sample)
            + "\n"
        )

print(f"✅ CLEANED DATASET SAVED")
print(f"📊 ORIGINAL: {line_num + 1}")
print(f"📊 CLEANED : {len(cleaned)}")
print(f"🗑 REMOVED : {removed}")
