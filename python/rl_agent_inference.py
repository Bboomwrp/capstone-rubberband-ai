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


def is_real_fight(state):

    if not state.get("inMatch", False):
        return False

    if state.get("time", 1.0) >= 0.99:
        return False

    return True

# =========================================================
# INFERENCE
# =========================================================

def select_action(state, epsilon=0.05):

    # RANDOM EXPLORATION 

    if random.random() < epsilon:

        idx = random.randint(
            0,
            len(ACTIONS) - 1
        )

        action = ACTIONS[idx]

        print(f"🎲 RANDOM ACTION: {action}")

        return action

    # MODEL INFERENCE

    state_vec = state_to_vector(state)

    state_tensor = torch.FloatTensor(
        state_vec
    ).unsqueeze(0).to(DEVICE)

    with torch.no_grad():

        q_values = model(state_tensor)

        q_values = q_values.cpu().numpy()[0]

    action_idx = int(np.argmax(q_values))

    action = ACTIONS[action_idx]

    # DEBUG

    print(
        f"🧠 ACTION: {action} | "
        f"Q: {np.round(q_values, 3)}"
    )

    return action

def is_same_state(a, b):
    return abs(a["p1_hp_ratio"] - b["p1_hp_ratio"]) < 1e-3 and \
           abs(a["p2_hp_ratio"] - b["p2_hp_ratio"]) < 1e-3 and \
           abs(a["time"] - b["time"]) < 1e-3

def should_allow_boost(state):

    p1_hp_ratio = state["p1_hp_ratio"]
    p2_hp_ratio = state["p2_hp_ratio"]

    hp_ratio_diff = abs(state["hp_ratio_diff"])

    # =====================================================
    # EARLY GAME
    # =====================================================

    if p1_hp_ratio > 0.90 and p2_hp_ratio > 0.90:
        return False

    # =====================================================
    # CLOSE MATCH
    # =====================================================

    if hp_ratio_diff < 0.075:
        return False

    # =====================================================
    # LOW HP FINISH
    # =====================================================

    if p1_hp_ratio < 0.10 and p2_hp_ratio < 0.10:
        return False

    return True

# =========================================================
# ADAPTIVE VALUE
# =========================================================
def get_boost_value(action, state):

    hp_ratio_diff = abs(state["hp_ratio_diff"])

    # Intensity
    if hp_ratio_diff > 0.3:
        intensity = 1.30
    elif hp_ratio_diff > 0.2:
        intensity = 1.20
    elif hp_ratio_diff > 0.1:
        intensity = 1.10
    else:
        intensity = 1.05

    # ACTION TYPE ADJUSTMENT
    if action == "BOOST_ATTACK":
        return intensity
    elif action == "BOOST_DEFENSE":
        return min(intensity+0.05, 1.35)
    elif action == "BOOST_GAUGE":
        return min(intensity+0.1, 1.4)
    
    return 1.0

# =========================================================
# MAIN LOOP
# =========================================================

print("🚀 RL AGENT STARTED")

write_action("NONE", 1.0)

prev_state = None
startup_synced = False
episode_done = False

while True:

    state = read_json(STATE_FILE)

    if state is None:

        time.sleep(0.1)

        continue

    # =====================================================
    # TERMINAL DETECTION (HIGHEST PRIORITY)
    # =====================================================

    if state.get("done", False):

        print("🏁 TERMINAL")

        write_action("NONE", 1.0)

        prev_state = None
        startup_synced = False
        episode_done = True

        time.sleep(1.0)

        continue

    # =====================================================
    # RESET ACTION OUTSIDE MATCH
    # =====================================================

    if not state.get("inMatch", False):

        write_action("NONE", 1.0)

        prev_state = None

        time.sleep(0.1)

        continue

    # =====================================================
    # STARTUP SYNC
    # =====================================================

    if not startup_synced:

        # wait until gameplay actually begins
        if state.get("time", 1.0) > 0.995:

            time.sleep(0.05)

            continue

        startup_synced = True

        episode_done = False

        print("✅ STARTUP SYNCED")

        write_action("NONE", 1.0)

        prev_state = state

        continue

    # =====================================================
    # WAIT NEXT ROUND AFTER TERMINAL
    # =====================================================

    if episode_done:

        if (
            state.get("inMatch", False)
            and
            state.get("time", 1.0) < 0.95
        ):

            episode_done = False

        else:

            time.sleep(0.1)

            continue

    # =====================================================
    # PREVIEW / READY FILTER
    # =====================================================

    if state.get("time", 1.0) >= 0.99:

        time.sleep(0.1)

        continue

    # =====================================================
    # FULL HP OPENING FILTER
    # =====================================================

    if (
        abs(state["hp_ratio_diff"]) < 1e-5
        and
        state["p1_hp_ratio"] > 0.99
        and
        state["p2_hp_ratio"] > 0.99
    ):

        time.sleep(0.1)

        continue

    # =====================================================
    # DUPLICATE STATE FILTER
    # =====================================================

    if prev_state is not None:

        if is_same_state(state, prev_state):

            time.sleep(0.1)

            continue

    # =====================================================
    # OBSERVE ACTIVE BOOST
    # =====================================================

    if state.get("is_boost_active", False):

        print(
            f"👀 OBSERVING BOOST: "
            f"{state.get('current_action', 'NONE')}"
        )

        prev_state = state

        time.sleep(0.3)

        continue

    # =====================================================
    # BOOST CONSTRAINTS
    # =====================================================

    if not should_allow_boost(state):

        write_action("NONE", 1.0)

        prev_state = state

        time.sleep(0.3)

        continue

    # =====================================================
    # MODEL ACTION
    # =====================================================

    action = select_action(
        state,
        epsilon=0.05
    )

    # =====================================================
    # VALUE
    # =====================================================

    value = get_boost_value(
        action,
        state
    )

    # =====================================================
    # NO BOOST
    # =====================================================

    if action == "NONE":

        write_action("NONE", 1.0)

        prev_state = state

        time.sleep(0.3)

        continue

    # =====================================================
    # WRITE ACTION
    # =====================================================

    write_action(action, value)

    print(
        f"⚡ WRITE ACTION: "
        f"{action} x{value:.2f}"
    )

    # =====================================================
    # WAIT UNITY APPLY
    # =====================================================

    time.sleep(0.8)

    next_state = read_json(STATE_FILE)

    if next_state is None:

        continue

    # =====================================================
    # INVALID TRANSITION
    # =====================================================

    if is_same_state(state, next_state):

        print("⚠ SAME STATE TRANSITION")

        prev_state = state

        continue

    # =====================================================
    # ACTION VALIDATION
    # =====================================================

    if next_state.get("current_action", "NONE") != action:

        print("⚠ ACTION NOT APPLIED")

        prev_state = state

        continue

    # =====================================================
    # BOOST VALIDATION
    # =====================================================

    if not next_state.get("is_boost_active", False):

        print("⚠ BOOST NOT ACTIVE")

        prev_state = state

        continue

    # =====================================================
    # ROUND SAFETY
    # =====================================================

    if next_state.get("time", 1.0) >= 0.99:

        continue

    if next_state["time"] > state["time"]:

        continue

    # =====================================================
    # SUCCESS
    # =====================================================

    print(
        f"✅ BOOST APPLIED: "
        f"{action} x{value:.2f}"
    )

    prev_state = next_state
