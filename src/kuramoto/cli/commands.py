"""
commands.py

Individual command implementations for the Kuramoto CLI.
Provides comprehensive execution capabilities across classical ODE,
Geometric Algebra (GA) rotor, and hybrid Quantum SCF solvers.

Author: Eigenscribe
Date: May 2026
Last Updated: October 2026
"""

from __future__ import annotations

import os
import time as time_module
from typing import Final

import click
import numpy as np

from ..analysis.spectral import (
    compute_fourier_coefficients,
    compute_psd,
    compute_spectral_decomposition,
)
from ..analysis.viz import (
    get_node_colors,
    plot_distributions,
    plot_fourier_convergence,
    plot_fourier_variability,
    plot_network,
    plot_psd_convergence,
    plot_psd_variability,
    plot_time_series,
)
from ..api import generate_kuramoto_dataset
from ..config import parse_simulation_config
from ..order_parameter import compute_order_parameter
from ..quantum.circuit_gen import export_to_qasm, generate_scf_angles
from ..solver_types import (
    SOLVER_ALIASES,
    is_quantum_solver,
    is_rotor_or_euler,
    is_rotor_solver,
)
from ..topologies.tree_of_life import tree_of_life_positions
from ..utils import get_rng
from .style import (
    ansi_256,
    cli_echo,
    cli_error,
    cli_highlight,
    cli_info,
    cli_network,
    cli_quantum,
    cli_rotor,
    cli_success,
    cli_warning,
    supports_256_color,
)
from .utils import DEFAULT_DEMO_PATH, PLOT_DIR, ensure_plot_dir, print_table

__all__: list[str] = [
    "datasetforbeginners",
    "generate",
    "quantum",
    "qasm",
    "benchmark",
    "time",
    "fouriervariability",
    "fourierconvergence",
    "psdvariability",
    "psdconvergence",
    "network",
    "distributions",
]

# -----------------------------------------------------------------------------------------------------------
# 0️⃣ / 🎭 Definitions, Constants & Types
# -----------------------------------------------------------------------------------------------------------

DEFAULT_QUANTUM_SHOTS: Final[int] = 1024
DEFAULT_COUPLING: Final[float] = 1.5


# -----------------------------------------------------------------------------------------------------------
# 1️⃣ Dataset & Generation Commands
# -----------------------------------------------------------------------------------------------------------


@click.command()
@click.option(
    "--output",
    "-o",
    default=DEFAULT_DEMO_PATH,
    help="Output path for the dataset.",
)
def datasetforbeginners(output: str) -> None:
    """Generate a quick starter dataset for beginners."""
    cli_info("Generating demo dataset...")

    params = {
        "n_oscillators": 50,
        "timesteps": 1000,
        "dt": 0.05,
        "coupling": 2.0,
        "seed": 27,
        "topology": "small_world",
    }

    rng = get_rng(params["seed"])
    omega = rng.normal(0, 1.0, params["n_oscillators"])

    data = generate_kuramoto_dataset(natural_frequencies=omega, **params)

    os.makedirs(os.path.dirname(output), exist_ok=True)
    np.savez(output, **data)

    cli_success(f"Dataset successfully saved to '{output}'")
    print_table([params], title="Simulation Parameters")


