# Adaptive Rubberband AI for Fighting Games using Reinforcement Learning

## Overview

This project presents a real-time adaptive rubberband balancing system for fighting games using Reinforcement Learning (RL).

The system dynamically adjusts gameplay parameters such as attack power, defense, and gauge gain based on the current match state to improve gameplay balance and create more engaging matches.

Developed as part of the CEDT Capstone Project.

---

## Features

- Real-time gameplay state extraction from Unity
- Reinforcement Learning-based balancing system
- Dynamic stat adjustment:
  - BOOST_ATTACK
  - BOOST_DEFENSE
  - BOOST_GAUGE
- DQN (Deep Q-Network) training pipeline
- Unity ↔ Python integration
- Adaptive rubberband balancing system

---

## System Architecture

```text
Unity Game
   ↓
RLStateExporter
   ↓
JSON State
   ↓
Python RL Agent
   ↓
DQN Model
   ↓
Action Decision
   ↓
RLActionReceiver
   ↓
Dynamic Gameplay Adjustment
```

---

## Technologies Used

| Category | Technology |
|---|---|
| Game Engine | Unity |
| Fighting Framework | UFE |
| Language | C#, Python |
| ML Framework | PyTorch |
| RL Algorithm | DQN |
| Communication | JSON File IPC |

---

## Project Structure

```text
unity/      → Unity project
python/     → RL training & inference
docs/       → Poster, diagrams, screenshots
demo/       → Gameplay videos
```

---

## Setup

### Python Environment

```bash
conda create -n rl python=3.10
conda activate rl

pip install torch torchvision numpy
```

---

## Training

```bash
python train_dqn.py
```

---

## Run Inference Agent

```bash
python rl_agent_inference.py
```

---

## Dataset Pipeline

```text
Gameplay
→ State Export
→ Dataset Collection
→ Dataset Cleaning
→ Reward Normalization
→ DQN Training
```

---

## Results

- Real-time adaptive balancing
- Stable RL inference
- Dynamic comeback generation
- Reduced gameplay imbalance

---

## Future Work

- PPO / Advanced RL algorithms
- Online learning
- Multi-character balancing
- Neural gameplay style adaptation
- Multiplayer balancing

---

## Authors

- "Weeraphat Plengudomkij"

CEDT Capstone Project  
Chulalongkorn University

---

## Academic Use

This project was developed as part of the CEDT Capstone Project for educational and research purposes.