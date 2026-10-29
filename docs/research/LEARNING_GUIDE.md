# 📘 Kuramoto Research & Learning Guide
*A Portfolio of Geometric Mechanics, Synchronization, and Quantum Bridges*

> ⚠️ **AI-GENERATED CONTENT NOTICE:** This learning guide was drafted with the assistance of an AI (Junie). It is intended as an educational resource and theoretical overview of the `kuramoto-benchmark-suite`.

## Overview
This guide serves as the theoretical backbone of the `kuramoto-benchmark-suite`. It bridges first-principles physics (Fluid Dynamics, Lie Algebras) with modern computational tools (Geometric Algebra, Quantum Circuits).

---

## 1. The Mathematical Foundation: Geometric Algebra (GA)
### 1.1 Why Rotors?
In standard Kuramoto models, the state is an angle $\theta$. In higher dimensions (Lohe model), it's a unit vector $\vec{u}$. Rotors $R$ generalize both by representing rotations as elements of a Clifford Algebra:
$$R = \exp(-B \theta / 2)$$
where $B$ is a unit bivector defining the plane of rotation.

### 1.2 Bivector Torque Derivation
The interaction between oscillators $i$ and $j$ can be viewed as a "pull" in the plane formed by their orientation vectors $v_i$ and $v_j$. 
In GA, this plane is the **outer product** (wedge product):
$$\text{Torque}_{ij} = v_j \wedge v_i$$
When $N$ is large, we interact with the **Mean Field**:
$$v_{\text{mean}} = \frac{1}{N} \sum_j v_j$$
The collective torque on oscillator $i$ is:
$$\Omega_i = K (v_{\text{mean}} \wedge v_i)$$
This bivector $\Omega_i$ acts as the generator of the rotation. The evolution of the rotor $R_i$ is then:
$$\frac{dR_i}{dt} = -\frac{1}{2} \Omega_i R_i$$

---

## 2. The Fluid Flow Analogy (Vorticity)
### 2.1 Bivector as Vorticity
In fluid mechanics, **vorticity** $\zeta$ is a bivector representing local angular velocity. 
A synchronization transition in the Kuramoto model is mathematically equivalent to the formation of a **vortex** in phase space.
- **Laminar Flow**: Oscillators move independently (incoherence).
- **Vortex Core**: Oscillators cluster and rotate together (synchronization).

### 2.2 Visualizing the Pull
By mapping the bivector torque $\Omega(x,y)$ to a vector field, we can use **streamplots** to visualize how the "fluid of oscillators" flows toward the synchronized state. The streamlines represent the paths of least resistance on the manifold.

---

## 3. The Quantum Bridge: SCF Mapping
### 3.1 Self-Consistent Field (SCF)
The non-linear interaction $K \sum \sin(\theta_j - \theta_i)$ is difficult to map directly to a quantum circuit because it requires $O(N^2)$ gates. 
However, by using the **SCF approximation**, we treat each oscillator as moving in a time-dependent mean field $v_{\text{mean}}(t)$. In our classical source code, this is implemented as the `fast` method in the `RotorSolver`, which scales linearly with the number of oscillators.

### 3.2 $O(1)$ Circuit Depth
If $v_{\text{mean}}(t)$ is known or approximated classically, the update for all $N$ oscillators can be performed in **parallel** using single-qubit rotation gates $R_z(\phi_i)$:
$$\phi_i = (\omega_i + K R \sin(\psi - \theta_i)) \Delta t$$
This result is profound: **A fully coupled Kuramoto system can be simulated on quantum hardware with constant circuit depth.**

---