@click.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="Path to JSON configuration file.",
)
@click.option(
    "--output",
    "-o",
    default="data/output.npz",
    help="Output path for the generated dataset (.npz).",
)
@click.option(
    "--solver",
    "-s",
    default="euler",
    type=click.Choice(list(SOLVER_ALIASES), case_sensitive=False),
    help="Integration method (e.g. rk45, rotor, rkmk4, dopri54, quantum, shot_sampling).",
)
@click.option(
    "--scheme",
    "--quantum-scheme",
    "quantum_scheme",
    default="statevector",
    type=click.Choice(
        ["statevector", "expectation", "shot_sampling"], case_sensitive=False
    ),
    help="Quantum execution scheme (statevector, expectation, shot_sampling).",
)
@click.option(
    "--shots",
    default=1024,
    type=click.IntRange(min=1),
    help="Number of measurement shots for quantum shot_sampling.",
)
@click.option(
    "--dt-internal",
    type=click.FloatRange(min=0.0),
    default=None,
    help="Internal integration sub-step size for rotor/quantum solvers.",
)
@click.option(
    "--enforce-nyquist/--no-nyquist",
    default=True,
    help="Enable/disable Nyquist-inspired temporal resolution check.",
)
@click.option(
    "--adaptive-rtol",
    type=float,
    default=1e-5,
    help="Relative tolerance for adaptive rotor steppers (DOPRI54 / adaptive).",
)
@click.option(
    "--adaptive-atol",
    type=float,
    default=1e-7,
    help="Absolute tolerance for adaptive rotor steppers (DOPRI54 / adaptive).",
)
@click.option(
    "--qasm-out",
    "-q",
    type=click.Path(),
    default=None,
    help="Optional output path to export final OpenQASM 2.0 quantum circuit.",
)
@click.option(
    "--track-symmetries",
    is_flag=True,
    help="Enable Lie symmetry tracking (U(1) gauge invariance, Noether charges).",
)
def generate(
    config: str,
    output: str,
    solver: str,
    quantum_scheme: str,
    shots: int,
    dt_internal: float | None,
    enforce_nyquist: bool,
    adaptive_rtol: float,
    adaptive_atol: float,
    qasm_out: str | None,
    track_symmetries: bool,
) -> None:
    """Generate a dataset from a JSON configuration file with advanced solver controls."""
    if config is None:
        cli_error("Please provide a configuration file with --config / -c")
        return

    with open(config, "r") as f:
        json_str = f.read()

    cli_info(f"Parsing configuration from {config}...")
    params = parse_simulation_config(json_str)

    # CLI option overrides
    params["solver"] = solver.lower()
    if dt_internal is not None:
        params["dt_internal"] = dt_internal
    if not enforce_nyquist:
        params["enforce_nyquist"] = False
    params["adaptive_rtol"] = adaptive_rtol
    params["adaptive_atol"] = adaptive_atol

    if is_quantum_solver(solver):
        params["quantum_scheme"] = quantum_scheme.lower()
        params["shots"] = shots
        cli_quantum(
            f"Running Quantum SCF simulation ({solver}, scheme={quantum_scheme}, shots={shots})..."
        )
    elif is_rotor_solver(solver):
        cli_rotor(f"Running Geometric Algebra rotor simulation ({solver})...")
    else:
        cli_info(f"Running classical ODE simulation ({solver})...")

    # Conditional Lie symmetry tracking
    if track_symmetries and is_rotor_or_euler(solver):
        cli_rotor("Tracking U(1) phase invariance and Lie algebra symmetries...")
        params["symmetry_metrics"] = True
    elif track_symmetries and not is_rotor_or_euler(solver):
        cli_warning("Lie symmetry tracking requires a rotor, Euler, or quantum solver.")

    data = generate_kuramoto_dataset(**params)

    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    np.savez(output, **data)

    cli_success(f"Dataset successfully saved to '{output}'")

    # Optional QASM export
    if qasm_out:
        final_phases = data["theta"][-1]
        omegas = data["omega"]
        adj = data.get("adjacency")
        angles = generate_scf_angles(
            phases=final_phases,
            omegas=omegas,
            K=params["coupling"],
            dt=params["dt"],
            adjacency_matrix=adj,
        )
        qasm_code = export_to_qasm(angles)
        os.makedirs(os.path.dirname(qasm_out) or ".", exist_ok=True)
        with open(qasm_out, "w") as f_qasm:
            f_qasm.write(qasm_code)
        cli_quantum(f"OpenQASM 2.0 quantum circuit exported to '{qasm_out}'")

    # Summary table
    summary = {
        "N": params["n_oscillators"],
        "K": params["coupling"],
        "T": params["timesteps"],
        "dt": params["dt"],
        "solver": solver.upper(),
        "symmetry_tracking": "Yes" if track_symmetries else "No",
    }
    if is_quantum_solver(solver):
        summary["quantum_scheme"] = quantum_scheme
        summary["shots"] = shots

    print_table([summary], title="Simulation Summary")


# -----------------------------------------------------------------------------------------------------------
# 2️⃣ Dedicated Quantum & Geometric Algebra Commands
# -----------------------------------------------------------------------------------------------------------


