import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_FILE = os.path.join(
    BASE_DIR,
    "dataset_clean.jsonl"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "dataset_final.jsonl"
)

# =========================================================
# CONFIG
# =========================================================

SCALE = 100.0

CLIP_MIN = -1.0
CLIP_MAX = 1.0

# =========================================================
# STATS
# =========================================================

count = 0

min_reward_before = float("inf")
max_reward_before = float("-inf")

min_reward_after = float("inf")
max_reward_after = float("-inf")

# =========================================================
# NORMALIZE
# =========================================================

print("⚡ Normalizing rewards...")

with open(INPUT_FILE, "r", encoding="utf-8") as fin, \
     open(OUTPUT_FILE, "w", encoding="utf-8") as fout:

    for line in fin:

        try:
            data = json.loads(line)

            reward = float(data["reward"])

            # =============================================
            # BEFORE STATS
            # =============================================

            min_reward_before = min(
                min_reward_before,
                reward
            )

            max_reward_before = max(
                max_reward_before,
                reward
            )

            # =============================================
            # NORMALIZE
            # =============================================

            reward = reward / SCALE

            # =============================================
            # CLIP
            # =============================================

            reward = max(
                CLIP_MIN,
                min(CLIP_MAX, reward)
            )

            # =============================================
            # SAVE
            # =============================================

            data["reward"] = reward

            fout.write(
                json.dumps(data) + "\n"
            )

            # =============================================
            # AFTER STATS
            # =============================================

            min_reward_after = min(
                min_reward_after,
                reward
            )

            max_reward_after = max(
                max_reward_after,
                reward
            )

            count += 1

        except Exception as e:
            print("⚠ Skip bad line:", e)

# =========================================================
# REPORT
# =========================================================

print("\n========== NORMALIZE REPORT ==========")

print(f"✅ Samples: {count}")

print("\n📉 BEFORE")
print(f"Min reward: {min_reward_before}")
print(f"Max reward: {max_reward_before}")

print("\n📈 AFTER")
print(f"Min reward: {min_reward_after}")
print(f"Max reward: {max_reward_after}")

print("\n💾 Saved to:")
print(OUTPUT_FILE)