import json
import statistics

from collections import defaultdict

DATASET_PATH = "dataset_v3_rewarded.jsonl"

# =====================================================
# LOAD
# =====================================================

data = []

with open(DATASET_PATH, "r", encoding="utf-8") as f:

    for line in f:

        line = line.strip()

        if not line:
            continue

        try:
            sample = json.loads(line)
            data.append(sample)

        except:
            continue

print("=" * 60)
print("🎯 REWARDED DATASET STATS")
print("=" * 60)

print(f"📦 TOTAL SAMPLES : {len(data)}")

if len(data) == 0:
    exit()

# =====================================================
# REWARD LIST
# =====================================================

rewards = []

for sample in data:

    rewards.append(
        sample["reward"]
    )

# =====================================================
# BASIC REWARD STATS
# =====================================================

print("\n" + "=" * 60)
print("📊 REWARD DISTRIBUTION")
print("=" * 60)

print(
    f"AVG REWARD : "
    f"{statistics.mean(rewards):.4f}"
)

print(
    f"STD REWARD : "
    f"{statistics.stdev(rewards):.4f}"
)

print(
    f"MIN REWARD : "
    f"{min(rewards):.4f}"
)

print(
    f"MAX REWARD : "
    f"{max(rewards):.4f}"
)

# =====================================================
# POSITIVE / NEGATIVE RATIO
# =====================================================

positive = 0
negative = 0
neutral = 0

for r in rewards:

    if r > 0.01:
        positive += 1

    elif r < -0.01:
        negative += 1

    else:
        neutral += 1

print("\n" + "=" * 60)
print("➕➖ REWARD POLARITY")
print("=" * 60)

print(
    f"POSITIVE : {positive}"
    f" ({positive / len(rewards) * 100:.2f}%)"
)

print(
    f"NEGATIVE : {negative}"
    f" ({negative / len(rewards) * 100:.2f}%)"
)

print(
    f"NEUTRAL  : {neutral}"
    f" ({neutral / len(rewards) * 100:.2f}%)"
)

# =====================================================
# REWARD CLIPPING
# =====================================================

clipped_pos = 0
clipped_neg = 0

for r in rewards:

    if r >= 0.99:
        clipped_pos += 1

    if r <= -0.99:
        clipped_neg += 1

print("\n" + "=" * 60)
print("✂ REWARD CLIPPING")
print("=" * 60)

print(
    f"POSITIVE CLIPPED : "
    f"{clipped_pos}"
)

print(
    f"NEGATIVE CLIPPED : "
    f"{clipped_neg}"
)

# =====================================================
# ACTION REWARD STATS
# =====================================================

action_rewards = defaultdict(list)

for sample in data:

    action = sample["action"]

    reward = sample["reward"]

    action_rewards[action].append(reward)

print("\n" + "=" * 60)
print("⚔ ACTION REWARD STATS")
print("=" * 60)

for action, values in action_rewards.items():

    avg_r = statistics.mean(values)

    std_r = (
        statistics.stdev(values)
        if len(values) > 1
        else 0.0
    )

    print(
        f"{action:15s}"
        f"| avg: {avg_r:+.4f} "
        f"| std: {std_r:.4f} "
        f"| n={len(values)}"
    )

# =====================================================
# MATCHUP REWARD STATS
# =====================================================

matchup_rewards = defaultdict(list)

for sample in data:

    state = sample["state"]

    matchup = (
        f'{state["p1_character"]}'
        f'_vs_'
        f'{state["p2_character"]}'
    )

    matchup_rewards[matchup].append(
        sample["reward"]
    )

print("\n" + "=" * 60)
print("🥊 MATCHUP REWARD STATS")
print("=" * 60)

for matchup, values in matchup_rewards.items():

    avg_r = statistics.mean(values)

    print(
        f"{matchup:20s}"
        f": {avg_r:+.4f}"
    )

# =====================================================
# TERMINAL REWARD STATS
# =====================================================

terminal_rewards = []

for sample in data:

    if sample["next_state"].get(
        "done",
        False
    ):

        terminal_rewards.append(
            sample["reward"]
        )

print("\n" + "=" * 60)
print("🏁 TERMINAL REWARD STATS")
print("=" * 60)

if len(terminal_rewards) > 0:

    print(
        f"AVG TERMINAL REWARD : "
        f"{statistics.mean(terminal_rewards):+.4f}"
    )

    print(
        f"MAX TERMINAL REWARD : "
        f"{max(terminal_rewards):+.4f}"
    )

    print(
        f"MIN TERMINAL REWARD : "
        f"{min(terminal_rewards):+.4f}"
    )

# =====================================================
# TOP / BOTTOM REWARDS
# =====================================================

sorted_data = sorted(
    data,
    key=lambda x: x["reward"]
)

lowest = sorted_data[:5]

highest = sorted_data[-5:]

print("\n" + "=" * 60)
print("📉 LOWEST REWARDS")
print("=" * 60)

for s in lowest:

    print(
        f'{s["reward"]:+.4f} '
        f'| {s["action"]}'
    )

print("\n" + "=" * 60)
print("📈 HIGHEST REWARDS")
print("=" * 60)

for s in highest:

    print(
        f'{s["reward"]:+.4f} '
        f'| {s["action"]}'
    )

# =====================================================
# REWARD TEMPORAL CONSISTENCY
# =====================================================

reward_diff = []

for i in range(len(data) - 1):

    r1 = data[i]["reward"]
    r2 = data[i + 1]["reward"]

    reward_diff.append(
        abs(r2 - r1)
    )

print("\n" + "=" * 60)
print("⏳ TEMPORAL CONSISTENCY")
print("=" * 60)

print(
    f"AVG REWARD DELTA : "
    f"{statistics.mean(reward_diff):.4f}"
)

print(
    f"MAX REWARD DELTA : "
    f"{max(reward_diff):.4f}"
)

print("\n" + "=" * 60)
print("✅ REWARD DATASET CHECK COMPLETE")
print("=" * 60)