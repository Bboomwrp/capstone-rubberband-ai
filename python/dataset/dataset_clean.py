# dataset_clean.py

import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_FILE = os.path.join(
    BASE_DIR,
    "dataset.jsonl"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "dataset_clean.jsonl"
)

# =========================================================
# CONFIG
# =========================================================

TIME_EPS = 1e-5
HP_EPS = 1e-5

# =========================================================
# HELPERS
# =========================================================

def is_same_state(a, b):

    keys = [
        "time",
        "p1_hp",
        "p2_hp",
        "hp_diff",
        "hp_ratio",
        "p1_gauge",
        "p2_gauge",
        "distance"
    ]

    for k in keys:

        if abs(a.get(k, 0) - b.get(k, 0)) > 1e-5:
            return False

    return True


def is_invalid_transition(state, next_state):

    # same state
    if is_same_state(state, next_state):
        return True

    # invalid timer
    if next_state["time"] > state["time"] + TIME_EPS:
        return True

    # preview / non-fight
    if state["time"] >= 0.99:
        return True

    return False


# =========================================================
# CLEAN
# =========================================================

print("🧹 Cleaning dataset...")

cleaned = []
seen = set()

removed_duplicate = 0
removed_invalid = 0
removed_terminal_duplicate = 0

last_terminal_signature = None

with open(INPUT_FILE, "r", encoding="utf-8") as f:

    for line in f:

        try:
            data = json.loads(line)

            state = data["state"]
            next_state = data["next_state"]

            # =============================================
            # INVALID TRANSITION
            # =============================================

            if is_invalid_transition(state, next_state):
                removed_invalid += 1
                continue

            # =============================================
            # TERMINAL DUPLICATE
            # =============================================

            done = next_state.get("done", False)

            if done:

                terminal_signature = (
                    round(next_state["p1_hp"], 3),
                    round(next_state["p2_hp"], 3),
                    round(next_state["time"], 3)
                )

                if terminal_signature == last_terminal_signature:
                    removed_terminal_duplicate += 1
                    continue

                last_terminal_signature = terminal_signature

            else:
                last_terminal_signature = None

            # =============================================
            # EXACT DUPLICATE
            # =============================================

            sig = json.dumps(data, sort_keys=True)

            if sig in seen:
                removed_duplicate += 1
                continue

            seen.add(sig)

            cleaned.append(data)

        except Exception as e:
            print("⚠ Skip bad line:", e)

# =========================================================
# SAVE
# =========================================================

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:

    for item in cleaned:
        f.write(json.dumps(item) + "\n")

# =========================================================
# REPORT
# =========================================================

print("\n========== CLEAN REPORT ==========")

print(f"✅ Cleaned samples: {len(cleaned)}")

print(f"❌ Removed invalid: {removed_invalid}")

print(f"❌ Removed duplicates: {removed_duplicate}")

print(f"❌ Removed terminal duplicates: {removed_terminal_duplicate}")

print(f"\n💾 Saved to:")
print(OUTPUT_FILE)