@click.command()
@click.option(
    "--oscillators",
    "-n",
    default=10,
    type=click.IntRange(min=2),
    help="Number of coupled oscillators / qubits.",
)
@click.option(
    "--coupling",
    "-k",
    default=DEFAULT_COUPLING,
    type=float,
    help="Coupling strength K.",
)
@click.option(
    "--timesteps",
    "-t",
    default=200,
    type=click.IntRange(min=2),
    help="Number of timesteps.",
)
@click.option(
    "--dt",
    default=0.05,
    type=click.FloatRange(min=0.0001),
    help="Time step size.",
)
@click.option(
    "--scheme",
    default="statevector",
    type=click.Choice(
        ["statevector", "expectation", "shot_sampling"], case_sensitive=False
    ),
    help="Quantum simulation scheme.",
)
@click.option(
    "--shots",
    default=DEFAULT_QUANTUM_SHOTS,
    type=click.IntRange(min=1),
    help="Shot count for shot_sampling scheme.",
)
@click.option(
    "--topology",
    type=str,
    default=None,
    help="Network topology (e.g., ring, small_world, bipartite, tree_of_life).",
)
@click.option("--seed", default=42, type=int, help="Random seed for reproducibility.")
@click.option(
    "--output",
    "-o",
    default=None,
    type=click.Path(),
    help="Optional path to save simulation dataset (.npz).",
)
@click.option(
    "--qasm-out",
    "-q",
    default=None,
    type=click.Path(),
    help="Optional path to export OpenQASM 2.0 quantum circuit.",
)
@click.option(
    "--track-symmetries",
    is_flag=True,
    help="Track U(1) global gauge invariance.",
)
def quantum(
    oscillators: int,
    coupling: float,
    timesteps: int,
    dt: float,
    scheme: str,
    shots: int,
    topology: str | None,
    seed: int,
    output: str | None,
    qasm_out: str | None,
    track_symmetries: bool,
) -> None:
    """Run an O(1) circuit depth Quantum Self-Consistent Field (SCF) Kuramoto simulation."""
    cli_quantum(
        f"Simulating Quantum Rotor system with {oscillators} qubits (scheme={scheme})..."
    )

    rng = get_rng(seed)
    omega = rng.normal(0.0, 1.0, oscillators)

    data = generate_kuramoto_dataset(
        n_oscillators=oscillators,
        natural_frequencies=omega,
        coupling=coupling,
        timesteps=timesteps,
        dt=dt,
        topology=topology,
        seed=seed,
        solver="quantum",
        scheme=scheme,
        shots=shots,
        symmetry_metrics=track_symmetries,
    )

    # Compute order parameter
    r = compute_order_parameter(data["theta"])
    mean_r = float(np.mean(r))
    final_r = float(r[-1])

    if output:
        os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
        np.savez(output, **data)
        cli_success(f"Quantum dataset saved to '{output}'")

    if qasm_out:
        final_phases = data["theta"][-1]
        adj = data.get("adjacency")
        angles = generate_scf_angles(
            phases=final_phases,
            omegas=data["omega"],
            K=coupling,
            dt=dt,
            adjacency_matrix=adj,
        )
        qasm_code = export_to_qasm(angles)
        os.makedirs(os.path.dirname(qasm_out) or ".", exist_ok=True)
        with open(qasm_out, "w") as f_qasm:
            f_qasm.write(qasm_code)
        cli_quantum(f"OpenQASM 2.0 quantum circuit exported to '{qasm_out}'")

    stats = [
        {"Parameter / Metric": "Qubits (N)", "Value": oscillators},
        {"Parameter / Metric": "Coupling (K)", "Value": f"{coupling:.2f}"},
        {"Parameter / Metric": "Timesteps", "Value": timesteps},
        {"Parameter / Metric": "Quantum Scheme", "Value": scheme},
        {
            "Parameter / Metric": "Shots",
            "Value": shots if scheme == "shot_sampling" else "N/A (Exact)",
        },
        {"Parameter / Metric": "Circuit Depth", "Value": "O(1) (Parallel R_Z layer)"},
        {"Parameter / Metric": "Mean Order Parameter <|r|>", "Value": f"{mean_r:.4f}"},
        {
            "Parameter / Metric": "Final Order Parameter |r(T)|",
            "Value": f"{final_r:.4f}",
        },
    ]
    if track_symmetries and "global_phase_invariant" in data:
        stats.append(
            {
                "Parameter / Metric": "U(1) Gauge Equivariance",
                "Value": (
                    "Verified (Invariant)"
                    if data["global_phase_invariant"]
                    else "Failed"
                ),
            }
        )

    print_table(stats, title="Quantum SCF Simulation Results")


