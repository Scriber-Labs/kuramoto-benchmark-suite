"""
commands.py

Individual command implementations for the Kuramoto CLI.

Author: Eigenscribe
Date: May 2026
"""

from __future__ import annotations

import os
import click
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any

from ..api import generate_kuramoto_dataset
from ..analysis.spectral import (
    compute_fourier_coefficients,
    compute_psd,
    compute_spectral_distribution
)
from ..analysis.viz import (
    plot_network,
    plot_distributions,
    get_node_colors,
    set_style,
    GRADIENTS
)
from ..config import parse_simulation_config
from ..order_parameter import compute_order_parameter
from .utils import ensure_plot_dir, print_table, DEFAULT_DEMO_PATH, PLOT_DIR

# -----------------------------------------------------------------------------------------------------------
# 1️⃣ Dataset Commands
# -----------------------------------------------------------------------------------------------------------

@click.command()
@click.option("--output", "-o", default=DEFAULT_DEMO_PATH, help="Output path for the dataset.")
def datasetforbeginners(output: str) -> None:
    """Copy a set of signals to train using the suite."""
    click.secho(f"🚀 Generating demo dataset...", fg="green")
    
    params = {
        "n_oscillators": 50,
        "timesteps": 1000,
        "dt": 0.05,
        "coupling": 2.0,
        "seed": 42,
        "topology": "ring"
    }
    
    rng = np.random.default_rng(params["seed"])
    omega = rng.normal(0, 1.0, params["n_oscillators"])
    
    data = generate_kuramoto_dataset(
        natural_frequencies=omega,
        **params
    )
    
    os.makedirs(os.path.dirname(output), exist_ok=True)
    np.savez(output, **data)
    
    click.secho(f"✅ Success: Dataset saved to '{output}'", fg="bright_green")
    
    # Table output
    print_table([params], title="Simulation Parameters")

# -----------------------------------------------------------------------------------------------------------
# 2️⃣ Analysis Commands
# -----------------------------------------------------------------------------------------------------------

@click.command()
@click.option("--config", "-c", type=click.Path(exists=True), help="Path to JSON config file.")
@click.option("--output", "-o", default="data/output.npz", help="Output path for the dataset.")
def generate(config: str, output: str) -> None:
    """Generate a dataset from a JSON configuration file."""
    if config is None:
        click.secho("❌ Error: Please provide a configuration file with --config", fg="red")
        return

    with open(config, "r") as f:
        json_str = f.read()
    
    click.secho(f"🚀 Parsing configuration from {config}...", fg="cyan")
    params = parse_simulation_config(json_str)
    
    click.secho(f"🏃 Running simulation...", fg="green")
    data = generate_kuramoto_dataset(**params)
    
    os.makedirs(os.path.dirname(output), exist_ok=True)
    np.savez(output, **data)
    
    click.secho(f"✅ Success: Dataset saved to '{output}'", fg="bright_green")
    
    # Summary table
    summary = {
        "N": params["n_oscillators"],
        "K": params["coupling"],
        "T": params["timesteps"],
        "dt": params["dt"]
    }
    print_table([summary], title="Simulation Summary")

@click.command()
@click.argument("dataset_path", type=click.Path(exists=True))
@click.option("--start-time", "-t", type=float, default=0.0, help="Starting time for analysis.")
@click.option("--gradient", "-g", default="gradient_4", help="Gradient theme for coloring.")
def time(dataset_path: str, start_time: float, gradient: str) -> None:
    """Plot the temporal signal and its time-average."""
    set_style()
    data = np.load(dataset_path)
    t = data["time"]
    theta = data["theta"]
    adj = data["adjacency"]
    
    mask = t >= start_time
    t_filtered = t[mask]
    theta_filtered = theta[mask]
    
    r = compute_order_parameter(theta_filtered)
    colors = get_node_colors(adj, cmap_name=gradient)
    
    ensure_plot_dir()
    plt.figure(figsize=(10, 6))
    plt.subplot(2, 1, 1)
    
    # Plot first 10 oscillators with consistent colors
    n_plot = min(10, theta_filtered.shape[1])
    for i in range(n_plot):
        plt.plot(t_filtered, np.sin(theta_filtered[:, i]), alpha=0.6, color=colors[i], label=f"Node {i}")
    
    plt.title(f"Phases (first {n_plot} oscillators, colored by degree)")
    plt.ylabel("sin(theta)")
    
    plt.subplot(2, 1, 2)
    plt.plot(t_filtered, r, 'k-', linewidth=2, label="Order Parameter r(t)")
    plt.axhline(np.mean(r), color=GRADIENTS["gradient_7"][-1], linestyle='--', label=f"Avg: {np.mean(r):.3f}")
    plt.xlabel("Time")
    plt.ylabel("Coherence r")
    plt.legend(loc='upper right', fontsize='small', ncol=2)
    
    plot_path = os.path.join(PLOT_DIR, "time_series.png")
    plt.savefig(plot_path)
    plt.close()
    
    click.echo(f"📈 Plot saved to {plot_path}")
    
    stats = [
        {"Metric": "Mean Order Parameter", "Value": f"{np.mean(r):.4f}"},
        {"Metric": "Std Order Parameter", "Value": f"{np.std(r):.4f}"},
        {"Metric": "Max Order Parameter", "Value": f"{np.max(r):.4f}"},
        {"Metric": "Min Order Parameter", "Value": f"{np.min(r):.4f}"}
    ]
    print_table(stats, title="Time Series Statistics")

