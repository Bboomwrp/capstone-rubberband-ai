import json
import time
import os
import random


BASE_PATH = r"C:\Users\booms\AppData\LocalLow\DefaultCompany\Fighting Game"

STATE_FILE = os.path.join(BASE_PATH, "rl_state.json")
ACTION_FILE = os.path.join(BASE_PATH, "rl_action.json")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
os.makedirs(DATASET_DIR, exist_ok=True)
DATASET_FILE = os.path.join(DATASET_DIR, "dataset_baseline.jsonl")

def read_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return None

def write_action(action, value):

    payload = {
        "action": action,
        "value": value
    }

    for attempt in range(5):

        try:

            with open(ACTION_FILE, "w") as f:

                json.dump(payload, f)

            return

        except PermissionError:

            print(
                f"⚠ ACTION FILE LOCKED "
                f"(attempt {attempt+1})"
            )

            time.sleep(0.05)

    print("❌ FAILED TO WRITE ACTION")

def policy( state, epsilon=0.18):

    p1_hp = state["p1_hp_ratio"]
    p2_hp = state["p2_hp_ratio"]

    hp_gap = abs(
        state["hp_ratio_diff"]
    )

    p1_gauge = state["p1_gauge_ratio"]
    p2_gauge = state["p2_gauge_ratio"]

    p1_ultra = state["p1_ultra_gauge_ratio"]
    p2_ultra = state["p2_ultra_gauge_ratio"]

    gauge_gap = abs(
        p1_gauge - p2_gauge
    )

    ultra_gap = abs(
        p1_ultra - p2_ultra
    )

    time_left = state["time"]

    # =================================================
    # PRESSURE ESTIMATION
    # =================================================

    pressure_diff = abs(

        state["p1_hits_received"]

        -

        state["p1_hits_landed"]
    )

    # =================================================
    # CONSTRAINTS
    # =================================================

    # EARLY ROUND
    # avoid immediate rubberband

    if (p1_hp > 0.90 and p2_hp > 0.90) or time_left > 0.92:
        return "NONE", 1.0

    # VERY CLOSE MATCH
    # no unnecessary intervention

    if hp_gap < 0.10:
        return "NONE", 1.0

    # CRITICAL FINISH
    # let gameplay decide ending

    if p1_hp < 0.10 and p2_hp < 0.10:
        return "NONE", 1.0

    # =================================================
    # RANDOM EXPLORATION
    # =================================================

    if random.random() < epsilon:

        actions = [
            "NONE",
            "BOOST_ATTACK",
            "BOOST_DEFENSE",
            "BOOST_GAUGE"
        ]

        weights = [
            0.40,  # NONE
            0.35,  # ATTACK
            0.15,  # DEFENSE
            0.10   # GAUGE
        ]

        action = random.choices(
            actions,
            weights=weights,
            k=1
        )[0]

        # adaptive boost strength

        if hp_gap > 0.35:
            value = 1.30

        elif hp_gap > 0.22:
            value = 1.20

        elif hp_gap > 0.12:
            value = 1.10

        else:
            value = 1.05

        return action, value

    # =================================================
    # HEAVY DISADVANTAGE
    # =================================================

    if hp_gap > 0.35:

        # under strong pressure
        # stabilize survival first

        if pressure_diff > 4:

            return "BOOST_DEFENSE", 1.30

        # otherwise encourage comeback offense

        return "BOOST_ATTACK", 1.30

    # =================================================
    # MID DISADVANTAGE
    # =================================================

    elif hp_gap > 0.20:

        # currently getting overwhelmed

        if pressure_diff > 2:

            return "BOOST_DEFENSE", 1.20

        # offensive momentum possible

        return "BOOST_ATTACK", 1.20

    # =================================================
    # RESOURCE COMEBACK
    # =================================================

    elif (
        gauge_gap > 0.25
        or
        ultra_gap > 0.25
    ):

        # late game:
        # gauge less valuable

        if time_left < 0.72 or min(p1_hp, p2_hp) < 0.20:

            return "BOOST_ATTACK", 1.10

        return "BOOST_GAUGE", 1.15

    # =================================================
    # LIGHT DISADVANTAGE
    # =================================================

    elif hp_gap > 0.10:

        # mild pressure -> stabilize

        if pressure_diff > 3:

            return "BOOST_DEFENSE", 1.10

        return "BOOST_ATTACK", 1.10

    # =================================================
    # DEFAULT
    # =================================================

    return "NONE", 1.0