@click.command()
@click.option(
    "--dataset",
    "-d",
    type=click.Path(exists=True),
    default=None,
    help="Path to dataset .npz file.",
)
@click.option(
    "--step",
    type=int,
    default=-1,
    help="Timestep index to synthesize (default: -1 for final step).",
)
@click.option(
    "--oscillators",
    "-n",
    type=int,
    default=10,
    help="Number of oscillators if generating synthetic angles without a dataset.",
)
@click.option(
    "--coupling",
    "-k",
    type=float,
    default=DEFAULT_COUPLING,
    help="Coupling strength K.",
)
@click.option(
    "--dt",
    type=float,
    default=0.05,
    help="Integration time step.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default=None,
    help="Output path for the generated .qasm file. If omitted, prints to console.",
)
def qasm(
    dataset: str | None,
    step: int,
    oscillators: int,
    coupling: float,
    dt: float,
    output: str | None,
) -> None:
    """Synthesize and export OpenQASM 2.0 quantum circuits from simulation states."""
    if dataset is not None:
        cli_info(f"Loading state snapshot from dataset '{dataset}' at step {step}...")
        data = np.load(dataset)
        phases = data["theta"][step]
        omegas = data["omega"]
        adj = data["adjacency"] if "adjacency" in data else None
    else:
        cli_info(
            f"Generating synthetic quantum SCF angles for N={oscillators} oscillators..."
        )
        rng = get_rng(42)
        phases = rng.uniform(-np.pi, np.pi, size=oscillators)
        omegas = rng.normal(0.0, 1.0, size=oscillators)
        adj = None

    angles = generate_scf_angles(
        phases=phases,
        omegas=omegas,
        K=coupling,
        dt=dt,
        adjacency_matrix=adj,
    )
    qasm_str = export_to_qasm(angles)

    if output:
        os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
        with open(output, "w") as f:
            f.write(qasm_str)
        cli_success(f"OpenQASM 2.0 circuit saved to '{output}'")
    else:
        click.echo("", color=True)
        if supports_256_color():
            click.echo(ansi_256("eigen_cyan", "── OpenQASM 2.0 Circuit ──", bold=True), color=True)
        else:
            click.secho("--- OpenQASM 2.0 Circuit ---", fg="bright_cyan", bold=True)
        click.echo(qasm_str, color=True)
        click.echo("", color=True)


@click.command()
@click.option(
    "--oscillators",
    "-n",
    default=20,
    type=click.IntRange(min=2),
    help="Number of oscillators.",
)
@click.option(
    "--timesteps",
    "-t",
    default=100,
    type=click.IntRange(min=2),
    help="Number of timesteps.",
)
@click.option(
    "--dt",
    default=0.02,
    type=click.FloatRange(min=0.0001),
    help="Time step size.",
)
@click.option(
    "--coupling",
    "-k",
    default=DEFAULT_COUPLING,
    type=float,
    help="Coupling strength K.",
)
@click.option("--seed", default=42, type=int, help="Random seed.")
def benchmark(
    oscillators: int,
    timesteps: int,
    dt: float,
    coupling: float,
    seed: int,
) -> None:
    """Benchmark and compare Classical ODE, GA Rotor, and Quantum SCF solvers."""
    cli_info(
        f"Benchmarking solver suite on N={oscillators} oscillators across {timesteps} steps..."
    )

    solvers_to_test = [
        ("Classic RK45 (Scipy)", "rk45", {}),
        ("GA Vectorized Euler", "rotor", {}),
        ("GA RKMK4 (Lie-Group RK4)", "rkmk4", {}),
        ("GA DOPRI54 (Embedded Adaptive)", "dopri54", {}),
        ("Quantum SCF (Statevector)", "quantum", {"scheme": "statevector"}),
        ("Quantum SCF (Expectation)", "quantum_expectation", {}),
        ("Quantum SCF (1024 Shots)", "quantum_shot_sampling", {"shots": 1024}),
    ]

    rng = get_rng(seed)
    omega = rng.normal(0.0, 1.0, oscillators)

    benchmark_rows = []
    for label, s_name, extra_kwargs in solvers_to_test:
        try:
            t0 = time_module.perf_counter()
            d = generate_kuramoto_dataset(
                n_oscillators=oscillators,
                natural_frequencies=omega,
                coupling=coupling,
                timesteps=timesteps,
                dt=dt,
                seed=seed,
                solver=s_name,
                **extra_kwargs,
            )
            elapsed_ms = (time_module.perf_counter() - t0) * 1000.0
            r = compute_order_parameter(d["theta"])
            benchmark_rows.append(
                {
                    "Solver / Method": label,
                    "Runtime (ms)": f"{elapsed_ms:.2f}",
                    "Mean |r|": f"{np.mean(r):.4f}",
                    "Max |r|": f"{np.max(r):.4f}",
                    "Status": "✅ OK",
                }
            )
        except Exception as e:
            benchmark_rows.append(
                {
                    "Solver / Method": label,
                    "Runtime (ms)": "N/A",
                    "Mean |r|": "N/A",
                    "Max |r|": "N/A",
                    "Status": f"❌ {type(e).__name__}",
                }
            )

    print_table(benchmark_rows, title="Solver Performance & Fidelity Benchmark")


