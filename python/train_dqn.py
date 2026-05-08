# train_dqn.py

import os
import json
import random
from collections import deque

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from dqn_model import DQN
from utils import state_to_vector

# =========================================================
# CONFIG
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_FILE = os.path.join(
    BASE_DIR,
    "dataset",
    "dataset_final.jsonl"
)

MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH = os.path.join(MODEL_DIR, "dqn_model.pth")

ACTIONS = [
    "NONE",
    "BOOST_ATTACK",
    "BOOST_DEFENSE",
    "BOOST_GAUGE"
]

STATE_DIM = 6
ACTION_DIM = len(ACTIONS)

BATCH_SIZE = 128
GAMMA = 0.99

LEARNING_RATE = 1e-4

EPOCHS = 30

TARGET_UPDATE = 3

MAX_MEMORY = 100000

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print(f"🔥 DEVICE: {DEVICE}")

# =========================================================
# REPLAY BUFFER
# =========================================================

memory = deque(maxlen=MAX_MEMORY)

# =========================================================
# LOAD DATASET
# =========================================================

print("📂 Loading dataset...")

count = 0

with open(DATASET_FILE, "r", encoding="utf-8") as f:
    for line in f:
        try:
            data = json.loads(line)

            state = state_to_vector(data["state"])
            next_state = state_to_vector(data["next_state"])

            action = ACTIONS.index(data["action"])
            reward = float(data["reward"])

            done = bool(
                data["next_state"].get("done", False)
            )

            memory.append(
                (
                    state,
                    action,
                    reward,
                    next_state,
                    done
                )
            )

            count += 1

        except Exception as e:
            print("⚠ Skip bad sample:", e)

print(f"✅ Loaded {count} transitions")

# =========================================================
# MODEL
# =========================================================

policy_net = DQN(
    STATE_DIM,
    ACTION_DIM
).to(DEVICE)

target_net = DQN(
    STATE_DIM,
    ACTION_DIM
).to(DEVICE)

target_net.load_state_dict(
    policy_net.state_dict()
)

target_net.eval()

optimizer = optim.Adam(
    policy_net.parameters(),
    lr=LEARNING_RATE
)

criterion = nn.MSELoss()

# =========================================================
# TRAINING
# =========================================================

print("🚀 TRAIN START")

for epoch in range(EPOCHS):

    policy_net.train()

    losses = []

    random.shuffle(memory)

    num_batches = len(memory) // BATCH_SIZE

    for batch_idx in range(num_batches):

        batch = random.sample(
            memory,
            BATCH_SIZE
        )

        states = np.array([x[0] for x in batch])
        actions = np.array([x[1] for x in batch])
        rewards = np.array([x[2] for x in batch])
        next_states = np.array([x[3] for x in batch])
        dones = np.array([x[4] for x in batch])

        states = torch.FloatTensor(
            states
        ).to(DEVICE)

        actions = torch.LongTensor(
            actions
        ).to(DEVICE)

        rewards = torch.FloatTensor(
            rewards
        ).to(DEVICE)

        next_states = torch.FloatTensor(
            next_states
        ).to(DEVICE)

        dones = torch.FloatTensor(
            dones
        ).to(DEVICE)

        # =================================================
        # CURRENT Q
        # =================================================

        current_q = policy_net(states)

        current_q = current_q.gather(
            1,
            actions.unsqueeze(1)
        ).squeeze(1)

        # =================================================
        # TARGET Q
        # =================================================

        with torch.no_grad():

            next_q = target_net(next_states)

            max_next_q = next_q.max(1)[0]

            target_q = rewards + (
                GAMMA
                * max_next_q
                * (1 - dones)
            )

        # =================================================
        # LOSS
        # =================================================

        loss = criterion(
            current_q,
            target_q
        )

        optimizer.zero_grad()

        loss.backward()

        # gradient clipping
        torch.nn.utils.clip_grad_norm_(
            policy_net.parameters(),
            10
        )

        optimizer.step()

        losses.append(loss.item())

    # =====================================================
    # TARGET UPDATE
    # =====================================================

    if epoch % TARGET_UPDATE == 0:
        target_net.load_state_dict(
            policy_net.state_dict()
        )

    # =====================================================
    # LOG
    # =====================================================

    avg_loss = np.mean(losses)

    print(
        f"Epoch {epoch+1}/{EPOCHS} "
        f"| Loss: {avg_loss:.6f}"
    )

# =========================================================
# SAVE MODEL
# =========================================================

torch.save(
    policy_net.state_dict(),
    MODEL_PATH
)

print(f"✅ MODEL SAVED: {MODEL_PATH}")