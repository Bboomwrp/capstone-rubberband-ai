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

    data = {
        "action": action,
        "value": value
    }

    try:
        with open(ACTION_FILE, "w") as f:
            json.dump(data, f)
    except:
        print("⚠ Cannot write action")


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

last_action = None
prev_state = None

while True:

    state = read_json(STATE_FILE)

    if state is None:
        time.sleep(0.1)
        continue

    # =====================================================
    # Round Reset
    # =====================================================

    if prev_state is not None:
        if state["time"] - prev_state["time"] > 0.5:
            print("🔄 NEW ROUND DETECTED")

            prev_state = None
            last_action = None
            continue

    # =====================================================
    # FILTER
    # =====================================================

    if not is_real_fight(state):
        time.sleep(0.1)
        continue

    if state.get("done", False):
        time.sleep(0.1)
        continue

    if abs(state["hp_ratio_diff"]) < 1e-5 and state["p1_hp_ratio"] > 0.99 and state["p2_hp_ratio"] > 0.99:
        time.sleep(0.1)
        continue

    # =====================================================
    # Terminal
    # =====================================================

    if state["p1_hp_ratio"] <= 0 or state["p2_hp_ratio"] <= 0:

        prev_state = None
        last_action = None

        time.sleep(0.5)
        continue

    # =====================================================
    # Duplicate State
    # =====================================================
    if prev_state is not None and is_same_state(state, prev_state):
        time.sleep(0.1)
        continue
 
    # =====================================================
    # ACTION
    # =====================================================

    if not should_allow_boost(state):

        write_action("NONE", 1.0)

        prev_state = state

        time.sleep(0.5)

        continue

    action = select_action(
        state,
        epsilon=0.05
    )

    # =====================================================
    # ACTION VALUE
    # =====================================================

    value = get_boost_value(action, state)

    # =====================================================
    # ANTI-SPAM
    # =====================================================

    if action == last_action:

        time.sleep(1.0)
        continue

    # =====================================================
    # WRITE
    # =====================================================

    write_action(action, value)

    print(f"⚡ WRITE ACTION: {action} x{value:.2f}")

    time.sleep(1)

    # Update last action and state
    
    last_action = action
    prev_state = state

    # =====================================================
    # LOOP DELAY
    # =====================================================

    # time.sleep(2.0)