@click.command()
@click.argument("dataset_path", type=click.Path(exists=True))
@click.option("--start-time", "-t", type=float, default=0.0)
@click.option("--freq", "-f", type=float, required=True, help="Target frequency.")
@click.option("--gradient", "-g", default="gradient_4", help="Gradient theme for coloring.")
def fouriervariability(dataset_path: str, start_time: float, freq: float, gradient: str) -> None:
    """Plot the Fourier variability diagnostic results."""
    set_style()
    data = np.load(dataset_path)
    t = data["time"]
    theta = data["theta"]
    adj = data["adjacency"]
    
    mask = t >= start_time
    t_filtered = t[mask]
    signals = np.sin(theta[mask])
    
    coeffs = compute_fourier_coefficients(t_filtered, signals, freq)
    amplitudes = np.abs(coeffs)
    colors = get_node_colors(adj, cmap_name=gradient)
    
    ensure_plot_dir()
    plt.figure(figsize=(10, 5))
    plt.bar(range(len(amplitudes)), amplitudes, color=colors, edgecolor="white", linewidth=0.5)
    plt.axhline(np.mean(amplitudes), color="black", linestyle='--', alpha=0.5, label="Mean")
    plt.xlabel("Oscillator Index")
    plt.ylabel(f"Fourier Amplitude at {freq} Hz")
    plt.title(f"Fourier Variability (colored by degree)")
    plt.legend()
    
    plot_path = os.path.join(PLOT_DIR, "fourier_variability.png")
    plt.savefig(plot_path)
    plt.close()
    
    click.echo(f"📈 Plot saved to {plot_path}")
    
    top_5_idx = np.argsort(amplitudes)[-5:][::-1]
    top_5_vals = [
        {"Index": i, "Amplitude": f"{amplitudes[i]:.4f}"} for i in top_5_idx
    ]
    print_table(top_5_vals, title=f"Top 5 Oscillators at {freq} Hz")

