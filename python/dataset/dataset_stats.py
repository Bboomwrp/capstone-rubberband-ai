import json
import statistics

from collections import defaultdict, Counter

DATASET_PATH = "dataset_v3.jsonl"

# =====================================================
# LOAD DATASET
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
print("📦 DATASET STATS")
print("=" * 60)

print(f"📊 TOTAL SAMPLES : {len(data)}")

if len(data) == 0:
    exit()

# =====================================================
# ROUND GROUPING
# =====================================================

rounds = defaultdict(list)

for sample in data:

    round_id = sample.get("round_id", -1)

    rounds[round_id].append(sample)

print(f"🎮 TOTAL ROUNDS  : {len(rounds)}")

# =====================================================
# ACTION DISTRIBUTION
# =====================================================

action_counter = Counter()

boost_active_counter = 0

for sample in data:

    action = sample.get("action", "NONE")

    action_counter[action] += 1

    if sample["state"].get(
        "is_boost_active",
        False
    ):
        boost_active_counter += 1

print("\n" + "=" * 60)
print("⚔ ACTION DISTRIBUTION")
print("=" * 60)

for action, count in action_counter.items():

    pct = (
        count / len(data)
    ) * 100

    print(
        f"{action:15s}"
        f": {count:6d}"
        f" ({pct:.2f}%)"
    )

print(
    f"\n🔥 BOOST ACTIVE STATES : "
    f"{boost_active_counter}"
)

# =====================================================
# MATCHUP DISTRIBUTION
# =====================================================

matchup_counter = Counter()

for round_id, samples in rounds.items():

    if len(samples) == 0:
        continue

    state = samples[0]["state"]

    matchup = (
        f'{state["p1_character"]}'
        f'_vs_'
        f'{state["p2_character"]}'
    )

    matchup_counter[matchup] += 1

print("\n" + "=" * 60)
print("🥊 MATCHUP DISTRIBUTION")
print("=" * 60)

for matchup, count in matchup_counter.items():

    pct = (
        count / len(rounds)
    ) * 100

    print(
        f"{matchup:20s}"
        f": {count:5d}"
        f" ({pct:.2f}%)"
    )

# =====================================================
# ROUND DURATION
# =====================================================

durations = []

samples_per_round = []

for round_id, samples in rounds.items():

    if len(samples) == 0:
        continue

    start_time = samples[0]["state"]["time"]
    end_time = samples[-1]["next_state"]["time"]

    duration = (
        (start_time - end_time)
        * 99.0
    )

    durations.append(duration)

    samples_per_round.append(
        len(samples)
    )

print("\n" + "=" * 60)
print("⏱ ROUND STATS")
print("=" * 60)

print(
    f"AVG ROUND DURATION : "
    f"{statistics.mean(durations):.2f} sec"
)

print(
    f"MIN ROUND DURATION : "
    f"{min(durations):.2f} sec"
)

print(
    f"MAX ROUND DURATION : "
    f"{max(durations):.2f} sec"
)

print()

print(
    f"AVG SAMPLES/ROUND  : "
    f"{statistics.mean(samples_per_round):.2f}"
)

# =====================================================
# BOOSTS PER ROUND
# =====================================================

boost_per_round = []

for round_id, samples in rounds.items():

    boost_count = 0

    for sample in samples:

        action = sample.get("action", "NONE")

        if action != "NONE":
            boost_count += 1

    boost_per_round.append(boost_count)

print("\n" + "=" * 60)
print("🚀 BOOST STATS")
print("=" * 60)

print(
    f"AVG BOOSTS/ROUND : "
    f"{statistics.mean(boost_per_round):.2f}"
)

print(
    f"MAX BOOSTS/ROUND : "
    f"{max(boost_per_round)}"
)

# =====================================================
# TERMINAL CHECK
# =====================================================

terminal_count = 0

for sample in data:

    if sample["next_state"].get(
        "done",
        False
    ):
        terminal_count += 1

print("\n" + "=" * 60)
print("🏁 TERMINAL STATS")
print("=" * 60)

print(
    f"TERMINAL STATES : "
    f"{terminal_count}"
)

print(
    f"TERMINAL RATIO  : "
    f"{(terminal_count / len(data)) * 100:.2f}%"
)

# =====================================================
# DUPLICATE TRANSITION CHECK
# =====================================================

duplicate_count = 0

for sample in data:

    state = sample["state"]
    next_state = sample["next_state"]

    same = (

        state["time"]
        ==
        next_state["time"]

        and

        state["p1_hp_ratio"]
        ==
        next_state["p1_hp_ratio"]

        and

        state["p2_hp_ratio"]
        ==
        next_state["p2_hp_ratio"]

        and

        state["distance"]
        ==
        next_state["distance"]
    )

    if same:
        duplicate_count += 1

print("\n" + "=" * 60)
print("🧹 DUPLICATE CHECK")
print("=" * 60)

print(
    f"POSSIBLE DUPLICATES : "
    f"{duplicate_count}"
)

print(
    f"DUPLICATE RATIO     : "
    f"{(duplicate_count / len(data)) * 100:.2f}%"
)

# =====================================================
# HP DELTA STATS
# =====================================================

hp_deltas = []

gauge_deltas = []

for sample in data:

    state = sample["state"]
    next_state = sample["next_state"]

    hp_delta = abs(

        state["hp_ratio_diff"]

        -

        next_state["hp_ratio_diff"]
    )

    gauge_delta = abs(

        (
            next_state["p1_gauge_ratio"]
            -
            state["p1_gauge_ratio"]
        )

        -

        (
            next_state["p2_gauge_ratio"]
            -
            state["p2_gauge_ratio"]
        )
    )

    hp_deltas.append(hp_delta)

    gauge_deltas.append(gauge_delta)

print("\n" + "=" * 60)
print("📉 TRANSITION STATS")
print("=" * 60)

print(
    f"AVG HP DELTA      : "
    f"{statistics.mean(hp_deltas):.4f}"
)

print(
    f"MAX HP DELTA      : "
    f"{max(hp_deltas):.4f}"
)

print()

print(
    f"AVG GAUGE DELTA   : "
    f"{statistics.mean(gauge_deltas):.4f}"
)

print(
    f"MAX GAUGE DELTA   : "
    f"{max(gauge_deltas):.4f}"
)

# =====================================================
# REWARD STATS (OPTIONAL)
# =====================================================

if "reward" in data[0]:

    rewards = []

    for sample in data:

        rewards.append(
            sample["reward"]
        )

    print("\n" + "=" * 60)
    print("🎯 REWARD STATS")
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

print("\n" + "=" * 60)
print("✅ DATASET CHECK COMPLETE")
print("=" * 60)
