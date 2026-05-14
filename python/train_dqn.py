import os
import json
import random
from collections import deque, Counter

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from dqn_model import DQN
from utils import state_to_vector

# =========================================================
# RANDOM SEED
# =========================================================

SEED = 42

random.seed(SEED)

np.random.seed(SEED)

torch.manual_seed(SEED)

if torch.cuda.is_available():

    torch.cuda.manual_seed(SEED)
    torch.cuda.manual_seed_all(SEED)

# =========================================================
# CONFIG
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_FILE = os.path.join(
    BASE_DIR,
    "dataset",
    "dataset_v3_rewarded.jsonl"
)

MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "dqn_model_v3_logged.pth"
)

ACTIONS = [
    "NONE",
    "BOOST_ATTACK",
    "BOOST_DEFENSE",
    "BOOST_GAUGE"
]

STATE_DIM = 15
ACTION_DIM = len(ACTIONS)

BATCH_SIZE = 128

# faster reaction balancing
GAMMA = 0.95

LEARNING_RATE = 1e-4

# more epochs after downsampling
EPOCHS = 25

TARGET_UPDATE = 3

MAX_MEMORY = 100000

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

print(f"🔥 DEVICE: {DEVICE}")

# =========================================================
# ACTION WEIGHTS
# =========================================================

ACTION_WEIGHTS = torch.FloatTensor([
    0.50,   # NONE
    1.25,   # BOOST_ATTACK
    1.10,   # BOOST_DEFENSE
    0.75    # BOOST_GAUGE
]).to(DEVICE)

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

            # =================================================
            # DOWNSAMPLE NONE ACTION
            # =================================================

            if data["action"] == "NONE":

                # keep only 25%
                if random.random() > 0.60:
                    continue

            state = state_to_vector(
                data["state"]
            )

            next_state = state_to_vector(
                data["next_state"]
            )

            action = ACTIONS.index(
                data["action"]
            )

            reward = float(
                data["reward"]
            )

            done = bool(
                data["next_state"].get(
                    "done",
                    False
                )
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

            print(
                "⚠ Skip bad sample:",
                e
            )

print(f"✅ Loaded {count} transitions")

# =========================================================
# TRAIN / VALIDATION SPLIT
# =========================================================

memory = list(memory)

random.shuffle(memory)

split_idx = int(
    len(memory) * 0.90
)

train_memory = memory[:split_idx]

val_memory = memory[split_idx:]

print(
    f"\n📚 TRAIN SAMPLES: "
    f"{len(train_memory)}"
)

print(
    f"🧪 VAL SAMPLES  : "
    f"{len(val_memory)}"
)

# =========================================================
# ACTION DISTRIBUTION
# =========================================================

counter = Counter()

for item in train_memory:

    action_idx = item[1]

    counter[
        ACTIONS[action_idx]
    ] += 1

print("\n===== TRAIN DISTRIBUTION =====")

for k, v in counter.items():

    print(f"{k}: {v}")

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

# =========================================================
# TRAINING
# =========================================================

print("🚀 TRAIN START")

# =========================================================
# LOSS HISTORY
# =========================================================

train_loss_history = []
val_loss_history = []

for epoch in range(EPOCHS):

    policy_net.train()

    losses = []

    num_batches = (
        len(train_memory)
        // BATCH_SIZE
    )

    for batch_idx in range(num_batches):

        batch = random.sample(
            train_memory,
            BATCH_SIZE
        )

        states = np.array(
            [x[0] for x in batch]
        )

        actions = np.array(
            [x[1] for x in batch]
        )

        rewards = np.array(
            [x[2] for x in batch]
        )

        next_states = np.array(
            [x[3] for x in batch]
        )

        dones = np.array(
            [x[4] for x in batch]
        )

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

        current_q = policy_net(
            states
        )

        current_q = current_q.gather(
            1,
            actions.unsqueeze(1)
        ).squeeze(1)

        # =================================================
        # TARGET Q
        # =================================================

        with torch.no_grad():

            next_q = target_net(
                next_states
            )

            max_next_q = next_q.max(1)[0]

            target_q = rewards + (
                GAMMA
                * max_next_q
                * (1 - dones)
            )

        # =================================================
        # WEIGHTED LOSS
        # =================================================

        sample_weights = ACTION_WEIGHTS[
            actions
        ]

        loss = torch.nn.functional.smooth_l1_loss(
            current_q,
            target_q,
            reduction="none"
        )

        loss = (
            loss
            * sample_weights
        ).mean()

        optimizer.zero_grad()

        loss.backward()

        # gradient clipping
        torch.nn.utils.clip_grad_norm_(
            policy_net.parameters(),
            10
        )

        optimizer.step()

        losses.append(
            loss.item()
        )

    # =====================================================
    # TARGET UPDATE
    # =====================================================

    if epoch % TARGET_UPDATE == 0:

        target_net.load_state_dict(
            policy_net.state_dict()
        )

    # =====================================================
    # VALIDATION
    # =====================================================

    policy_net.eval()

    val_losses = []

    with torch.no_grad():

        val_batches = max(
            1,
            len(val_memory) // BATCH_SIZE
        )

        for _ in range(val_batches):

            batch = random.sample(
                val_memory,
                BATCH_SIZE
            )

            states = np.array(
                [x[0] for x in batch]
            )

            actions = np.array(
                [x[1] for x in batch]
            )

            rewards = np.array(
                [x[2] for x in batch]
            )

            next_states = np.array(
                [x[3] for x in batch]
            )

            dones = np.array(
                [x[4] for x in batch]
            )

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

            current_q = policy_net(
                states
            )

            current_q = current_q.gather(
                1,
                actions.unsqueeze(1)
            ).squeeze(1)

            next_q = target_net(
                next_states
            )

            max_next_q = next_q.max(1)[0]

            target_q = rewards + (
                GAMMA
                * max_next_q
                * (1 - dones)
            )

            sample_weights = ACTION_WEIGHTS[
                actions
            ]

            val_loss = torch.nn.functional.smooth_l1_loss(
                current_q,
                target_q,
                reduction="none"
            )

            val_loss = (
                val_loss
                * sample_weights
            ).mean()

            val_losses.append(
                val_loss.item()
            )

    avg_val_loss = np.mean(
        val_losses
    )

    # =====================================================
    # LOG
    # =====================================================

    avg_train_loss = np.mean(losses)

    train_loss_history.append(
        float(avg_train_loss)
    )

    val_loss_history.append(
        float(avg_val_loss)
    )

    print(
        f"Epoch {epoch+1}/{EPOCHS}"
        f" | Train Loss: "
        f"{avg_train_loss:.6f}"
        f" | Val Loss: "
        f"{avg_val_loss:.6f}"
    )

# =========================================================
# SAVE LOSS HISTORY
# =========================================================

LOSS_HISTORY_PATH = os.path.join(
    MODEL_DIR,
    "loss_history.json"
)

with open(
    LOSS_HISTORY_PATH,
    "w"
) as f:

    json.dump(

        {
            "train_loss":
                train_loss_history,

            "val_loss":
                val_loss_history
        },

        f,
        indent=4
    )

print(
    f"\n✅ LOSS HISTORY SAVED: "
    f"{LOSS_HISTORY_PATH}"
)

# =========================================================
# SAVE MODEL
# =========================================================

torch.save({

    "model_state_dict":
        policy_net.state_dict(),

    "state_dim":
        STATE_DIM,

    "actions":
        ACTIONS,

}, MODEL_PATH)

print(f"\n✅ MODEL SAVED: {MODEL_PATH}")
