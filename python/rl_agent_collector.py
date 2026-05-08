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
DATASET_FILE = os.path.join(DATASET_DIR, "dataset.jsonl")

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
    with open(ACTION_FILE, "w") as f:
        json.dump(data, f)

def policy(state, epsilon=0.3):
    actions = ["NONE", "BOOST_ATTACK", "BOOST_DEFENSE", "BOOST_GAUGE"]

    # random exploration
    if random.random() < epsilon:
        return random.choice(actions), 1.0

    hp_diff = abs(state["hp_diff"])
    gauge_diff = state["p1_gauge"] - state["p2_gauge"]

    # heuristic
    if hp_diff > 0.2:
        return "BOOST_ATTACK", 1.2
    elif hp_diff > 0.1:
        return "BOOST_DEFENSE", 1.1
    elif gauge_diff < -200:
        return "BOOST_GAUGE", 1.2
    else:
        return "NONE", 1.0

def compute_reward(state, next_state):
    reward = 0.0

    # =========================
    # 1. DAMAGE (หลัก)
    # =========================
    p1_loss = state["p1_hp"] - next_state["p1_hp"]
    p2_loss = state["p2_hp"] - next_state["p2_hp"]

    net_damage = p2_loss - p1_loss
    reward += net_damage * 1.0

    # =========================
    # 2. COMEBACK (rubberband)
    # =========================
    prev_diff = abs(state["hp_diff"])
    next_diff = abs(next_state["hp_diff"])

    # ถ้าความห่างลดลง = เกมสูสีขึ้น → ดี
    if next_diff < prev_diff:
        reward += (prev_diff - next_diff) * 50.0

    # =========================
    # 3. SURVIVAL (กันตายโง่)
    # =========================
    if state["hp_diff"] < 0:
        # p1 เสียเปรียบ → โดนตีแรง = โดนลงโทษ
        reward -= p1_loss * 0.5
    else:
        # p2 เสียเปรียบ → โดนตีแรง = ดี
        reward += p2_loss * 0.3

    # =========================
    # 4. GAUGE (resource)
    # =========================
    p1_gain = next_state["p1_gauge"] - state["p1_gauge"]
    p2_gain = next_state["p2_gauge"] - state["p2_gauge"]

    # rubberband-aware
    if state["hp_diff"] < 0:
        reward += p1_gain * 0.1
    else:
        reward += p2_gain * 0.1

    # =========================
    # 5. STABILITY (กันมั่ว)
    # =========================
    # ถ้า HP เปลี่ยนเยอะผิดปกติ → penalty
    if abs(p1_loss) > 200 or abs(p2_loss) > 200:
        reward -= 10.0

    # =========================
    # 6. TERMINAL (จบ round)
    # =========================
    if next_state.get("done", False):
        if next_state["p1_hp"] <= 0:
            reward -= 100.0
        elif next_state["p2_hp"] <= 0:
            reward += 100.0

    reward = reward / 100.0
    reward = max(min(reward, 1.0), -1.0)

    return reward

def save_dataset(prev, action, reward, curr):
    data = {
        "state": prev,
        "action": action,
        "reward": reward,
        "next_state": curr
    }

    with open(DATASET_FILE, "a") as f:
        f.write(json.dumps(data) + "\n")

def is_real_fight(state):
    return state["time"] < 0.99

def is_terminal(prev, curr):
    if prev is None or curr is None:
        return False

    p1_dead = prev["p1_hp"] > 0 and curr["p1_hp"] <= 0
    p2_dead = prev["p2_hp"] > 0 and curr["p2_hp"] <= 0

    return p1_dead or p2_dead

def make_signature(prev, curr):
    return (
        round(prev["p1_hp"], 3),
        round(prev["p2_hp"], 3),
        round(curr["p1_hp"], 3),
        round(curr["p2_hp"], 3)
    )

def is_same_state(a, b):
    return abs(a["p1_hp"] - b["p1_hp"]) < 1e-3 and \
           abs(a["p2_hp"] - b["p2_hp"]) < 1e-3 and \
           abs(a["time"] - b["time"]) < 1e-3

# ================= LOOP =================

print("🤖 RL Agent started")

prev_state = None
last_done = False
episode_done = False
last_terminal_signature = None

while True:
    state = read_json(STATE_FILE)

    if state is None:
        time.sleep(0.1)
        continue

    # ================= ROUND RESET =================
    if prev_state is not None:
        if state["time"] - prev_state["time"] > 0.5:
            print("🔄 NEW ROUND DETECTED")

            episode_done = False
            prev_state = None
            last_terminal_signature = None
            continue

    # ================= FORCE UNSTUCK =================
    if episode_done and prev_state is None:
        if state.get("time", 1.0) < 0.95:
            episode_done = False

    # ================= BLOCK AFTER DONE =================
    if episode_done:
        time.sleep(0.1)
        continue

    # ================= FILTER PREVIEW =================
    if state.get("time", 1.0) >= 0.99:
        continue

    # skip full HP (ยังไม่เริ่มสู้)
    if abs(state["hp_diff"]) < 1e-5 and state["hp_ratio"] > 0.99:
        continue

    if not is_real_fight(state):
        continue

    # ================= TERMINAL FLAG =================
    if state["p1_hp"] <= 0 or state["p2_hp"] <= 0:
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

    # ================= TERMINAL DETECTION =================
    if prev_state is not None:
        if is_terminal(prev_state, state):

            sig = make_signature(prev_state, state)

            # ❗ กัน terminal ซ้ำ
            if sig == last_terminal_signature:
                continue

            last_terminal_signature = sig

            state["done"] = True

            reward = compute_reward(prev_state, state)
            save_dataset(prev_state, "NONE", reward, state)

            print("🏁 TERMINAL SAVED")

            episode_done = True
            prev_state = None
            continue

    # ================= BLOCK NORMAL FLOW IF DONE =================
    if state.get("done", False):
        prev_state = None
        continue

    # ================= ACTION =================
    action, value = policy(state)
    write_action(action, value)

    time.sleep(1)

    next_state = read_json(STATE_FILE)
    if next_state is None:
        continue

    # ================= VALIDATE NEXT STATE =================
    if next_state.get("time", 1.0) >= 0.99:
        continue

    # ❗ กันข้าม round
    if next_state["time"] > state["time"]:
        continue

    # mark done
    if next_state["p1_hp"] <= 0 or next_state["p2_hp"] <= 0:
        next_state["done"] = True

    # ❗ กัน terminal ซ้ำใน normal flow
    if next_state.get("done", False):
        continue

    # ================= SAVE NORMAL =================
    reward = compute_reward(state, next_state)
    save_dataset(state, action, reward, next_state)

    print(f"📊 {action} | reward: {reward:.4f}")

    # ================= UPDATE =================
    prev_state = state