@click.command()
@click.argument("dataset_path", type=click.Path(exists=True))
@click.option("--start-time", "-t", type=float, default=0.0)
@click.option("--freq", "-f", type=float, required=True)
def fourierconvergence(dataset_path: str, start_time: float, freq: float) -> None:
    """Plot discrete Fourier transform convergence."""
    set_style()
    data = np.load(dataset_path)
    t = data["time"]
    theta = data["theta"]
    
    mask = t >= start_time
    t_filtered = t[mask]
    r = compute_order_parameter(theta[mask])
    
    steps = np.linspace(len(r)//10, len(r), 10, dtype=int)
    conv_results = []
    for step in steps:
        c = compute_fourier_coefficients(t_filtered[:step], r[:step, np.newaxis], freq)
        conv_results.append({
            "Duration": f"{t_filtered[step-1]:.2f}",
            "Amplitude": np.abs(c[0])
        })
        
    ensure_plot_dir()
    plt.figure(figsize=(8, 5))
    plt.plot([float(d["Duration"]) for d in conv_results], [d["Amplitude"] for d in conv_results], 'o-', color=GRADIENTS["gradient_5"][2])
    plt.xlabel("Signal Duration")
    plt.ylabel(f"Fourier Amplitude of r(t) at {freq} Hz")
    plt.title("Fourier Convergence")
    
    plot_path = os.path.join(PLOT_DIR, "fourier_convergence.png")
    plt.savefig(plot_path)
    plt.close()
    
    click.echo(f"📈 Plot saved to {plot_path}")
    print_table(conv_results, title=f"Convergence of r(t) at {freq} Hz")

@click.command()
@click.argument("dataset_path", type=click.Path(exists=True))
@click.option("--start-time", "-t", type=float, default=0.0)
@click.option("--freq", "-f", type=float, required=True)
def psdvariability(dataset_path: str, start_time: float, freq: float) -> None:
    """Plot the spectral energy at the target frequency."""
    set_style()
    data = np.load(dataset_path)
    t = data["time"]
    theta = data["theta"]
    dt = t[1] - t[0]
    fs = 1.0 / dt
    
    mask = t >= start_time
    r = compute_order_parameter(theta[mask])
    
    f, pxx = compute_psd(r[:, np.newaxis], fs, nperseg=min(len(r), 1024))
    dist = compute_spectral_distribution(f, pxx, freq, bandwidth=freq*0.1)
    
    ensure_plot_dir()
    plt.figure(figsize=(8, 5))
    plt.semilogy(f, pxx, color=GRADIENTS["gradient_1"][1])
    plt.axvline(freq, color='r', linestyle='--', label='Target')
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("PSD")
    plt.title(f"PSD Variability")
    plt.legend()
    
    plot_path = os.path.join(PLOT_DIR, "psd_variability.png")
    plt.savefig(plot_path)
    plt.close()
    
    click.echo(f"📈 Plot saved to {plot_path}")
    
    dist_table = [
        {"Component": k.capitalize(), "Energy Fraction": f"{v:.2%}"} for k, v in dist.items()
    ]
    print_table(dist_table, title="Spectral Energy Distribution")

@click.command()
@click.argument("dataset_path", type=click.Path(exists=True))
@click.option("--start-time", "-t", type=float, default=0.0)
@click.option("--freq", "-f", type=float, required=True)
def psdconvergence(dataset_path: str, start_time: float, freq: float) -> None:
    """Plot the PSD convergence diagnostic results."""
    set_style()
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
        "Last Half": r[n//2:],
        "Last Quarter": r[3*n//4:]
    }
    
    ensure_plot_dir()
    plt.figure(figsize=(10, 6))
    conv_stats = []
    for label, sig in signals.items():
        f, pxx = compute_psd(sig[:, np.newaxis], fs, nperseg=min(len(sig), 512))
        plt.loglog(f, pxx, label=label)
        
        # Find peak near target frequency
        idx_target = np.argmin(np.abs(f - freq))
        peak_idx = idx_target - 10 + np.argmax(pxx[max(0, idx_target-10):idx_target+10, 0])
        conv_stats.append({
            "Window": label,
            "Samples": len(sig),
            "Peak Freq": f"{f[peak_idx]:.4f}",
            "Peak PSD": f"{pxx[peak_idx, 0]:.4e}"
        })
        
    plt.axvline(freq, color='k', linestyle=':')
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("PSD")
    plt.title("PSD Convergence")
    plt.legend()
    
    plot_path = os.path.join(PLOT_DIR, "psd_convergence.png")
    plt.savefig(plot_path)
    plt.close()
    
    click.echo(f"📈 Plot saved to {plot_path}")
    print_table(conv_stats, title="PSD Convergence Statistics")

# -----------------------------------------------------------------------------------------------------------
# 3️⃣ Visualization Commands
# -----------------------------------------------------------------------------------------------------------

@click.command()
@click.argument("dataset_path", type=click.Path(exists=True))
@click.option("--gradient", "-g", default="gradient_4", help="Gradient theme to use.")
def network(dataset_path: str, gradient: str) -> None:
    """Visualize the oscillator network structure."""
    data = np.load(dataset_path)
    adj = data["adjacency"]
    
    ensure_plot_dir()
    plot_path = os.path.join(PLOT_DIR, "network.png")
    
    click.echo(f"🕸️ Visualizing network with {gradient} theme (colored by degree)...")
    plot_network(adj, node_colors=None, cmap_name=gradient, save_path=plot_path)
    click.echo(f"📈 Plot saved to {plot_path}")
    
    import networkx as nx
    G = nx.from_numpy_array(adj)
    
    stats = [
        {"Metric": "Nodes", "Value": G.number_of_nodes()},
        {"Metric": "Edges", "Value": G.number_of_edges()},
        {"Metric": "Density", "Value": f"{nx.density(G):.4f}"},
        {"Metric": "Avg Degree", "Value": f"{np.mean([d for n, d in G.degree()]):.2f}"}
    ]
    print_table(stats, title="Network Statistics")

@click.command()
@click.argument("dataset_path", type=click.Path(exists=True))
@click.option("--gradient", "-g", default="gradient_3", help="Gradient theme to use.")
def distributions(dataset_path: str, gradient: str) -> None:
    """Visualize frequency and phase distributions."""
    data = np.load(dataset_path)
    omega = data["omega"]
    theta_0 = data["initial_conditions"]
    
    ensure_plot_dir()
    plot_path = os.path.join(PLOT_DIR, "distributions.png")
    
    click.echo(f"📊 Visualizing distributions with {gradient} theme...")
    plot_distributions(omega, theta_0, cmap_name=gradient, save_path=plot_path)
    click.echo(f"📈 Plot saved to {plot_path}")
    
    stats = [
        {"Variable": "Natural Frequencies (omega)", "Mean": f"{np.mean(omega):.4f}", "Std": f"{np.std(omega):.4f}"},
        {"Variable": "Initial Phases (theta_0)", "Mean": f"{np.mean(theta_0):.4f}", "Std": f"{np.std(theta_0):.4f}"}
    ]
    print_table(stats, title="Distribution Statistics")
