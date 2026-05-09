def state_to_vector(state):

    return [
        state["p1_hp_ratio"],
        state["p2_hp_ratio"],

        state["hp_ratio_diff"],

        state["p1_gauge_ratio"],
        state["p2_gauge_ratio"],

        state["p1_ultra_ratio"],
        state["p2_ultra_ratio"],

        state["distance"],
        state["time"]
    ]