def save_dataset(prev, action, action_value, curr):

    global SAMPLE_ID
    global ROUND_ID

    SAMPLE_ID += 1

    # =====================================================
    # CHARACTER INFO
    # =====================================================

    p1_character = prev.get(
        "p1_character",
        "unknown"
    ).lower()

    p2_character = prev.get(
        "p2_character",
        "unknown"
    ).lower()

    # =====================================================
    # MATCHUP
    # =====================================================

    matchup = (
        p1_character
        + "_vs_"
        + p2_character
    )

    # =====================================================
    # METADATA
    # =====================================================

    metadata = {

        "dataset_version": "v3",
        # ---------------------------------------------
        # dataset indexing
        # ---------------------------------------------

        "sample_id": SAMPLE_ID,

        "round_id": ROUND_ID,

        # ---------------------------------------------
        # matchup info
        # ---------------------------------------------

        "matchup": matchup,

        "p1_character": p1_character,

        "p2_character": p2_character,

        # ---------------------------------------------
        # gameplay context
        # ---------------------------------------------

        "action": action,

        "action_value": action_value,

        # ---------------------------------------------
        # state transition
        # ---------------------------------------------

        "state": prev,

        "next_state": curr
    }

    # =====================================================
    # SAVE
    # =====================================================

    with open(DATASET_FILE, "a") as f:

        f.write(
            json.dumps(metadata)
            + "\n"
        )

def load_dataset_metadata():

    if not os.path.exists(DATASET_FILE):

        return 1, 0

    try:

        with open(DATASET_FILE, "r") as f:

            lines = f.readlines()

            if len(lines) == 0:
                return 1, 0

            last_entry = json.loads(lines[-1])

            last_round_id = last_entry.get(
                "round_id",
                0
            )

            last_sample_id = last_entry.get(
                "sample_id",
                0
            )

            return (
                last_round_id + 1,
                last_sample_id
            )

    except Exception as e:

        print(f"⚠ Failed to load dataset metadata: {e}")

        return 1, 0

def is_real_fight(state):
    if state.get("inMatch", False) is False:
        return False
    
    if state.get("time", 1.0) >= 0.99:
        return False
    return True

def is_terminal(prev, curr):
    if prev is None or curr is None:
        return False

    p1_dead = prev["p1_hp_ratio"] > 0 and curr["p1_hp_ratio"] <= 0
    p2_dead = prev["p2_hp_ratio"] > 0 and curr["p2_hp_ratio"] <= 0

    return p1_dead or p2_dead

def make_signature(prev, curr):
    return (
        round(prev["p1_hp_ratio"], 3),
        round(prev["p2_hp_ratio"], 3),
        round(curr["p1_hp_ratio"], 3),
        round(curr["p2_hp_ratio"], 3)
    )

def is_same_state(a, b):
    return abs(a["p1_hp_ratio"] - b["p1_hp_ratio"]) < 1e-3 and \
           abs(a["p2_hp_ratio"] - b["p2_hp_ratio"]) < 1e-3 and \
           abs(a["time"] - b["time"]) < 1e-3

# =====================================================
# METADATA
# =====================================================

ROUND_ID, SAMPLE_ID = load_dataset_metadata()

print(f"📂 RESUME ROUND_ID: {ROUND_ID}")
print(f"📂 RESUME SAMPLE_ID: {SAMPLE_ID}")


# ================= LOOP =================

print("🤖 RL Agent started")

write_action("NONE", 1.0)

prev_state = None
last_done = False
episode_done = False
last_terminal_signature = None
startup_synced = False
last_action_time = 0