# -----------------------------------------------------------------------------------------------------------
# 3️⃣ Analysis Commands
# -----------------------------------------------------------------------------------------------------------


@click.command()
@click.argument("dataset_path", type=click.Path(exists=True))
@click.option(
    "--start-time",
    "-t",
    type=float,
    default=0.0,
    help="Starting time for analysis.",
)
@click.option(
    "--gradient",
    "-g",
    default="gradient_4",
    help="Gradient theme for coloring.",
)
def time(dataset_path: str, start_time: float, gradient: str) -> None:
    """Plot the temporal signal and its time-average order parameter."""
    data = np.load(dataset_path)
    t = data["time"]
    theta = data["theta"]
    adj = data["adjacency"]

    mask = t >= start_time
    t_filtered = t[mask]
    theta_filtered = theta[mask]

    r = compute_order_parameter(theta_filtered)
    omega = data["omega"]
    colors = get_node_colors(adj, values=omega, cmap_name=gradient)

    ensure_plot_dir()
    plot_path = os.path.join(PLOT_DIR, "time_series.png")
    plot_time_series(
        t_filtered, theta_filtered, r, node_colors=colors, save_path=plot_path
    )

    cli_success(f"Plot saved to {plot_path}")

    stats = [
        {"Metric": "Mean Order Parameter", "Value": f"{np.mean(r):.4f}"},
        {"Metric": "Std Order Parameter", "Value": f"{np.std(r):.4f}"},
        {"Metric": "Max Order Parameter", "Value": f"{np.max(r):.4f}"},
        {"Metric": "Min Order Parameter", "Value": f"{np.min(r):.4f}"},
    ]
    print_table(stats, title="Time Series Statistics")


@click.command()
@click.argument("dataset_path", type=click.Path(exists=True))
@click.option("--start-time", "-t", type=float, default=0.0)
@click.option("--freq", "-f", type=float, required=True, help="Target frequency.")
@click.option(
    "--gradient",
    "-g",
    default="gradient_4",
    help="Gradient theme for coloring.",
)
def fouriervariability(
    dataset_path: str, start_time: float, freq: float, gradient: str
) -> None:
    """Plot the Fourier variability diagnostic results."""
    data = np.load(dataset_path)
    t = data["time"]
    theta = data["theta"]
    adj = data["adjacency"]

    mask = t >= start_time
    t_filtered = t[mask]
    signals = np.sin(theta[mask])

    coeffs = compute_fourier_coefficients(t_filtered, signals, freq)
    amplitudes = np.abs(coeffs)
    omega = data["omega"]
    colors = get_node_colors(adj, values=omega, cmap_name=gradient)

    ensure_plot_dir()
    plot_path = os.path.join(PLOT_DIR, "fourier_variability.png")
    plot_fourier_variability(
        amplitudes, node_colors=colors, freq=freq, save_path=plot_path
    )

    cli_success(f"Plot saved to {plot_path}")

    top_5_idx = np.argsort(amplitudes)[-5:][::-1]
    top_5_vals = [{"Index": i, "Amplitude": f"{amplitudes[i]:.4f}"} for i in top_5_idx]
    print_table(top_5_vals, title=f"Top 5 Oscillators at {freq} Hz")


