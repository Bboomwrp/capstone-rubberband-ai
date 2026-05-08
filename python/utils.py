def state_to_vector(state):

    return [
        state["hp_diff"],
        state["hp_ratio"],
        state["p1_gauge"] / 1000.0,
        state["p2_gauge"] / 1000.0,
        state["distance"] / 20.0,
        state["time"]
    ]