while True:
    state = read_json(STATE_FILE)

    if state is None:
        time.sleep(0.1)
        continue

    # ================= TERMINAL DETECTION =================
    if state.get("done", False):

        if prev_state is not None:

            sig = make_signature(prev_state, state)

            # prevent duplicate terminal
            if sig != last_terminal_signature:

                last_terminal_signature = sig

                save_dataset(prev_state, "NONE", 1.0, state)

                print("🏁 TERMINAL SAVED")

                ROUND_ID += 1

                print(f"🎮 ROUND ID: {ROUND_ID}")

        episode_done = True
        startup_synced = False
        prev_state = None

        continue

    # =====================================================
    # STARTUP SYNC
    # =====================================================

    if not startup_synced:

        # wait until real match starts
        if not state.get("inMatch", False):

            time.sleep(0.1)

            continue

        # wait until round actually begins
        if state.get("time", 1.0) > 0.995:

            time.sleep(0.05)

            continue

        startup_synced = True

        print("✅ STARTUP SYNCED")

        write_action("NONE", 1.0)

        prev_state = state

        continue

    # ================= FORCE UNSTUCK =================
    if episode_done and prev_state is None:
        if ( state.get("inMatch", False) and state.get("time", 1.0) < 0.95):
            episode_done = False

    # ================= BLOCK AFTER DONE =================
    if episode_done:

        if state["time"] < 0.95:

            episode_done = False

    # ================= FILTER PREVIEW =================
    if state.get("time", 1.0) >= 0.99:
        time.sleep(0.1)
        continue

    # skip full HP (ยังไม่เริ่มสู้)
    if abs(state["hp_ratio_diff"]) < 1e-5 and state["p1_hp_ratio"] > 0.99 and state["p2_hp_ratio"] > 0.99:
        time.sleep(0.1)
        continue

    if not is_real_fight(state):
        time.sleep(0.1)
        continue

    # ================= TERMINAL FLAG =================
    if state["p1_hp_ratio"] <= 0 or state["p2_hp_ratio"] <= 0:
        state["done"] = True

    # ❗ กัน terminal state หลุดเข้า logic
    if state.get("done", False) and prev_state is None:
        continue

    # ❗ กัน prev_state ที่เป็น terminal
    if prev_state is not None and prev_state.get("done", False):
        prev_state = None
        continue

    # ================= DUPLICATE STATE =================
    if prev_state is not None and is_same_state(state, prev_state):
        time.sleep(0.1)
        continue

    # ================= BLOCK NORMAL FLOW IF DONE =================
    if state.get("done", False):
        prev_state = None
        continue

    # ================= WHEN BOOST IS ACTIVATING =================
    if state.get("is_boost_active", False):

        active_action = state.get(
            "current_action",
            "NONE"
        )

        value = state.get(
            "action_value",
            1.0
        )

        # keep current boost action active
        write_action(
            active_action,
            value
        )

        time.sleep(0.3)

        next_state = read_json(STATE_FILE)

        if next_state is None:
            continue

        if is_same_state(state, next_state):
            continue

        save_dataset(
            state,
            active_action,
            value,
            next_state
        )

        prev_state = next_state

        print(
            f"👀 OBSERVING ACTIVE BOOST: {active_action}"
        )

        continue
    
    # action, value = policy(state)
    action = "NONE"
    value = 1.0

    if action == "NONE":

        write_action("NONE", 1.0)

        time.sleep(0.5)

        next_state = read_json(STATE_FILE)

        if next_state is None:
            continue

        # skip stale transition
        if is_same_state(state, next_state):
            continue

        save_dataset(
            state,
            "NONE",
            1.0,
            next_state
        )

        print(f"📊 NONE")

        prev_state = next_state

        continue

    
    write_action(action, value)
    last_action_time = time.time()

    time.sleep(1.0)

    next_state = read_json(STATE_FILE)
    
    # invalid transition
    if next_state is None:
        continue
    
    if is_same_state(state, next_state):

        print("⚠ SAME STATE TRANSITION")

        prev_state = state

        continue
    
    # action rejected by Unity
    if next_state.get("current_action", "NONE") != action:

        print("⚠ ACTION NOT APPLIED")

        prev_state = state

        continue
    if not next_state.get("is_boost_active", False):

        print("⚠ BOOST NOT ACTIVE")

        prev_state = state

        continue
    # ================= VALIDATE NEXT STATE =================
    if next_state.get("time", 1.0) >= 0.99:
        continue

    # ❗ กันข้าม round
    if next_state["time"] > state["time"]:
        continue

    # mark done
    if next_state["p1_hp_ratio"] <= 0 or next_state["p2_hp_ratio"] <= 0:
        next_state["done"] = True

    # ❗ กัน terminal ซ้ำใน normal flow
    if next_state.get("done", False):
        continue

    # ================= SAVE NORMAL =================
    save_dataset(state, action, value, next_state)

    print(f"📊 {action} | value: {value:.2f}")

    # ================= UPDATE =================
    prev_state = state