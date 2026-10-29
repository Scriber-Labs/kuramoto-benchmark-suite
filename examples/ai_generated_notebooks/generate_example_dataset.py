# examples/generate_example_dataset.py
"""
Example script for generating a Kuramoto dataset.

This script demonstrates the standard workflow for generating benchmark datasets using the Kuramoto API.
It configures a population of oscillators, simulates their dynamics, and saves the output to a compressed NumPy file.

Author: Eigenscribe
Date: May 2026
"""

from __future__ import annotations

# --------------------------------------------------------------------------- #
# Imports
# --------------------------------------------------------------------------- #

import os
from typing import Final
import numpy as np

from kuramoto.api import generate_kuramoto_dataset

# ------------------------------------------------------------------------------ #
# 1️⃣ Constants & Configuration
# ------------------------------------------------------------------------------ #

N: Final[int] = 50
T: Final[int] = 1000
DT: Final[float] = 0.01
COUPLING: Final[float] = 5.0
SEED: Final[int] = 27
OUTPUT_PATH: Final[str] = "data/examples/small_demo.npz"

# ------------------------------------------------------------------------------ #
# 2️⃣ Generation Logic
# ------------------------------------------------------------------------------ #

def run_dataset_generation() -> None:
    """
    Generate a Kuramoto dataset and save it to disk.

    Steps:
    1. Sample natural frequencies from a normal distribution.
    2. Invoke the Kuramoto API to perform the simulation.
    3. Ensure output directory existence.
    4. Save the resulting dataset dictionary as an .npz file.
    """
    print(f"🚀 Initializing Kuramoto dataset generation (N={N}, T={T})...")

    # Sample natural frequencies (omega)
    # Note: We use the local random state for reproducibility
    rng = np.random.default_rng(SEED)
    omega = rng.normal(0.0, 1.0, size=N)

    # Generate the dataset using the public API
    data = generate_kuramoto_dataset(
        n_oscillators=N,
        natural_frequencies=omega,
        coupling=COUPLING,
        timesteps=T,
        dt=DT,
        seed=SEED,
    )

    # Ensure the target directory exists
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    # Save the dataset to disk
    np.savez(OUTPUT_PATH, **data)

    print(f"✅ Success: Dataset saved to '{OUTPUT_PATH}'")

# ------------------------------------------------------------------------------ #
# 3️⃣ Entry Point
# ------------------------------------------------------------------------------ #

def main() -> None:
    """
    Main entry point for the example script.
    """
    run_dataset_generation()

if __name__ == "__main__":
    main()
