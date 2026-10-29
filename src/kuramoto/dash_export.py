# src/kuramoto/dash_export.py
"""
Enriched export utilities for the Kuramoto Dash App integration.

Extends the basic export pipeline with additional synchronization metrics:
  - Mean field phase ψ(t), the argument of the complex mean phasor.
  - Frequency locking fraction, the proportion of phase-locked oscillators per timestep.
  - Solver and network topology metadata for dashboard context.

Author: Eigenscribe & Junie
Date: 10-2026
"""

from __future__ import annotations

import json
from collections import namedtuple
from typing import Any, Callable, Dict, Optional

import numpy as np
import pandas as pd
from numpy.typing import NDArray

# Import RNG utilities from the central utils module
try:
    from .utils import get_rng
except (ImportError, ValueError):
    import sys
    from pathlib import Path

    _src_dir = str(Path(__file__).resolve().parent.parent)
    if _src_dir not in sys.path:
        sys.path.insert(0, _src_dir)

    from kuramoto.utils import get_rng

__all__: list[str] = [
    "TimestepRecord",
    "compute_mean_field_phase",
    "compute_locking_fraction",
    "export_for_dash",
    "export_for_dash_stream",
]

# ------------------------------------------------------------------------------
# 🎭 Type Aliases
# ------------------------------------------------------------------------------

PhaseArray = NDArray[np.floating]
TimeArray = NDArray[np.floating]

# TimestepRecord for streaming export — one record per output timestep
TimestepRecord = namedtuple(
    "TimestepRecord",
    ["time", "theta", "order_parameter", "mean_field_phase", "locking_fraction"],
)

# Callback type: invoked after each output timestep with the current time, phases, and record
TimestepCallback = Callable[[float, PhaseArray, "TimestepRecord"], None]

# ------------------------------------------------------------------------------
# 1️⃣ Public API — Metric Computation
# ------------------------------------------------------------------------------


def compute_mean_field_phase(theta: PhaseArray) -> TimeArray:
    """
    Compute the mean field phase ψ(t) from phase trajectories.

    The mean field phase is the argument of the complex mean phasor:

        ψ(t) = arg( 1/N * Σ_j exp(i * θ_j(t)) )

    It complements the order parameter magnitude R(t) by providing the
    collective phase angle of the oscillator population.

    Parameters
    ----------
    theta : PhaseArray
        Phase trajectories of shape (T, N), where T is the number of
        timesteps and N is the number of oscillators.

    Returns
    -------
    TimeArray
        Mean field phase ψ(t), shape (T,). Values are in [-π, π].

    Examples
    --------
    >>> import numpy as np
    >>> theta = np.array([[0.0, 0.1, 0.05], [0.5, 0.6, 0.55]])
    >>> psi = compute_mean_field_phase(theta)
    >>> psi.shape
    (2,)
    """
    if theta.ndim != 2:
        raise ValueError(f"Expected theta to be 2D (T, N), got {theta.ndim}D")

    mean_phasor = np.mean(np.exp(1j * theta), axis=1)
    psi = np.angle(mean_phasor)

    return psi


