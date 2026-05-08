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

model = DQN(6, len(ACTIONS)).to(DEVICE)

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

    # =====================================================
    # RANDOM EXPLORATION
    # =====================================================

    if random.random() < epsilon:

        idx = random.randint(
            0,
            len(ACTIONS) - 1
        )

        action = ACTIONS[idx]

        print(f"🎲 RANDOM ACTION: {action}")

        return action

    # =====================================================
    # MODEL INFERENCE
    # =====================================================

    state_vec = state_to_vector(state)

    state_tensor = torch.FloatTensor(
        state_vec
    ).unsqueeze(0).to(DEVICE)

    with torch.no_grad():

        q_values = model(state_tensor)

        q_values = q_values.cpu().numpy()[0]

    action_idx = int(np.argmax(q_values))

    action = ACTIONS[action_idx]

    # =====================================================
    # DEBUG
    # =====================================================

    print(
        f"🧠 ACTION: {action} | "
        f"Q: {np.round(q_values, 3)}"
    )

    return action

# =========================================================
# MAIN LOOP
# =========================================================

print("🚀 RL AGENT STARTED")

last_action = None

while True:

    state = read_json(STATE_FILE)

    if state is None:
        time.sleep(0.1)
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

    # =====================================================
    # ACTION
    # =====================================================

    action = select_action(
        state,
        epsilon=0.05
    )

    # =====================================================
    # ACTION VALUE
    # =====================================================

    value = 1.0

    if action == "BOOST_ATTACK":
        value = 1.2

    elif action == "BOOST_DEFENSE":
        value = 1.15

    elif action == "BOOST_GAUGE":
        value = 1.25

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

    print(f"⚡ WRITE ACTION: {action}")

    last_action = action

    # =====================================================
    # LOOP DELAY
    # =====================================================

    time.sleep(2.0)