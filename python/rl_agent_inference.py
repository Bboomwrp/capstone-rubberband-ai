import os
import json
import time
import random

import torch
import numpy as np

from dqn_model import DQN
from utils import state_to_vector

# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UNITY_PATH = r"C:\Users\booms\AppData\LocalLow\DefaultCompany\Fighting Game"

STATE_FILE = os.path.join(
    UNITY_PATH,
    "rl_state.json"
)

ACTION_FILE = os.path.join(
    UNITY_PATH,
    "rl_action.json"
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "dqn_model.pth"
)

DATASET_DIR = os.path.join(BASE_DIR, "dataset")
os.makedirs(DATASET_DIR, exist_ok=True)
DATASET_FILE = os.path.join(DATASET_DIR, "dataset_rl.jsonl")
# =========================================================
# ACTIONS
# =========================================================

ACTIONS = [
    "NONE",
    "BOOST_ATTACK",
    "BOOST_DEFENSE",
    "BOOST_GAUGE"
]

# =========================================================
# DEVICE
# =========================================================

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print(f"🔥 DEVICE: {DEVICE}")

# =========================================================
# LOAD MODEL
# =========================================================

model = DQN(9, len(ACTIONS)).to(DEVICE)

model.load_state_dict(
    torch.load(MODEL_PATH, map_location=DEVICE)
)

model.eval()

print("✅ MODEL LOADED")

# =========================================================
# HELPERS
# =========================================================

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

def adaptive_boost_value(state, action):

    hp_ratio_diff = abs(
        state["hp_ratio_diff"]
    )

    # =====================================================
    # BASE INTENSITY
    # =====================================================

    if hp_ratio_diff > 0.40:

        intensity = 1.35

    elif hp_ratio_diff > 0.30:

        intensity = 1.25

    elif hp_ratio_diff > 0.20:

        intensity = 1.18

    elif hp_ratio_diff > 0.10:

        intensity = 1.10

    else:

        intensity = 1.05

    # =====================================================
    # ACTION-SPECIFIC ADJUSTMENT
    # =====================================================

    if action == "BOOST_ATTACK":

        value = intensity

    elif action == "BOOST_DEFENSE":

        value = intensity

    elif action == "BOOST_GAUGE":

        value = min(intensity + 0.05, 1.35)

    else:

        value = 1.0

    # =====================================================
    # CLAMP
    # =====================================================

    value = max(
        1.0,
        min(value, 1.40)
    )

    return round(value, 2)

def model_policy(state, epsilon=0.0):

    # =====================================================
    # CONSTRAINTS
    # =====================================================

    p1_hp_ratio = state["p1_hp_ratio"]
    p2_hp_ratio = state["p2_hp_ratio"]

    hp_ratio_diff = abs(
        state["hp_ratio_diff"]
    )

    # EARLY GAME
    if p1_hp_ratio > 0.90 and p2_hp_ratio > 0.90:
        return "NONE", 1.0

    # CLOSE MATCH
    if hp_ratio_diff < 0.075:
        return "NONE", 1.0

    # CRITICAL FINISH
    if p1_hp_ratio < 0.10 and p2_hp_ratio < 0.10:
        return "NONE", 1.0

    # =====================================================
    # RANDOM EXPLORATION
    # =====================================================

    if random.random() < epsilon:

        action = random.choice(ACTIONS)

    else:

        state_vector = torch.FloatTensor(
            [state_to_vector(state)]
        ).to(DEVICE)

        with torch.no_grad():

            q_values = model(state_vector)

            # best action
            action_idx = torch.argmax(
                q_values
            ).item()

            action = ACTIONS[action_idx]

    # =====================================================
    # ADAPTIVE BOOST VALUE
    # =====================================================

    value = adaptive_boost_value(
        state,
        action
    )

    return action, value

