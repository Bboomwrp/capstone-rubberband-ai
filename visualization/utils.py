import os
import json

from collections import defaultdict

# =====================================================
# PROJECT ROOT
# =====================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PROJECT_ROOT = os.path.dirname(BASE_DIR)

DATASET_DIR = os.path.join(
    PROJECT_ROOT,
    "python",
    "dataset"
)

# =====================================================
# LOAD DATASET
# =====================================================

def load_dataset(filename):

    path = os.path.join(
        DATASET_DIR,
        filename
    )

    print(f"📂 Loading dataset: {path}")

    data = []

    with open(path, "r", encoding="utf-8") as f:

        for line in f:

            try:

                sample = json.loads(line)

                data.append(sample)

            except:

                continue

    print(f"✅ Loaded samples: {len(data)}")

    return data

# =====================================================
# GROUP BY ROUND
# =====================================================

def group_by_round(data):

    rounds = defaultdict(list)

    for sample in data:

        round_id = sample["round_id"]

        rounds[round_id].append(sample)

    return rounds

# =====================================================
# GET MATCHUP
# =====================================================

def get_matchup(sample):

    return sample.get(
        "matchup",
        "unknown"
    ).lower()