## 4. High-Order Lie-Group Integrators & Cartesian Product Manifolds
### 4.1 Runge-Kutta Munthe-Kaas (RKMK4) on Lie Algebras
Standard Runge-Kutta methods evaluate linear combinations in Euclidean space $\mathbb{R}^d$, causing numerical trajectories to drift off curved manifolds like $\operatorname{Spin}(n)$ or $\operatorname{SO}(n)$.
Runge-Kutta Munthe-Kaas (RKMK) solves this by mapping stages into the **Lie algebra** $\mathfrak{g} \cong \bigwedge^2 \mathbb{R}^n$, evaluating velocity fields $\Omega_i$, and advancing the group state via the exponential map:
$$y_{n+1} = y_n \exp\left(-\frac{\Delta t}{2} \left[\frac{\omega_1 + 2\omega_2 + 2\omega_3 + \omega_4}{6}\right] B\right)$$
Because $\exp: \mathfrak{spin}(n) \to \operatorname{Spin}(n)$ maps directly into the unit rotor manifold, the invariant $\|R\|^2 = R\tilde{R} = 1$ is preserved to machine precision ($10^{-16}$) without projection.

### 4.2 Dormand-Prince 5(4) (DOPRI54) with FSAL Caching
To achieve high-order accuracy with adaptive error control:
1. **Embedded Pair**: 7 Lie-algebra stages evaluate both a 5th-order candidate $y_5$ and a 4th-order candidate $y_4$, estimating local truncation error directly on the bivector space:
   $$\text{LTE} = \Delta t \left\| \sum_{i=1}^7 (b_i^{(5)} - b_i^{(4)}) \omega_i \right\|_\infty$$
2. **First-Same-As-Last (FSAL)**: The 7th velocity stage evaluated at the accepted state $y_5$ satisfies $\omega_7 = \Omega(y_5, K)$, which is identical to stage 1 $\omega_1$ of the next step. Reusing this cached bivector reduces the cost from 7 evaluations to 6 per accepted step.
3. **Cartesian Product $\operatorname{Spin}(n)^N$**: The total network manifold is the direct product group $\mathcal{M} = \operatorname{Spin}(n)^N$. The group exponential factorizes cleanly across all $N$ oscillators, allowing vectorized SIMD evaluation while tracking component-wise maximum error across the ensemble.

### 4.3 Time-Reversal Symmetry & Symplectic Properties
In conservative systems ($K=0$ or symmetric potential gradients), continuous dynamics are time-reversible ($t \to -t, \omega \to -\omega$). High-order Lie-group integrators (RKMK4 and DOPRI54) preserve time-reversal symmetry up to high-order truncation cancellations, enabling long-time roundtrip reconstructions ($T=50\,\text{s}$) with errors below $10^{-12}$.

---

## 5. Numerical Analysis for Nonlinear Systems
### 5.1 Stability
Numerical stability refers to the property that errors do not grow exponentially over time. For the Kuramoto model, the step size $\Delta t$ must be small enough to resolve the fastest oscillations (the high-frequency natural frequencies $\omega_i$) and the strongest coupling $K$.
A rule of thumb for Euler-like methods is $\Delta t < 2 / (K + \max|\omega_i|)$.

### 5.2 Consistency
A method is **consistent** if the local truncation error goes to zero as $\Delta t \to 0$. The `RotorSolver`'s geometric update is first-order consistent in time, but zeroth-order consistent with the unit-norm constraint (meaning it preserves the constraint exactly, which is a significant advantage over phase-based methods that might suffer from numerical drift if converted to vectors). High-order schemes (RKMK4, DOPRI54) achieve 4th- and 5th-order consistency.

### 5.3 Convergence (Lax Equivalence Theorem)
For linear problems, the Lax Equivalence Theorem states that **Consistency + Stability = Convergence**. For nonlinear systems like Kuramoto, convergence is generally guaranteed if the vector field is Lipschitz continuous and the method is stable and consistent. Our benchmarks against RK45 confirm that the GA rotor solver converges to the physical ground truth.

---

## 6. Key Sources & Citations
- **Kuramoto (1975)**: "Self-entrainment of a population of coupled non-linear oscillators."
- **Munthe-Kaas (1998)**: "Runge-Kutta methods on Lie groups."
- **Dormand & Prince (1980)**: "A family of embedded Runge-Kutta formulae."
- **Lohe (2009)**: "Non-abelian Kuramoto models and synchronization."
- **Doran & Lasenby (2003)**: "Geometric Algebra for Physicists." (Standard GA reference).
- **Acebrón et al. (2005)**: "The Kuramoto model: A simple paradigm for synchronization phenomena."