def compute_locking_fraction(
    theta: PhaseArray,
    time: TimeArray,
    threshold: float = 0.1,
    window: int = 10,
) -> TimeArray:
    """
    Compute the fraction of frequency-locked oscillators per timestep.

    An oscillator is considered "locked" if its instantaneous frequency
    deviation from the mean frequency stays below a threshold over a
    sliding window. The instantaneous frequency is estimated via

        ω_i(t) ≈ dθ_i / dt

    using ``np.gradient``.

    Parameters
    ----------
    theta : PhaseArray
        Phase trajectories of shape (T, N).
    time : TimeArray
        Time array of shape (T,).
    threshold : float, default 0.1
        Maximum frequency deviation (rad/s) from the mean frequency for an
        oscillator to be considered locked.
    window : int, default 10
        Sliding window size (in timesteps) for computing the rolling lock
        status. An oscillator is locked at time t if it has been within
        the threshold for at least ``window`` consecutive timesteps ending at t.

    Returns
    -------
    TimeArray
        Locking fraction at each timestep, shape (T,). Values are in [0, 1].

    Notes
    -----
    For a single oscillator (N=1), the locking fraction is trivially 1.0
    at all timesteps, as the oscillator is always "locked" to itself.
    """
    if theta.ndim != 2:
        raise ValueError(f"Expected theta to be 2D (T, N), got {theta.ndim}D")
    if time.ndim != 1:
        raise ValueError(f"Expected time to be 1D, got {time.ndim}D")

    T, N = theta.shape

    # Trivial case: single oscillator is always locked
    if N == 1:
        return np.ones(T)

    # Instantaneous frequencies: ω_i(t) ≈ dθ_i/dt, shape (T, N)
    instantaneous_freq = np.gradient(theta, time, axis=0)

    # Mean frequency at each timestep, shape (T,)
    mean_freq = np.mean(instantaneous_freq, axis=1)

    # Deviation from mean frequency, shape (T, N)
    freq_deviation = np.abs(instantaneous_freq - mean_freq[:, np.newaxis])

    # Binary lock status: 1 if within threshold, 0 otherwise
    locked = (freq_deviation <= threshold).astype(np.float64)

    # Sliding window: an oscillator is locked at time t if it has been
    # locked for at least `window` consecutive timesteps ending at t
    locking_fraction = np.zeros(T)
    for t in range(T):
        start = max(0, t - window + 1)
        window_locked = locked[start : t + 1, :]
        # An oscillator is locked if it was locked in all steps of the window
        consistently_locked = np.all(window_locked, axis=0)
        locking_fraction[t] = np.mean(consistently_locked)

    return locking_fraction


# ------------------------------------------------------------------------------
# 2️⃣ Public API — Export Function
# ------------------------------------------------------------------------------


def export_for_dash(
    dataset: Dict[str, Any],
    output_path: str,
    include_locking: bool = True,
    locking_threshold: float = 0.1,
    locking_window: int = 10,
    **kwargs: Any,
) -> None:
    """
    Export a Kuramoto dataset as enriched JSON for the Dash App.

    Takes a dictionary produced by ``generate_kuramoto_dataset()`` and writes
    a JSON file with the structure:

    .. code-block:: json

        {
          "metadata": { ... },
          "data": { ... }
        }

    The ``data`` field uses ``orient='split'`` (backward compatible with the
    existing Dash app). New fields include ``mean_field_phase`` (ψ(t)) and
    ``locking_fraction`` (fraction of phase-locked oscillators per timestep).

    Parameters
    ----------
    dataset : Dict[str, Any]
        Dataset dictionary from ``generate_kuramoto_dataset()``. Expected keys:
        ``theta``, ``time``, ``omega``, ``adjacency``, ``coupling``,
        ``noise_std``, ``solver``, etc.
    output_path : str
        Path for the output JSON file.
    include_locking : bool, default True
        Whether to compute and include the locking fraction metric.
    locking_threshold : float, default 0.1
        Frequency deviation threshold for locking detection (rad/s).
    locking_window : int, default 10
        Sliding window size for locking detection (timesteps).
    **kwargs : Any
        Additional keyword arguments (reserved for future extensions).

    Examples
    --------
    >>> from kuramoto.api import generate_kuramoto_dataset
    >>> import numpy as np
    >>> data = generate_kuramoto_dataset(
    ...     n_oscillators=10,
    ...     natural_frequencies=np.ones(10),
    ...     coupling=1.5,
    ...     timesteps=100,
    ...     dt=0.02,
    ...     seed=42,
    ... )
    >>> export_for_dash(data, "output.json")  # doctest: +SKIP
    """
    theta = dataset["theta"]
    time = dataset["time"]
    T, N = theta.shape

    # Compute order parameter R(t)
    from .order_parameter import compute_order_parameter

    R = compute_order_parameter(theta)

    # Compute mean field phase ψ(t)
    psi = compute_mean_field_phase(theta)

    # Compute locking fraction if requested
    locking = np.zeros(T)
    if include_locking:
        locking = compute_locking_fraction(
            theta, time, threshold=locking_threshold, window=locking_window
        )

    # Build DataFrame for structured export
    df = pd.DataFrame(theta, columns=[f"node_{i}" for i in range(N)])
    df.insert(0, "time", time)
    df["order_parameter"] = R
    df["mean_field_phase"] = psi
    df["locking_fraction"] = locking

    # Build enriched metadata
    adjacency = dataset.get("adjacency")
    topology_type = dataset.get("topology_type", "complete")

    # Compute topology stats if adjacency is available
    topology_stats = {}
    if adjacency is not None:
        try:
            import networkx as nx

            G = nx.from_numpy_array(adjacency)
            topology_stats = {
                "num_nodes": G.number_of_nodes(),
                "num_edges": G.number_of_edges(),
                "density": nx.density(G),
                "avg_degree": float(np.mean(dict(G.degree()).values())),
            }
        except Exception:
            topology_stats = {
                "num_nodes": int(adjacency.shape[0]),
                "num_edges": int(np.sum(adjacency) // 2),
            }

    metadata = {
        "n_oscillators": int(N),
        "timesteps": int(T),
        "coupling": float(dataset.get("coupling", 0.0)),
        "noise_std": float(dataset.get("noise_std", 0.0)),
        "solver": str(dataset.get("solver", "unknown")),
        "dt": float(dataset.get("dt", 0.0)),
        "topology_type": topology_type,
        "topology_stats": topology_stats,
        "solver_params": {
            "dt": float(dataset.get("dt", 0.0)),
            "noise_std": float(dataset.get("noise_std", 0.0)),
            "locking_threshold": locking_threshold,
            "locking_window": locking_window,
        },
    }

    # Write JSON
    result = {
        "metadata": metadata,
        "data": df.to_dict(orient="split"),
    }
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)