def compute_reward(state, next_state):

    reward = 0.0

    # =====================================================
    # 1. DAMAGE IMPACT
    # =====================================================

    p1_loss = (
        state["p1_hp_ratio"]
        - next_state["p1_hp_ratio"]
    )

    p2_loss = (
        state["p2_hp_ratio"]
        - next_state["p2_hp_ratio"]
    )

    net_damage = p2_loss - p1_loss

    # MUCH STRONGER
    reward += net_damage * 40.0

    # =====================================================
    # 2. COMEBACK PROGRESS
    # =====================================================

    prev_gap = abs(state["hp_ratio_diff"])
    next_gap = abs(next_state["hp_ratio_diff"])

    gap_change = prev_gap - next_gap

    # direct meaningful comeback
    reward += gap_change * 60.0

    # =====================================================
    # 3. SURVIVAL BONUS
    # =====================================================

    # disadvantaged player survives
    if state["hp_ratio_diff"] < 0:

        reward += (-p1_loss) * 15.0

    else:

        reward += (-p2_loss) * 15.0

    # =====================================================
    # 4. RESOURCE MOMENTUM
    # =====================================================

    p1_resource_gain = (
        (next_state["p1_gauge_ratio"]
         - state["p1_gauge_ratio"])

        +

        (next_state["p1_ultra_gauge_ratio"]
         - state["p1_ultra_gauge_ratio"])
    )

    p2_resource_gain = (
        (next_state["p2_gauge_ratio"]
         - state["p2_gauge_ratio"])

        +

        (next_state["p2_ultra_gauge_ratio"]
         - state["p2_ultra_gauge_ratio"])
    )

    if state["hp_ratio_diff"] < 0:

        reward += p1_resource_gain * 12.0

    else:

        reward += p2_resource_gain * 12.0

    # =====================================================
    # 5. SNOWBALL PENALTY
    # =====================================================

    # punish runaway advantage
    if next_gap > prev_gap:

        reward -= (
            (next_gap - prev_gap)
            * 35.0
        )

    # =====================================================
    # 6. EXTREME STATE PENALTY
    # =====================================================

    # too one-sided
    if next_gap > 0.70:

        reward -= 8.0

    # unrealistic HP jump
    if abs(p1_loss) > 0.45 or abs(p2_loss) > 0.45:

        reward -= 10.0

    # =====================================================
    # 7. TERMINAL REWARD
    # =====================================================

    if next_state.get("done", False):

        if next_state["p1_hp_ratio"] <= 0:

            reward -= 30.0

        elif next_state["p2_hp_ratio"] <= 0:

            reward += 30.0

    # =====================================================
    # NORMALIZATION
    # =====================================================

    reward = max(min(reward, 30.0), -30.0)

    reward /= 30.0

    return reward

def save_dataset(prev, action, action_value, reward, curr):

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

        "dataset_version": "v2",
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
        # timestamp
        # ---------------------------------------------

        "timestamp": time.time(),

        # ---------------------------------------------
        # gameplay context
        # ---------------------------------------------

        "action": action,

        "action_value": action_value,

        "reward": reward,

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

                reward = compute_reward(
                    prev_state,
                    state
                )

                save_dataset(
                    prev_state,
                    "NONE",
                    1.0,
                    reward,
                    state
                )

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

    # ================= ACTION =================
    if state.get("is_boost_active", False):

        write_action("NONE", 1.0)

        time.sleep(0.3)

        next_state = read_json(STATE_FILE)

        if next_state is None:
            continue

        if is_same_state(state, next_state):
            continue

        reward = compute_reward(state, next_state)

        save_dataset(
            state,
            "NONE",
            1.0,
            reward,
            next_state
        )

        prev_state = next_state

        print("👀 OBSERVING ACTIVE BOOST")

        continue
    
    action, value = model_policy(state)


    if action == "NONE":

        write_action("NONE", 1.0)

        time.sleep(0.5)

        next_state = read_json(STATE_FILE)

        if next_state is None:
            continue

        # skip stale transition
        if is_same_state(state, next_state):
            continue

        reward = compute_reward(
            state,
            next_state
        )

        save_dataset(
            state,
            "NONE",
            1.0,
            reward,
            next_state
        )

        print(f"📊 NONE | reward: {reward:.4f}")

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
    reward = compute_reward(state, next_state)
    save_dataset(state, action, value, reward, next_state)

    print(f"📊 {action} | reward: {reward:.4f}")

    # ================= UPDATE =================
    prev_state = state
