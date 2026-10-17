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

## 4. Numerical Analysis for Nonlinear Systems
### 4.1 Stability
Numerical stability refers to the property that errors do not grow exponentially over time. For the Kuramoto model, the step size $\Delta t$ must be small enough to resolve the fastest oscillations (the high-frequency natural frequencies $\omega_i$) and the strongest coupling $K$.
A rule of thumb for Euler-like methods is $\Delta t < 2 / (K + \max|\omega_i|)$.

### 4.2 Consistency
A method is **consistent** if the local truncation error goes to zero as $\Delta t \to 0$. The `RotorSolver`'s geometric update is first-order consistent in time, but zeroth-order consistent with the unit-norm constraint (meaning it preserves the constraint exactly, which is a significant advantage over phase-based methods that might suffer from numerical drift if converted to vectors).

### 4.3 Convergence (Lax Equivalence Theorem)
For linear problems, the Lax Equivalence Theorem states that **Consistency + Stability = Convergence**. For nonlinear systems like Kuramoto, convergence is generally guaranteed if the vector field is Lipschitz continuous and the method is stable and consistent. Our benchmarks against RK45 confirm that the GA rotor solver converges to the physical ground truth.

---

## 4. Key Sources & Citations
- **Kuramoto (1975)**: "Self-entrainment of a population of coupled non-linear oscillators."
- **Lohe (2009)**: "Non-abelian Kuramoto models and synchronization."
- **Doran & Lasenby (2003)**: "Geometric Algebra for Physicists." (Standard GA reference).
- **Acebrón et al. (2005)**: "The Kuramoto model: A simple paradigm for synchronization phenomena."

---

## 5. Glossary of Geometric Mechanics
- **Bivector ($\Omega$ / $B$):** An oriented area element. In 2D, it represents the plane of rotation. Mathematically, it is the outer product of two vectors.
- **Rotor ($R$):** An operator that performs a rotation via the "sandwich product" $v' = R v \tilde{R}$. It generalizes complex numbers and quaternions.
- **Wedge Product ($\wedge$):** The operation that creates a bivector from two vectors. It captures the "directed area" between them.
- **Order Parameter ($R$):** A measure of how synchronized a system is ($R=0$ for random, $R=1$ for perfect alignment).
- **Manifold:** The space where the oscillators live. For Kuramoto, this is the $S^1$ circle. For Lohe, it is the $S^2$ sphere.
- **Hamiltonian ($H$):** A scalar function representing the total energy of a system. Synchronization transitions are often viewed as "energy minimizing" trajectories.

---

## 6. Dash App Bridge Protocol
The `kuramoto-dash-app` can ingest pre-computed simulation data from this suite using the `export_to_dash.py` utility.
- **Data Format**: `JSON` (orient='split') containing metadata and a structured data frame.
- **Fields**: `time`, `node_i` (phases), `order_parameter`.
- **Integration**: To load data into Dash, use `pd.read_json(path, orient='split')` on the `data` field of the exported JSON.

---
*Created by Eigenscribe & Junie*