---

## 7. Glossary of Geometric Mechanics
- **Bivector ($\Omega$ / $B$):** An oriented area element. In 2D, it represents the plane of rotation. Mathematically, it is the outer product of two vectors.
- **Rotor ($R$):** An operator that performs a rotation via the "sandwich product" $v' = R v \tilde{R}$. It generalizes complex numbers and quaternions.
- **Wedge Product ($\wedge$):** The operation that creates a bivector from two vectors. It captures the "directed area" between them.
- **Lie Algebra ($\mathfrak{spin}(n)$):** The tangent space at the identity of the rotor group, isomorphic to the space of 2-blades (bivectors) $\bigwedge^2 \mathbb{R}^n$.
- **FSAL (First-Same-As-Last):** An optimization in embedded Runge-Kutta methods where the final stage of an accepted step is reused as the initial stage of the next step.
- **Order Parameter ($R$):** A measure of how synchronized a system is ($R=0$ for random, $R=1$ for perfect alignment).
- **Manifold:** The space where the oscillators live. For Kuramoto, this is the $S^1$ circle. For Lohe, it is the $S^2$ sphere.
- **Hamiltonian ($H$):** A scalar function representing the total energy of a system. Synchronization transitions are often viewed as "energy minimizing" trajectories.

---

## 8. Dash App Bridge Protocol
The `kuramoto-dash-app` can ingest pre-computed simulation data from this suite. Two export options are available:

### 8.1 Legacy Export (scripts/export_to_dash.py)
The `scripts/export_to_dash.py` script converts `.npz` files to JSON with basic fields.
- **Data Format**: `JSON` (orient='split') containing metadata and a structured data frame.
- **Fields**: `time`, `node_i` (phases), `order_parameter`.

### 8.2 Enhanced Export (kuramoto dash-export)
The `kuramoto dash-export` CLI subcommand runs a simulation and exports enriched JSON in one step:

```bash
kuramoto dash-export -n 50 -k 1.5 -t 200 --topology small_world -o data/dash_export.json
```

**Enhanced JSON Schema:**

```json
{
  "metadata": {
    "n_oscillators": 50,
    "timesteps": 200,
    "coupling": 1.5,
    "noise_std": 0.0,
    "solver": "rk45",
    "dt": 0.05,
    "topology_type": "small_world",
    "topology_stats": {
      "num_nodes": 50,
      "num_edges": 100,
      "density": 0.082,
      "avg_degree": 4.0
    },
    "solver_params": {
      "dt": 0.05,
      "noise_std": 0.0,
      "locking_threshold": 0.1,
      "locking_window": 10
    }
  },
  "data": {
    "columns": ["time", "node_0", ..., "node_49", "order_parameter", "mean_field_phase", "locking_fraction"],
    "data": [[...], ...]
  }
}
```

**New Fields:**
- **`mean_field_phase`** (ψ(t)): The collective phase angle of the oscillator population, computed as `arg(mean(exp(i·θ)))`. Complements R(t) by showing the direction of synchronization.
- **`locking_fraction`**: The fraction of oscillators whose instantaneous frequency is locked to the mean frequency (within a threshold over a sliding window). Values range from 0 (no locking) to 1 (all oscillators phase-locked).
- **`topology_stats`**: Network graph metrics (node count, edge count, density, average degree) derived from the adjacency matrix.
- **`solver_params`**: Simulation parameters (dt, noise, locking detection thresholds) for reproducibility.

**Loading in Dash:**
```python
import json
import pandas as pd

with open("data/dash_export.json") as f:
    exported = json.load(f)

metadata = exported["metadata"]
df = pd.DataFrame(exported["data"]["data"], columns=exported["data"]["columns"])
```

The `data` field uses `orient='split'` for backward compatibility with the existing Dash app.

---
*Created by Eigenscribe & Junie*
