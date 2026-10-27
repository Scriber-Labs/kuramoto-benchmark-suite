"""
config.py

Configuration handling for Kuramoto simulations via JSON.

Author: Eigenscribe
Date: May 2026
"""

from __future__ import annotations

import json
from typing import Any, Dict

import numpy as np

from kuramoto.utils import get_rng

# -----------------------------------------------------------------------------------------------------------
# 1️⃣ Core logic
# -----------------------------------------------------------------------------------------------------------


def parse_simulation_config(json_str: str) -> Dict[str, Any]:
    """
    Parse a JSON string containing Kuramoto simulation parameters.

    Expected format:
    {
        "n_oscillators": 10,
        "coupling_strength": 1.0,
        "topology": "ring",
        "timesteps": 1000,
        "dt": 0.05,
        "seed": 42,
        "frequency_distribution": {
            "type": "normal",
            "mean": 0.0,
            "std": 1.0
        },
        "adjacency_matrix": [[0,1], [1,0]] (optional)
    }

    Returns
    -------
    dict
        Validated parameters dictionary.
    """
    params = json.loads(json_str)

    # Default values
    config = {
        "n_oscillators": params.get("n_oscillators", 20),
        "coupling": float(params.get("coupling_strength", 1.0)),
        "timesteps": int(params.get("timesteps", 500)),
        "dt": float(params.get("dt", 0.05)),
        "seed": params.get("seed", None),
        "topology": params.get("topology", None),
        "adjacency": None,
    }

    if "solver" in params:
        config["solver"] = str(params["solver"]).lower()
    if "quantum_scheme" in params:
        config["scheme"] = str(params["quantum_scheme"]).lower()
    elif "scheme" in params:
        config["scheme"] = str(params["scheme"]).lower()
    if "shots" in params:
        config["shots"] = int(params["shots"])
    if "dt_internal" in params:
        config["dt_internal"] = float(params["dt_internal"])
    if "enforce_nyquist" in params:
        config["enforce_nyquist"] = bool(params["enforce_nyquist"])
    if "adaptive_rtol" in params:
        config["adaptive_rtol"] = float(params["adaptive_rtol"])
    if "adaptive_atol" in params:
        config["adaptive_atol"] = float(params["adaptive_atol"])

    if "adjacency_matrix" in params:
        config["adjacency"] = np.array(params["adjacency_matrix"], dtype=float)
        config["n_oscillators"] = config["adjacency"].shape[0]

    # Generate frequencies
    freq_cfg = params.get(
        "frequency_distribution", {"type": "normal", "mean": 0.0, "std": 1.0}
    )
    dist_type = freq_cfg.get("type", "normal")
    n = config["n_oscillators"]

    rng = get_rng(config["seed"])

    if dist_type == "normal":
        config["natural_frequencies"] = rng.normal(
            freq_cfg.get("mean", 0.0), freq_cfg.get("std", 1.0), n
        )
    elif dist_type == "uniform":
        config["natural_frequencies"] = rng.uniform(
            freq_cfg.get("low", -1.0), freq_cfg.get("high", 1.0), n
        )
    elif dist_type == "custom":
        config["natural_frequencies"] = np.array(freq_cfg.get("values"), dtype=float)
    else:
        config["natural_frequencies"] = rng.normal(0, 1, n)

    return config
