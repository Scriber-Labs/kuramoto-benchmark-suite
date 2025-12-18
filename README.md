# Kuramoto Benchmark Suite

A reproducible benchmark and dataset generator for coupled oscillator systems based on the Kuramoto model.

This repository provides:
- A **deterministic Kuramoto simulator** with configurable coupling and network topology.
- A **standardized dataset format** suitable for system identification, reduced-order modeling, and physics-informed learning.
- A small set of **validation tests** ensuring reproducibility, correctness, and numerical stability.

🥅 **Goal:** Supply a **high-quality synthetic dynamical dataset** that can be used downstream in:
- SINDy / sparse system identification
- Physics-informed neural networks (PINNs)
- Graph-based dynamical systems analysis
- Synchronization and phase-transition studies

---
## Mathematical Model
The **Kuramoto model** describes the phase evolution of a system of $N$ coupled phase oscillators:

   $$\frac{d\theta_i}{dt}=\omega_i+\frac{1}{N}\sum_{j=1}^N{K_{ij} \sin\big(\theta_j - \theta_i\big)}$$

where:
- $\theta_i(t)$ is the phase of the $i^\text{th}$ oscillator
- $\omega_i$ is the intrinsic frequency of the $i^\text{th}$ oscillator
- $K_{ij}$ encodes network structure and coupling strength between adjacent oscillators

---
## Scientific Design Principles
This implementation emphasizes:
1. **Reproducibility** - All simulations are deterministic when a random seed is supplied.
3. **Structure preservation** - Phase variables are evolved directly and wrapped modulo $2\pi$ to prevent drift.
4. **Separation of concerns** - Data generation, validation, and storage are all clearly separated.
5. **Black-box usability** - Downstream users do not need to inspect the implementation to use the data.

---
## Public API (Data Generation)

The core entry point is:
```py
generate_kuramoto_dataset(...)
```

This function:
- Generates phase trajectories $\theta_i(t)$
- Computes instantaneous phase velocities $\dot{\theta}_i(t)$
- Records simulation metadata and graph statistics
- Returns data in a standardized dictionary format

The API is intentinoally minimal and stable to support reuse across projects.

For parameter definitions and returned shapes, see function docstring.

---
## Dataset Structure
Each simulation generates:
- Phase trajectories: `(T, N)`
- Phase derivatives: `(T, N)`
- Time vector: `(T,)`
- Intrinsic frequencies: `(N,)`
- Initial conditions: `(N,)`
- Graph metadata (connectivity, density, etc.)

These outputs are suitable for direct use in:
- Regression-based system identification
- Dimensionality reduction
- Order-parameter analysis

---
## Validation and Testing
A standalone test harness verifies:
- Deterministic behavior
- Input immutability
- Correct handling of network structure
- Performance at moderate system sizes
- Presence of complete type annotations and documentation

Tests are black-box by design and do not depend on internal implementation details.

---
## Intended Scope
This repository intentionally **does NOT** include:
- Learning algorithms
- Visualization pipelines
- GPU acceleration
- External dependenccies beyond NumPy

✨ These concerns are better handled downstream once the data is fixed.

---
## Scientific Motivation
Coupled oscillator systems appear across:
- Neuroscience (rhythms, synchronization)
- Physics (phase transitions, collective behavior)
- Chemistry (reaction networks)
- Network science

This benchmark suite is meant to provide a clean experimental substrate for studying these phenomena in a controlled and reproducible way.