@click.command()
@click.argument("dataset_path", type=click.Path(exists=True))
@click.option("--start-time", "-t", type=float, default=0.0)
@click.option("--freq", "-f", type=float, required=True)
def fourierconvergence(dataset_path: str, start_time: float, freq: float) -> None:
    """Plot discrete Fourier transform convergence."""
    data = np.load(dataset_path)
    t = data["time"]
    theta = data["theta"]

    mask = t >= start_time
    t_filtered = t[mask]
    r = compute_order_parameter(theta[mask])

    steps = np.linspace(len(r) // 10, len(r), 10, dtype=int)
    conv_results = []
    for step in steps:
        c = compute_fourier_coefficients(t_filtered[:step], r[:step, np.newaxis], freq)
        conv_results.append(
            {
                "Duration": f"{t_filtered[step - 1]:.2f}",
                "Amplitude": np.abs(c[0]),
            }
        )

    ensure_plot_dir()
    plot_path = os.path.join(PLOT_DIR, "fourier_convergence.png")
    plot_fourier_convergence(
        durations=[float(d["Duration"]) for d in conv_results],
        amplitudes=[d["Amplitude"] for d in conv_results],
        freq=freq,
        save_path=plot_path,
    )

    cli_success(f"Plot saved to {plot_path}")
    print_table(conv_results, title=f"Convergence of r(t) at {freq} Hz")


@click.command()
@click.argument("dataset_path", type=click.Path(exists=True))
@click.option("--start-time", "-t", type=float, default=0.0)
@click.option("--freq", "-f", type=float, required=True)
def psdvariability(dataset_path: str, start_time: float, freq: float) -> None:
    """Plot the spectral energy at the target frequency."""
    data = np.load(dataset_path)
    t = data["time"]
    theta = data["theta"]
    dt = t[1] - t[0]
    fs = 1.0 / dt

    mask = t >= start_time
    r = compute_order_parameter(theta[mask])

    f, pxx = compute_psd(r[:, np.newaxis], fs, nperseg=min(len(r), 1024))
    dist = compute_spectral_decomposition(f, pxx, freq, bandwidth=freq * 0.1)

    ensure_plot_dir()
    plot_path = os.path.join(PLOT_DIR, "psd_variability.png")
    plot_psd_variability(f, pxx, target_freq=freq, save_path=plot_path)

    cli_success(f"Plot saved to {plot_path}")

    dist_table = [
        {"Component": k.capitalize(), "Energy Fraction": f"{v:.2%}"}
        for k, v in dist.items()
    ]
    print_table(dist_table, title="Spectral Energy Distribution")


@click.command()
@click.argument("dataset_path", type=click.Path(exists=True))
@click.option("--start-time", "-t", type=float, default=0.0)
@click.option("--freq", "-f", type=float, required=True)
def psdconvergence(dataset_path: str, start_time: float, freq: float) -> None:
    """Plot the PSD convergence diagnostic results."""
    data = np.load(dataset_path)
    t = data["time"]
    theta = data["theta"]
    dt = t[1] - t[0]
    fs = 1.0 / dt

    mask = t >= start_time
    r = compute_order_parameter(theta[mask])

    n = len(r)
    signals = {
        "Full": r,
        "Last Half": r[n // 2 :],
        "Last Quarter": r[3 * n // 4 :],
    }

    # Compute PSD for each window and collect stats
    psd_data = {}
    shared_f = None
    conv_stats = []
    for label, sig in signals.items():
        f, pxx = compute_psd(sig[:, np.newaxis], fs, nperseg=min(len(sig), 512))
        psd_data[label] = pxx[:, 0]
        if shared_f is None:
            shared_f = f

        # Find peak near target frequency
        idx_target = np.argmin(np.abs(f - freq))
        peak_idx = (
            idx_target
            - 10
            + np.argmax(pxx[max(0, idx_target - 10) : idx_target + 10, 0])
        )
        conv_stats.append(
            {
                "Window": label,
                "Samples": len(sig),
                "Peak Freq": f"{f[peak_idx]:.4f}",
                "Peak PSD": f"{pxx[peak_idx, 0]:.4e}",
            }
        )

    ensure_plot_dir()
    plot_path = os.path.join(PLOT_DIR, "psd_convergence.png")
    plot_psd_convergence(shared_f, psd_data, target_freq=freq, save_path=plot_path)

    cli_success(f"Plot saved to {plot_path}")
    print_table(conv_stats, title="PSD Convergence Statistics")


# -----------------------------------------------------------------------------------------------------------
# 4️⃣ Visualization Commands
# -----------------------------------------------------------------------------------------------------------


@click.command()
@click.argument("dataset_path", type=click.Path(exists=True))
@click.option(
    "--gradient",
    "-g",
    default="gradient_4",
    help="Gradient theme to use.",
)
def network(dataset_path: str, gradient: str) -> None:
    """Visualize the oscillator network structure."""
    data = np.load(dataset_path)
    adj = data["adjacency"]
    omega = data["omega"]

    ensure_plot_dir()
    plot_path = os.path.join(PLOT_DIR, "network.png")

    # Determine if we should use the Tree of Life layout
    pos = None
    if adj.shape == (10, 10):
        from ..topologies.tree_of_life import sefirot_labels

        pos_dict = tree_of_life_positions()
        labels = sefirot_labels()
        pos = {i: pos_dict[labels[i]] for i in range(10)}
        cli_network("Using canonical Tree of Life layout.")

    cli_network(f"Visualizing network with {gradient} theme (colored by frequency)...")
    plot_network(
        adj, node_values=omega, pos=pos, cmap_name=gradient, save_path=plot_path
    )
    cli_success(f"Plot saved to {plot_path}")

    import networkx as nx

    G = nx.from_numpy_array(adj)

    stats = [
        {"Metric": "Nodes", "Value": G.number_of_nodes()},
        {"Metric": "Edges", "Value": G.number_of_edges()},
        {"Metric": "Density", "Value": f"{nx.density(G):.4f}"},
        {"Metric": "Avg Degree", "Value": f"{np.mean([d for n, d in G.degree()]):.2f}"},
    ]
    print_table(stats, title="Network Statistics")


@click.command()
@click.argument("dataset_path", type=click.Path(exists=True))
@click.option(
    "--gradient",
    "-g",
    default="gradient_3",
    help="Gradient theme to use.",
)
def distributions(dataset_path: str, gradient: str) -> None:
    """Visualize frequency and phase distributions."""
    data = np.load(dataset_path)
    omega = data["omega"]
    theta_0 = data["initial_conditions"]

    ensure_plot_dir()
    plot_path = os.path.join(PLOT_DIR, "distributions.png")

    cli_info(f"Visualizing distributions with {gradient} theme...")
    plot_distributions(omega, theta_0, cmap_name=gradient, save_path=plot_path)
    cli_success(f"Plot saved to {plot_path}")

    stats = [
        {
            "Variable": "Natural Frequencies (omega)",
            "Mean": f"{np.mean(omega):.4f}",
            "Std": f"{np.std(omega):.4f}",
        },
        {
            "Variable": "Initial Phases (theta_0)",
            "Mean": f"{np.mean(theta_0):.4f}",
            "Std": f"{np.std(theta_0):.4f}",
        },
    ]
    print_table(stats, title="Distribution Statistics")


# -----------------------------------------------------------------------------------------------------------
# 💨 Smoke tests
# -----------------------------------------------------------------------------------------------------------


def _run_smoke_test() -> None:
    """Quick sanity check for CLI commands definitions."""
    print("💨 Running commands smoke test...")
    assert callable(datasetforbeginners)
    assert callable(generate)
    assert callable(quantum)
    assert callable(qasm)
    assert callable(benchmark)
    assert callable(time)
    assert callable(network)
    print("✅ Commands smoke test passed.")


# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry point
# -----------------------------------------------------------------------------------------------------------


def main() -> None:
    """Entry point for standalone execution."""
    _run_smoke_test()


if __name__ == "__main__":
    main()