# ------------------------------------------------------------------------------
# 3️⃣ Public API — Streaming JSONL Export
# ------------------------------------------------------------------------------


def export_for_dash_stream(
    dataset: Dict[str, Any],
    output_path: str,
    callback: Optional[TimestepCallback] = None,
    include_locking: bool = True,
    locking_threshold: float = 0.1,
    locking_window: int = 10,
) -> None:
    """
    Export a Kuramoto dataset as streaming JSONL for near-real-time Dash updates.

    Writes one JSON line per timestep to ``output_path``. A header line (prefixed
    with ``# ``) contains metadata as JSON. Each subsequent line is a JSON object
    with fields: ``t``, ``theta``, ``R``, ``psi``, and ``locking``.

    An optional callback is invoked after each timestep, allowing the caller to
    perform additional actions (e.g., logging, progress reporting).

    Parameters
    ----------
    dataset : Dict[str, Any]
        Dataset dictionary from ``generate_kuramoto_dataset()``. Expected keys:
        ``theta``, ``time``, ``omega``, ``adjacency``, ``coupling``,
        ``noise_std``, ``solver``, etc.
    output_path : str
        Path for the output JSONL file.
    callback : callable, optional
        If provided, called after each timestep as
        ``callback(time, theta_t, record)`` where ``record`` is a
        ``TimestepRecord`` namedtuple.
    include_locking : bool, default True
        Whether to compute and include the locking fraction metric.
    locking_threshold : float, default 0.1
        Frequency deviation threshold for locking detection (rad/s).
    locking_window : int, default 10
        Sliding window size for locking detection (timesteps).

    Examples
    --------
    >>> from kuramoto.api import generate_kuramoto_dataset
    >>> import numpy as np
    >>> data = generate_kuramoto_dataset(
    ...     n_oscillators=10,
    ...     natural_frequencies=np.ones(10),
    ...     coupling=1.5,
    ...     timesteps=100,
    ...     dt=0.02,
    ...     seed=42,
    ... )
    >>> export_for_dash_stream(data, "output.jsonl")  # doctest: +SKIP
    """
    theta = dataset["theta"]
    time = dataset["time"]
    T, N = theta.shape

    # Compute order parameter R(t)
    from .order_parameter import compute_order_parameter

    R = compute_order_parameter(theta)

    # Compute mean field phase ψ(t)
    psi = compute_mean_field_phase(theta)

    # Compute locking fraction if requested
    locking = np.zeros(T)
    if include_locking:
        locking = compute_locking_fraction(
            theta, time, threshold=locking_threshold, window=locking_window
        )

    # Build enriched metadata
    adjacency = dataset.get("adjacency")
    topology_type = dataset.get("topology_type", "complete")

    # Compute topology stats if adjacency is available
    topology_stats = {}
    if adjacency is not None:
        try:
            import networkx as nx

            G = nx.from_numpy_array(adjacency)
            topology_stats = {
                "num_nodes": G.number_of_nodes(),
                "num_edges": G.number_of_edges(),
                "density": nx.density(G),
                "avg_degree": float(np.mean(dict(G.degree()).values())),
            }
        except Exception:
            topology_stats = {
                "num_nodes": int(adjacency.shape[0]),
                "num_edges": int(np.sum(adjacency) // 2),
            }

    metadata = {
        "n_oscillators": int(N),
        "timesteps": int(T),
        "coupling": float(dataset.get("coupling", 0.0)),
        "noise_std": float(dataset.get("noise_std", 0.0)),
        "solver": str(dataset.get("solver", "unknown")),
        "dt": float(dataset.get("dt", 0.0)),
        "topology_type": topology_type,
        "topology_stats": topology_stats,
        "solver_params": {
            "dt": float(dataset.get("dt", 0.0)),
            "noise_std": float(dataset.get("noise_std", 0.0)),
            "locking_threshold": locking_threshold,
            "locking_window": locking_window,
        },
    }

    # Write JSONL file
    with open(output_path, "w") as f:
        # Header line (comment, starts with # )
        f.write(f"# {json.dumps({'metadata': metadata})}\n")
        f.flush()

        # One JSON line per timestep
        for t_idx in range(T):
            t_val = float(time[t_idx])
            theta_t = theta[t_idx].tolist()
            r_val = float(R[t_idx])
            psi_val = float(psi[t_idx])
            lock_val = float(locking[t_idx])

            record = TimestepRecord(
                time=t_val,
                theta=theta[t_idx],
                order_parameter=r_val,
                mean_field_phase=psi_val,
                locking_fraction=lock_val,
            )

            # Invoke callback if provided
            if callback is not None:
                callback(t_val, theta[t_idx], record)

            # Write JSONL line
            line = json.dumps(
                {
                    "t": t_val,
                    "theta": theta_t,
                    "R": r_val,
                    "psi": psi_val,
                    "locking": lock_val,
                }
            )
            f.write(line + "\n")
            f.flush()


# ------------------------------------------------------------------------------
# 💨 Smoke Test
# ------------------------------------------------------------------------------


def _run_smoke_test() -> None:
    """Sanity check for dash_export module."""
    print("💨 Running dash_export smoke tests...")

    rng = get_rng(42)

    # ------------------------------------------------------------------
    # Test 1: Mean field phase range
    # ------------------------------------------------------------------
    theta = rng.uniform(0, 2 * np.pi, (50, 10))
    psi = compute_mean_field_phase(theta)

    assert psi.shape == (50,), f"Expected shape (50,), got {psi.shape}"
    assert np.all((psi >= -np.pi) & (psi <= np.pi)), "ψ(t) out of [-π, π]"

    print(" ... ✔️  Mean field phase range test passed.")

    # ------------------------------------------------------------------
    # Test 2: Locking fraction range
    # ------------------------------------------------------------------
    time = np.linspace(0, 10, 100)
    theta = rng.uniform(0, 2 * np.pi, (100, 20))
    locking = compute_locking_fraction(theta, time)

    assert locking.shape == (100,), f"Expected shape (100,), got {locking.shape}"
    assert np.all((locking >= 0.0) & (locking <= 1.0)), "Locking fraction out of [0, 1]"

    print(" ... ✔️  Locking fraction range test passed.")

    # ------------------------------------------------------------------
    # Test 3: Full export pipeline
    # ------------------------------------------------------------------
    from kuramoto.api import generate_kuramoto_dataset

    data = generate_kuramoto_dataset(
        n_oscillators=10,
        natural_frequencies=np.ones(10),
        coupling=1.5,
        timesteps=50,
        dt=0.02,
        seed=42,
    )

    import os
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        tmp_path = f.name

    try:
        export_for_dash(data, tmp_path)

        with open(tmp_path, "r") as f:
            exported = json.load(f)

        assert "metadata" in exported
        assert "data" in exported
        assert "n_oscillators" in exported["metadata"]
        assert "solver" in exported["metadata"]
        assert "topology_type" in exported["metadata"]

        # Verify backward compatibility: data should be loadable by pandas
        df = pd.DataFrame(exported["data"]["data"], columns=exported["data"]["columns"])
        assert "time" in df.columns
        assert "order_parameter" in df.columns
        assert "mean_field_phase" in df.columns
        assert "locking_fraction" in df.columns

        print(" ... ✔️  Full export pipeline test passed.")
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    print("\n✅ All dash_export smoke tests passed.")


# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry point
# -----------------------------------------------------------------------------------------------------------


def main() -> None:
    """Entry point."""
    _run_smoke_test()


if __name__ == "__main__":
    main()
