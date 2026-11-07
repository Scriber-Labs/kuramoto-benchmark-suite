# ✍️ Practice Problems: Geometric Synchronization, Number Theory & Visualization
*Mastering the foundations of the Kuramoto Benchmark Suite*

> ⚠️ **AI-GENERATED CONTENT NOTICE:** This practice problem set was generated with the assistance of an AI (Junie).
> **Last Updated:** October 2026 — Expanded with Bézout identity, plotting exercises, and canonical derivation problems.

---

## 📚 How to Use This Document

1. **Attempt each problem on paper first** — derive the answer before checking the solution.
2. **For plotting problems**, open a Jupyter notebook and run the code yourself. Change the parameters and observe what happens.
3. **For code-reference problems**, actually open the referenced file and read the implementation. Don't just trust the problem statement.
4. **Track your progress** — mark each problem with `[ ]` (not started), `[~]` (in progress), or `[x]` (completed).

## Problem 1: The 2D Rotor Sandwich
**Goal:** Apply a rotor to a vector $\mathbf{v}=\mathbf{e}_1$.

**Setup:** Consider an orthonormal set of basis vectors $\{\mathbf{e}_1, \mathbf{e}_2\}$ and a rotor 
$R=\exp(-B \theta / 2)$ where $B=\mathbf{e}_1 \wedge \mathbf{e}_2$. 

**Tasks:**
1. Write out the expression for the rotated vector $\mathbf{v}'$.
2. Calculate the components of $\mathbf{v}'$.

**Reference:** See how this is implemented in `RotorSolver._random_rotors` in `../src/kuramoto/solvers/rotor.py`.


## Problem 2: The Bivector Torque
**Goal**: Compute the interaction torque.
Given two oscillators with orientations $v_1 = e_1$ and $v_2 = e_2$:
1. Compute the wedge product $\Omega = v_1 \wedge v_2$.
2. If $K=1$, what is the bivector torque $\Omega_{int}$ acting on oscillator 1?
3. **Reference**: Look at `step_euler_geometric` in `../src/kuramoto/solvers/rotor.py` for the code implementation of this wedge product.

## Problem 3: Order Parameter $R$
**Goal**: Calculate macroscopic synchronization.
You have 3 oscillators with phases $\theta = [0, \pi/4, \pi/2]$.
1. Calculate the complex order parameter $Z = \frac{1}{N} \sum e^{i\theta_j}$.
2. Find the synchronization strength $R = |Z|$.
3. **Reference**: Check `compute_order_parameter` in `../src/kuramoto/order_parameter.py`.

## Problem 4: The Quantum Phase Gate
**Goal**: Link classical dynamics to quantum gates.
In our "Quantum Bridge," we map a rotor step $\Delta \theta$ to an $R_z(\phi)$ gate.
1. If an oscillator has $\omega = 1.0$, $K=0$, and $\Delta t = 0.1$, what is the required $R_z$ gate angle $\phi$?
2. Why does the circuit depth remain $O(1)$ regardless of $N$?
3. **Reference**: See `LEARNING_GUIDE.md` Section 3.2.

## Problem 5: Bivector to Matrix
**Goal**: Bridge GA with standard Linear Algebra.
A bivector $B = \Omega e_{12}$ in 2D can be represented as a skew-symmetric matrix.
1. Write the $2 \times 2$ matrix corresponding to $B$.
2. How does the matrix exponential $\exp(M)$ relate to the rotor exponential $\exp(B)$?

## Problem 6: The Nyquist Limit
**Goal**: Prevent aliasing in simulations.
Given $\Delta t = 0.1$:
1. What is the maximum resolvable natural frequency $\omega_{max}$ (Nyquist limit)?
2. What happens to the simulation if $\omega_i > \omega_{max}$?
3. **Reference**: See `RotorSolver.simulate` logic in `../src/kuramoto/solvers/rotor.py`.

## Problem 7: Hamiltonian Energy
**Goal**: Understand conserved quantities.
The Kuramoto model has a conserved quantity (Hamiltonian) when $\omega_i = 0$.
1. Write the expression for the system energy $H$.
2. Why is the GA Rotor solver better at preserving this energy than standard Euler?

## Problem 8: The Lohe $S^2$ Extension
**Goal**: Generalizing to 3D.
In 3D, a rotor is represented by 4 coefficients (like a quaternion).
1. Why can't we use a single complex number to represent a 3D orientation?
2. **Reference**: See the `dim=3` logic in `../src/kuramoto/solvers/rotor.py`.

## Problem 9: Vectorized Speedup
**Goal**: Computational complexity.
Why is $O(N)$ better than $O(N^2)$ for $N=10,000$?
1. Calculate the number of operations for both for a single step.
2. **Reference**: See the `BENCHMARK_RUNDOWN.md` results.

## Problem 10: Symmetry Invariance
**Goal**: Proving Noether's Theorem.
Show that shifting all phases $\theta_i \to \theta_i + \alpha$ does not change the Kuramoto equations.
1. Apply the shift to the $\sin(\theta_j - \theta_i)$ term.
2. What physical "charge" corresponds to this $U(1)$ symmetry?

---

## 📐 Section B: Canonical Derivation (From First Principles)

These problems guide you through deriving the Kuramoto model from physical assumptions. Work through them on paper.

## Problem 13: Deriving the Coupling Term

**Goal:** Understand where the sine coupling comes from.

**Setup:** Consider a population of oscillators. Each oscillator $i$ has a phase $\theta_i$ and natural frequency $\omega_i$. Without coupling, the dynamics are simply $\dot{\theta}_i = \omega_i$.

**Tasks:**
1. Assume the coupling between oscillators depends only on their phase difference: $\dot{\theta}_i = \omega_i + \sum_j H(\theta_j - \theta_i)$, where $H$ is some interaction function.
2. Argue why $H$ must be an **odd function** (i.e., $H(-x) = -H(x)$). Hint: Think about what happens when oscillator $j$ is "ahead" vs "behind" oscillator $i$.
3. Show that the simplest nontrivial odd, $2\pi$-periodic function is $H(x) = K \sin(x)$.
4. **Conclusion:** This recovers the standard Kuramoto coupling term.

## Problem 14: The Mean-Field Reduction

**Goal:** Derive the order parameter equation for all-to-all coupling.

**Setup:** The full Kuramoto equation with all-to-all coupling is:
$$\dot{\theta}_i = \omega_i + \frac{K}{N} \sum_{j=1}^N \sin(\theta_j - \theta_i)$$

**Tasks:**
1. Use the trigonometric identity $\sin(\theta_j - \theta_i) = \sin(\theta_j)\cos(\theta_i) - \cos(\theta_j)\sin(\theta_i)$ to expand the sum.
2. Define the complex order parameter $Z(t) = R(t)e^{i\psi(t)} = \frac{1}{N}\sum_{j=1}^N e^{i\theta_j}$.
3. Show that the equation reduces to:
$$\dot{\theta}_i = \omega_i - K R(t) \sin(\theta_i - \psi(t))$$
4. **Physical interpretation:** What does this equation tell you about how each oscillator "sees" the rest of the population?

## Problem 15: Critical Coupling Threshold (Adler's Formula)

**Goal:** Understand the synchronization transition.

**Setup:** Assume the natural frequencies $\omega_i$ are drawn from a symmetric distribution $g(\omega)$ (e.g., a Lorentzian or Gaussian).

**Tasks:**
1. In the incoherent state ($R \approx 0$), oscillators rotate at their natural frequencies. In the partially synchronized state, a fraction of oscillators "lock" to the mean field.
2. For a Lorentzian distribution $g(\omega) = \frac{1}{\pi} \frac{D}{(\omega - \omega_0)^2 + D^2}$, the critical coupling is $K_c = 2D / g(\omega_0)$.
3. Calculate $K_c$ for $D = 0.5$ and $\omega_0 = 0$.
4. **Plotting task:** Write a short Python script that generates natural frequencies from this Lorentzian distribution and runs a simulation for $K = K_c - 0.1$, $K = K_c$, and $K = K_c + 0.1$. Plot the order parameter $R(t)$ for all three cases on the same graph.
5. **Reference:** Use `kuramoto.analysis.viz.plot_order_parameter` for the visualization.

---

## 🔢 Section C: Number Theory — Bézout's Identity & Coprime Sampling

Your codebase uses coprime sampling to reduce memory from $O(MN)$ to $O(M+N)$. These problems build the mathematical foundation.

## Problem 16: Bézout's Identity by Hand

**Goal:** Compute Bézout coefficients manually.

**Setup:** Bézout's identity states that for any integers $a, b$, there exist integers $x, y$ such that:
$$ax + by = \gcd(a, b)$$

**Tasks:**
1. Use the extended Euclidean algorithm to find $\gcd(7, 11)$ and the Bézout coefficients $(x, y)$.
2. Verify your answer: does $7x + 11y = 1$?
3. Now find $\gcd(6, 9)$ and the Bézout coefficients. What do you notice about the result?
4. **Code reference:** Open `src/kuramoto/solvers/coprime.py` and locate the `extended_gcd` function. Trace through the recursive calls for inputs $(7, 11)$ and verify your hand calculation matches.

## Problem 17: Chinese Remainder Theorem (CRT) Reconstruction

**Goal:** Understand how two coprime samplers reconstruct the full signal.

**Setup:** You have two samplers: Sampler A records every $N=11$-th step, Sampler B records every $M=7$-th step. Since $\gcd(7, 11) = 1$, you can reconstruct any time index $t \in [0, 76]$ from the pair of remainders $(t \bmod 7, t \bmod 11)$.

**Tasks:**
1. Suppose Sampler A observes the signal at local index $k_n = 5$ (meaning $t \equiv 5 \pmod{11}$) and Sampler B observes at local index $k_m = 3$ (meaning $t \equiv 3 \pmod{7}$).
2. Use the Bézout coefficients from Problem 16 to reconstruct $t$.
3. Verify: does $t \bmod 11 = 5$ and $t \bmod 7 = 3$?
4. **Code reference:** Look at `coprime_reconstruct_frequency` in `coprime.py`. The formula is:
$$k_{\text{true}} = (k_m \cdot b \cdot N + k_n \cdot a \cdot M) \bmod (M \cdot N)$$
where $(g, a, b) = \text{extended\_gcd}(M, N)$.

## Problem 18: Why Coprime Matters

**Goal:** Understand what breaks when samplers are not coprime.

**Tasks:**
1. Suppose you choose $M = 6$ and $N = 9$. Compute $\gcd(6, 9)$.
2. Show that there exist time indices $t_1 \neq t_2$ in $[0, 53]$ such that $t_1 \equiv t_2 \pmod{6}$ and $t_1 \equiv t_2 \pmod{9}$. This means you cannot uniquely reconstruct the time index.
3. **Code reference:** Run `extended_gcd(6, 9)` and observe the error when you try `coprime_reconstruct_frequency` with non-coprime strides.

## Problem 18b: Positive Rotor Composition (Forward-Only Operations)

**Goal:** Investigate whether two discrete rotations can generate a finer composite rotation using positive integer powers only (forward operations without inverse rotations).

**Setup:** Consider two discrete generator rotors in the geometric algebra plane $B = \mathbf{e}_1 \wedge \mathbf{e}_2$:
$$R_m = \exp\left(-\frac{B\pi}{m}\right), \qquad R_n = \exp\left(-\frac{B\pi}{n}\right)$$
Assume $m, n > 1$ with $\gcd(m, n) = 1$. We wish to construct the fine rotation:
$$R\left(\frac{2\pi}{mn}\right) = \exp\left(-\frac{B\pi}{mn}\right)$$
Under rotor composition with powers $x, y \in \mathbb{Z}$:
$$R_m^x R_n^y = \exp\left(-B\left(\frac{x\pi}{m} + \frac{y\pi}{n}\right)\right)$$

**Tasks:**
1. **The Ordinary Bézout Barrier:** Show that matching the rotation exponent directly requires $\frac{x}{m} + \frac{y}{n} = \frac{1}{mn}$, which simplifies to the linear Diophantine equation $nx + my = 1$. Prove that if $x, y \in \mathbb{Z}_{>0}$ (strictly positive integers), no solutions exist for $m, n > 1$. Explain why standard Bézout solutions necessarily require inverse rotations (negative powers).
2. **Periodic Modular Wrapping:** Using the $2\pi$-periodicity of physical rotations ($R(\theta + 2\pi) = R(\theta)$), show that the composite exponent only needs to satisfy $\frac{x}{m} + \frac{y}{n} = \frac{1}{mn} + k$ for an integer $k \ge 1$. Deduce the modified Diophantine equation:
$$nx + my = 1 + kmn$$
3. **Concrete Construction for $m=7, n=11$:** Set $k=1$ and solve $11x + 7y = 78$. Find a pair of strictly positive integers $(x, y) \in \mathbb{Z}_{>0}^2$ satisfying this relation.
4. **Rotor Verification:** Explicitly verify that $R(2\pi/77) = R_7^2 R_{11}^8$. Show how the extra full revolution ($2\pi$) disappears in the resulting physical rotation.
5. **Gate Count vs. Computational Efficiency:** Investigate what happens to the solution $(x, y)$ if you choose $k=2$ ($11x + 7y = 155$). Contrast mathematical existence with operational gate depth (total applications $x + y$).
6. **Bonus Proof (Universal Positive Solvability):** Prove that for any coprime integers $m, n > 1$, there always exists an integer $k \ge 1$ such that $nx + my = 1 + kmn$ admits strictly positive integer solutions $x, y > 0$. *(Hint: Express general integer solutions to $nx + my = 1$ and add sufficient periods $mn$).*

**Physical & Algorithmic Context:** In physical implementations (such as quantum phase gate synthesis without inverse gate overhead, forward-only numerical ODE stepping, or non-reversible actuator dynamics), mathematical reversibility does not imply operational accessibility. Modular wrapping provides a mechanism to realize exact transformations strictly through forward evolution.

---

## 📊 Section D: Plotting & Visualization Exercises

These problems require you to write code, run simulations, and produce plots. The goal is to internalize what synchronization **looks like**.

## Problem 19: Phase Portrait — Incoherent vs Synchronized

**Goal:** Visualize the difference between incoherent and synchronized states.

**Tasks:**
1. Run a Kuramoto simulation with $N=50$ oscillators, $K=0.1$ (weak coupling), and $T=10$ seconds.
2. Run the same simulation with $K=3.0$ (strong coupling).
3. For each case, plot the phases $\theta_i(t)$ as a function of time (a "phase portrait" or "spaghetti plot").
4. **Plotting task:** Use `kuramoto.analysis.viz.plot_time_series` to create both plots side by side.
5. **Question:** What visual features distinguish the synchronized state from the incoherent state?

## Problem 20: Order Parameter Dynamics

**Goal:** Track how synchronization emerges over time.

**Tasks:**
1. Run a simulation with $N=100$ oscillators, natural frequencies drawn uniformly from $[-1, 1]$, coupling $K=2.0$, and $T=20$ seconds.
2. Compute the order parameter $R(t)$ at each timestep.
3. **Plotting task:** Use `kuramoto.analysis.viz.plot_order_parameter` to plot $R(t)$.
4. **Question:** Does $R(t)$ approach a steady state? What is the final synchronization strength? How does it change if you increase $K$ to $4.0$?

## Problem 21: Natural Frequency Distribution

**Goal:** Visualize how frequency spread affects synchronization.

**Tasks:**
1. Generate two sets of natural frequencies:
   - Set A: Uniform distribution on $[-0.5, 0.5]$ (narrow spread)
   - Set B: Uniform distribution on $[-2.0, 2.0]$ (wide spread)
2. Run simulations with the same coupling $K=1.5$ for both sets.
3. **Plotting task:** Use `kuramoto.analysis.viz.plot_distributions` to plot the frequency distributions, and `plot_order_parameter` to compare $R(t)$ for both cases.
4. **Question:** Which distribution achieves higher synchronization? Why?

## Problem 22: Network Topology Visualization

**Goal:** See how network structure affects coupling.

**Tasks:**
1. Generate a ring topology with $N=20$ nodes and a small-world topology with $N=20$ nodes.
2. **Plotting task:** Use `kuramoto.analysis.viz.plot_network` to visualize both topologies.
3. Run Kuramoto simulations on both topologies with the same coupling strength.
4. **Question:** Which topology synchronizes faster? Does the network structure matter for the final synchronization strength?

## Problem 23: Bifurcation Diagram (Advanced)

**Goal:** Create a bifurcation diagram showing the synchronization transition.

**Tasks:**
1. Sweep the coupling strength $K$ from $0.1$ to $5.0$ in steps of $0.05$.
2. For each $K$, run a simulation for $T=50$ seconds and record the final (steady-state) order parameter $R_{\text{final}}$.
3. **Plotting task:** Plot $K$ on the x-axis and $R_{\text{final}}$ on the y-axis. This is your bifurcation diagram.
4. **Question:** Where does the sharp transition from $R \approx 0$ to $R > 0$ occur? Does it match the theoretical critical coupling $K_c$?

## Problem 24: Fluid Vorticity Visualization

**Goal:** Connect the bivector torque to fluid flow visualization.

**Tasks:**
1. Run a simulation with $N=30$ oscillators and moderate coupling $K=1.5$.
2. At a single snapshot in time, extract the phases and natural frequencies.
3. **Plotting task:** Use `kuramoto.analysis.viz.plot_fluid_vorticity` to visualize the bivector torque field.
4. **Question:** Do you see "vortex-like" structures where oscillators cluster? How does the flow field change as the system approaches synchronization?

---

## 🔍 Section E: Repo Scavenger Hunt

These tasks connect the math to the actual codebase. Complete them to build confidence in reading and understanding the implementation.

## Problem 25: Find the Rotor Update Rule

**Goal:** Locate and understand the core rotor evolution equation.

**Tasks:**
1. Open `src/kuramoto/solvers/rotor.py`.
2. Find the function that implements the rotor update $R(t+\Delta t) = \exp(-\frac{1}{2}\Omega \Delta t) R(t)$.
3. Trace through the code: how is the bivector $\Omega$ computed? Where does the coupling term appear?
4. **Question:** Does the code match the equation in the preprint (`RESEARCH_PREPRINT.md`, Section 2.3)?

## Problem 26: Trace the Order Parameter Calculation

**Goal:** Understand how $R(t)$ is computed from phases.

**Tasks:**
1. Open `src/kuramoto/order_parameter.py`.
2. Find the `compute_order_parameter` function.
3. Read the implementation: how does it convert phases $\theta_i$ to the complex order parameter $Z$?
4. **Question:** Does the code use $e^{i\theta}$ or $\cos(\theta) + i\sin(\theta)$? Are they equivalent?

## Problem 27: Find the SCF (Self-Consistent Field) Optimization

**Goal:** Locate the $O(N)$ mean-field optimization.

**Tasks:**
1. Open `src/kuramoto/solvers/rotor.py`.
2. Find the method or function that computes the mean field vector $\mathbf{u}_{\text{mean}}$ once per timestep.
3. Compare it with the pairwise $O(N^2)$ method.
4. **Question:** How many lines of code save the $O(N^2)$ computation? What's the key insight?

## Problem 28: Locate the U(1) Symmetry Check

**Goal:** Find how gauge invariance is verified.

**Tasks:**
1. Open `src/kuramoto/order_parameter.py`.
2. Find the function that checks global phase invariance (shifting all phases by a constant $\phi$).
3. Read the implementation: what metric is compared before and after the shift?
4. **Question:** Why is this check important for validating the solver?

---

## Problem 11: Runge-Kutta Munthe-Kaas (RKMK4) on Lie Algebras
**Goal**: Understand why RKMK4 avoids manifold drift.
Given a rotor differential equation $\dot{R} = -\frac{1}{2}\Omega(R) R$:
1. If standard RK4 updates $R_{\text{next}} = R_0 + \Delta t \sum b_i k_i$, why does $R_{\text{next}}$ violate $\|R_{\text{next}}\|=1$?
2. How does RKMK4 restore exact unit-norm invariant conservation by evaluating stages on the Lie algebra $\mathfrak{spin}(n)$?
3. **Reference**: See `step_rkmk4` in `../src/kuramoto/solvers/rotor.py`.

## Problem 12: Dormand-Prince FSAL & Adaptive Scaling
**Goal**: Analyze embedded error estimation and FSAL efficiency.
In the Dormand-Prince 5(4) integrator (DOPRI54):
1. What does FSAL (First-Same-As-Last) mean, and how many bivector field evaluations are saved per accepted step?
2. If the local truncation error estimate is $\text{LTE} = 10^{-10}$ and the target tolerance is $\text{tol} = 10^{-8}$, what is the proposed step-size scale factor $s$ using 5th-order scaling?
3. **Reference**: See `step_adaptive_dopri54` in `../src/kuramoto/solvers/rotor.py`.

---

# ✅ Solutions

### Solution 1
1. $v' = R e_1 \tilde{R}$.
2. $R = \cos(\pi/4) - (e_1 \wedge e_2) \sin(\pi/4) = \frac{\sqrt{2}}{2}(1 - e_{12})$.
   $v' = \frac{1}{2}(1 - e_{12}) e_1 (1 + e_{12}) = e_2$. (A $90^\circ$ rotation).

### Solution 2
1. $\Omega = e_1 \wedge e_2 = e_{12}$.
2. $\Omega_{int} = K (v_2 \wedge v_1) = 1 (e_2 \wedge e_1) = -e_{12}$. (The torque pulls $v_1$ toward $v_2$).

### Solution 3
1. $Z = \frac{1}{3} (e^{i0} + e^{i\pi/4} + e^{i\pi/2}) \approx 0.57 + 0.57i$.
2. $R \approx 0.81$.

### Solution 4
1. $\phi = \omega \Delta t = 1.0 \times 0.1 = 0.1$ radians.
2. Because the SCF approximation allows all $N$ qubits to be updated with parallel single-qubit gates simultaneously.

### Solution 5
1. $M = \begin{pmatrix} 0 & -\Omega \\ \Omega & 0 \end{pmatrix}$.
2. They are identical maps; $\exp(B)$ in GA is the algebraic equivalent of the matrix exponential of a skew-symmetric matrix.

### Solution 6
1. $\omega_{max} = \pi / \Delta t = 10\pi \approx 31.4$.
2. Aliasing occurs: the oscillator appears to rotate backwards or at the wrong speed, leading to numerical artifacts.

### Solution 7
1. $H = -\sum \sum A_{ij} \cos(\theta_j - \theta_i)$.
2. Because GA rotors use exact exponential maps which are "symplectic-like" in preserving the orientation on the manifold.

### Solution 8
1. 3D space requires two independent planes of rotation to reach any point on the sphere, whereas a complex number only describes one plane ($e_{12}$).

### Solution 9
1. For $N=10^4$: $O(N) = 10^4$ operations. $O(N^2) = 10^8$ operations. The $O(N)$ solver is **10,000 times faster**.

### Solution 10
1. $\sin((\theta_j + \alpha) - (\theta_i + \alpha)) = \sin(\theta_j - \theta_i)$. The shift cancels out.
2. The conservation of total phase (or the "Total Momentum" of the ensemble).

### Solution 11
1. Linear addition in Euclidean space does not preserve the quadratic constraint $\|R\|^2 = 1$; the sum of unit vectors/rotors generally lies outside the unit hypersphere.
2. RKMK4 evaluates velocity stages $\omega_i \in \mathfrak{spin}(n)$ (bivectors) and applies the Lie group exponential map $\exp(-\frac{\Delta t}{2} \omega_{\text{eff}} B)$, which is analytically guaranteed to lie strictly in $\operatorname{Spin}(n)$ with $\|R\|=1$ to machine precision ($10^{-16}$).

### Solution 12
1. FSAL means the 7th stage velocity $\omega_7 = \Omega(y_5)$ computed at the accepted 5th-order state $y_5$ is identical to the 1st stage velocity $\omega_1$ of the next step. Reusing $\omega_7$ as $\omega_1$ saves 1 full bivector torque evaluation per accepted step (reducing cost from 7 to 6 evaluations).
2. For order $p=5$, $s = 0.9 \times (\text{tol} / \text{LTE})^{1/5} = 0.9 \times (10^{-8} / 10^{-10})^{1/5} = 0.9 \times (100)^{0.2} \approx 0.9 \times 2.512 = 2.26$. The step size $\Delta t$ can safely increase by $\approx 2.26\times$.

---

## ✅ Solutions — Section B: Canonical Derivation

### Solution 13 (Deriving the Coupling Term)
1. The coupling depends on phase difference: $\dot{\theta}_i = \omega_i + \sum_j H(\theta_j - \theta_i)$.
2. If oscillator $j$ is ahead of $i$ by $\delta$, then $i$ should be pulled forward (positive contribution). If $j$ is behind by $\delta$, $i$ should be pulled backward (negative contribution). This means $H(-\delta) = -H(\delta)$, so $H$ is odd.
3. The Taylor expansion of an odd, $2\pi$-periodic function starts with the sine term: $H(x) = c_1 \sin(x) + c_3 \sin(3x) + \cdots$. The simplest nontrivial choice is $H(x) = K \sin(x)$.

### Solution 14 (Mean-Field Reduction)
1. $\sum_j \sin(\theta_j - \theta_i) = \sum_j [\sin(\theta_j)\cos(\theta_i) - \cos(\theta_j)\sin(\theta_i)] = \cos(\theta_i)\sum_j \sin(\theta_j) - \sin(\theta_i)\sum_j \cos(\theta_j)$.
2. $Z = \frac{1}{N}\sum e^{i\theta_j} = \frac{1}{N}\sum[\cos(\theta_j) + i\sin(\theta_j)] = R\cos(\psi) + iR\sin(\psi)$.
3. Substituting: $\sum_j \sin(\theta_j - \theta_i) = N[R\sin(\psi)\cos(\theta_i) - R\cos(\psi)\sin(\theta_i)] = -NR\sin(\theta_i - \psi)$. This gives $\dot{\theta}_i = \omega_i - KR\sin(\theta_i - \psi)$.
4. Each oscillator sees the entire population as a single "mean field" with strength $R$ and phase $\psi$. The $O(N^2)$ pairwise interactions collapse to an $O(1)$ effective force.

### Solution 15 (Critical Coupling)
1. For a Lorentzian with width $D=0.5$ centered at $\omega_0=0$: $g(0) = \frac{1}{\pi} \frac{0.5}{0 + 0.25} = \frac{1}{\pi/2} = \frac{2}{\pi}$.
2. $K_c = \frac{2D}{g(\omega_0)} = \frac{1}{2/\pi} = \frac{\pi}{2} \approx 1.57$.
3. **Plotting task:** Your plot should show $R(t) \to 0$ for $K < K_c$, a slow growth for $K \approx K_c$, and rapid convergence to $R > 0$ for $K > K_c$.

---

## ✅ Solutions — Section C: Number Theory

### Solution 16 (Bézout's Identity)
1. Extended Euclidean algorithm for $(7, 11)$:
   - $11 = 1 \cdot 7 + 4$
   - $7 = 1 \cdot 4 + 3$
   - $4 = 1 \cdot 3 + 1$
   - Back-substitution: $1 = 4 - 3 = 4 - (7 - 4) = 2 \cdot 4 - 7 = 2(11 - 7) - 7 = 2 \cdot 11 - 3 \cdot 7$
   - So $\gcd(7, 11) = 1$, with $x = -3$ and $y = 2$.
2. Verification: $7(-3) + 11(2) = -21 + 22 = 1$. ✓
3. For $(6, 9)$: $\gcd(6, 9) = 3$, with $6(-1) + 9(1) = 3$. The gcd is not 1, so 6 and 9 are not coprime.
4. The code in `coprime.py` implements this recursively.

### Solution 17 (CRT Reconstruction)
1. From Problem 16: $a = -3$, $b = 2$ for $\gcd(7, 11) = 1$.
2. $k_{\text{true}} = (k_m \cdot b \cdot N + k_n \cdot a \cdot M) \bmod (M \cdot N) = (3 \cdot 2 \cdot 11 + 5 \cdot (-3) \cdot 7) \bmod 77 = (66 - 105) \bmod 77 = (-39) \bmod 77 = 38$.
3. Verification: $38 \bmod 11 = 5$ ✓, $38 \bmod 7 = 3$ ✓.

### Solution 18 (Why Coprime Matters)
1. $\gcd(6, 9) = 3 \neq 1$.
2. For example, $t_1 = 0$ and $t_2 = 18$: $0 \equiv 18 \pmod{6}$ (both give 0) and $0 \equiv 18 \pmod{9}$ (both give 0). You cannot distinguish $t=0$ from $t=18$.
3. The code raises `ValueError` when `gcd(M, N) != 1`.

### Solution 18b (Positive Rotor Composition & Forward-Only Operations)
1. **The Ordinary Bézout Barrier:**
   Matching the exponent directly gives $\frac{x}{m} + \frac{y}{n} = \frac{1}{mn} \implies nx + my = 1$.
   If $x, y \in \mathbb{Z}_{>0}$, then $x \ge 1$ and $y \ge 1$.
   Since $m, n > 1$, the lower bound is $nx + my \ge n(1) + m(1) = n + m > 1$ (for $m=7, n=11$, $11x + 7y \ge 18 > 1$).
   Hence, no strictly positive integer solutions exist for $nx + my = 1$. Unrestricted Bézout solutions necessarily contain negative coefficients (e.g., $11(2) + 7(-3) = 1$ or $11(-5) + 7(8) = 1$), which correspond to inverse rotor operations $R^{-1}$. When physical or algorithmic constraints forbid backwards rotations, unrestricted Bézout cannot be implemented directly.

2. **Periodic Modular Wrapping:**
   Physical vector rotations satisfy $R(\theta + 2\pi) = R(\theta)$ (a full $2\pi$ rotation is the identity on vectors).
   Therefore, we only require the composite exponent to equal the target angle plus an integer number of full revolutions:
   $$\frac{x}{m} + \frac{y}{n} = \frac{1}{mn} + k \quad (k \in \mathbb{Z})$$
   Multiplying through by $mn$ gives the Diophantine equation:
   $$nx + my = 1 + kmn$$

3. **Solving for $m=7, n=11$ with $k=1$:**
   For $k=1$, $1 + 77(1) = 78$, giving $11x + 7y = 78$.
   - For $x=1$: $11(1) + 7y = 78 \implies 7y = 67$ (no integer solution).
   - For $x=2$: $11(2) + 7y = 78 \implies 22 + 7y = 78 \implies 7y = 56 \implies y = 8$.
   Both $x=2$ and $y=8$ are strictly positive integers ($x, y \in \mathbb{Z}_{>0}$).

4. **Rotor Verification:**
   $$R_7^2 R_{11}^8 = \exp\left(-B\left(\frac{2\pi}{7} + \frac{8\pi}{11}\right)\right) = \exp\left(-B\frac{22 + 56}{77}\pi\right) = \exp\left(-B\frac{78\pi}{77}\right) = \exp\left(-B\left(\pi + \frac{\pi}{77}\right)\right)$$
   Under the rotor sandwich product $v' = R v \tilde{R}$, the factor $\exp(-B\pi) = -1$ appears on both sides:
   $$v' = (-R(2\pi/77)) v (-\tilde{R}(2\pi/77)) = R(2\pi/77) v \tilde{R}(2\pi/77)$$
   The extra half-rotor period (full $2\pi$ spatial turn) leaves the physical orientation invariant, yielding the exact rotation $R(2\pi/77)$.

5. **Gate Count vs. Computational Efficiency:**
   For $k=1$, the total gate applications are $x + y = 2 + 8 = 10$.
   For $k=2$, $11x + 7y = 155$:
   - Solution branch A: $x=2, y=19 \implies x + y = 21$ gates.
   - Solution branch B: $x=9, y=8 \implies x + y = 17$ gates.
   Although higher $k$ provides additional positive integer branches, the total number of operations increases. In quantum circuit compilation and numerical integration, one must minimize $x + y$ across admissible $k$ to avoid unnecessary circuit depth or accumulated numerical round-off.

6. **Bonus Proof (Universal Positive Solvability):**
   Let $\gcd(m, n) = 1$ with $m, n > 1$. By the extended Euclidean algorithm, there exists a base integer solution $(x_0, y_0)$ to $nx_0 + my_0 = 1$.
   Now consider $nx + my = 1 + kmn$.
   Decompose $k = k_1 + k_2$ with $k_1, k_2 \in \mathbb{Z}$. Then:
   $$n(x_0 + k_1 m) + m(y_0 + k_2 n) = (nx_0 + my_0) + (k_1 + k_2)mn = 1 + kmn$$
   We set $x = x_0 + k_1 m$ and $y = y_0 + k_2 n$.
   Since $m, n > 1$, we can always choose integers $k_1 > -x_0 / m$ and $k_2 > -y_0 / n$.
   This guarantees $x = x_0 + k_1 m \ge 1$ and $y = y_0 + k_2 n \ge 1$.
   Setting $k = k_1 + k_2$ yields a valid $k \ge 1$ where both $x$ and $y$ are strictly positive integers.

---

## ✅ Solutions — Section D: Plotting Exercises

### Solutions 19-24
These are hands-on coding exercises. The expected outcomes are:

**Problem 19:** For $K=0.1$, phases diverge (spaghetti plot). For $K=3.0$, phases lock together and move in parallel.

**Problem 20:** $R(t)$ should start near 0 and grow to a steady-state value (e.g., $R \approx 0.6$ for $K=2.0$). Increasing $K$ to $4.0$ should yield higher final $R$.

**Problem 21:** Narrow spread (Set A) achieves higher synchronization because oscillators are closer in frequency and easier to lock.

**Problem 22:** Small-world networks typically synchronize faster than ring networks due to shorter average path lengths.

**Problem 23:** The bifurcation diagram should show a sharp transition near $K_c \approx 1.57$ (for Lorentzian) or $K_c \approx 2/\pi \cdot \Delta\omega$ (for uniform).

**Problem 24:** The vorticity plot should show streamlines converging toward the synchronized cluster, resembling a fluid vortex.

---

## ✅ Solutions — Section E: Repo Scavenger Hunt

### Solution 25 (Rotor Update Rule)
The rotor update is in `step_euler_geometric` (or similar) in `rotor.py`. The bivector $\Omega$ is computed from the wedge product of the mean field and individual orientation, then multiplied by the coupling strength $K$.

### Solution 26 (Order Parameter)
`compute_order_parameter` uses `np.mean(np.exp(1j * theta), axis=1)` to compute $Z$, then `np.abs(Z)` for $R$. This is equivalent to $\frac{1}{N}\sum[\cos(\theta_j) + i\sin(\theta_j)]$.

### Solution 27 (SCF Optimization)
The key insight is computing `u_mean = np.mean(orientations, axis=0)` once per timestep, then using it for all oscillators. This replaces the $N^2$ pairwise sum with a single mean-field vector.

### Solution 28 (U(1) Symmetry)
The function `track_lie_symmetries` in `order_parameter.py` shifts all phases by a random constant $\phi$, recomputes the order parameter, and verifies that $R(t)$ is unchanged. This confirms the model respects global gauge invariance.
*An introductory Qiskit side quest for the Kuramoto Benchmark Suite*

> **AI-GENERATED CONTENT NOTICE:** These exercises were developed with AI assistance. Treat the derivations as the primary source of understanding; use Qiskit to test predictions, not as a substitute for them.

>

> **Integration note:** Append this section to `PRACTICE_PROBLEMS.md` after the existing Repo Scavenger Hunt section (or wherever the quantum-computing material best fits). The numbering continues from the current set.

---

## ⚛️ Section F: Quantum Computing — Complex Amplitudes, Rotations & Statistical Mechanics

These exercises introduce one-qubit quantum computing through the mathematics already used throughout this benchmark suite: complex numbers, vectors, matrices, rotations, and probability.

The intended workflow is **derive by hand → predict the result → run Qiskit → compare**. You do not need quantum hardware. The exercises use statevector simulation.

### Setup

Install the required packages in your project environment:

```bash

python -m pip install qiskit numpy

```

Imports used throughout this section:

```python

import numpy as np

from qiskit import QuantumCircuit

from qiskit.quantum_info import Statevector

```

A normalized one-qubit state has the form

$$

|\psi\rangle = \alpha|0\rangle + \beta|1\rangle,

\qquad

|\alpha|^2 + |\beta|^2 = 1,

$$

where $\alpha,\beta\in\mathbb{C}$. In the computational basis,

$$

|0\rangle =

\begin{bmatrix}1\\0\end{bmatrix},

\qquad

|1\rangle =

\begin{bmatrix}0\\1\end{bmatrix},

\qquad

|\psi\rangle =

\begin{bmatrix}\alpha\\\beta\end{bmatrix}.

$$

The norm of a ket is written with double vertical bars:

$$

\bigl\|\,|\psi\rangle\,\bigr\|

= \sqrt{\langle\psi|\psi\rangle}.

$$

For a normalized state, this norm equals $1$.

## Problem 29: Meet the Qubit

**Goal:** Translate between Dirac notation, column vectors, and measurement probabilities.

**Setup:** Consider the computational basis states

$$

|0\rangle =

\begin{bmatrix}1\\0\end{bmatrix},

\qquad

|1\rangle =

\begin{bmatrix}0\\1\end{bmatrix}.

$$

Also consider the equal-superposition state

$$

|+\rangle =

\frac{1}{\sqrt{2}}|0\rangle

+\frac{1}{\sqrt{2}}|1\rangle.

$$

**Tasks:**

1. Verify that $|0\rangle$ and $|1\rangle$ are normalized.

2. Write $|+\rangle$ as a column vector and verify that it is normalized.

3. Calculate the probability of measuring $0$ and the probability of measuring $1$ for each of the three states.

4. Explain why the amplitudes $\alpha$ and $\beta$ are not themselves measurement probabilities.

5. **Qiskit task:** Create a one-qubit circuit, apply a Hadamard gate with `qc.h(0)`, and inspect the resulting statevector and probabilities using `Statevector.from_instruction(qc)`.

**Hint:** For a state $|\psi\rangle=\alpha|0\rangle+\beta|1\rangle$,

$$

P(0)=|\alpha|^2,

\qquad

P(1)=|\beta|^2.

$$

**Reference:** Qiskit's `QuantumCircuit` and `Statevector` APIs.

## Problem 30: The Z-Axis Rotation

**Goal:** Understand how the $R_Z(\theta)$ gate transforms complex amplitudes.

**Setup:** The one-qubit Z-axis rotation is represented by

$$

R_Z(\theta)=

\begin{bmatrix}

e^{-i\theta/2} & 0\\

0 & e^{i\theta/2}

\end{bmatrix}.

$$

Begin with the equal-superposition state

$$

|+\rangle =

\frac{1}{\sqrt{2}}

\begin{bmatrix}1\\1\end{bmatrix}.

$$

**Tasks:**

1. Calculate $R_Z(\theta)|+\rangle$.

2. Evaluate the resulting state for

   $$

   \theta=0,\quad \frac{\pi}{2},\quad \pi,\quad 2\pi.

   $$

3. For each angle, calculate the computational-basis measurement probabilities.

4. Explain why the amplitudes change while the measurement probabilities remain equal.

5. Apply $R_Z(\theta)$ separately to $|0\rangle$ and $|1\rangle$. What changes, and what remains unchanged?

6. **Qiskit task:** Prepare $|+\rangle$ using `qc.h(0)`, apply `qc.rz(theta, 0)`, and inspect the resulting statevector and probabilities for the four angles above.

**Hint:** Apply the diagonal matrix to each component separately. Recall that $|e^{i\phi}|^2=1$.

**Conceptual checkpoint:** Distinguish a **global phase**, which multiplies the entire state by the same complex phase, from a **relative phase**, which changes the phase relationship between components.

**Reference:** `RZGate` and `QuantumCircuit.rz`.

## Problem 31: The Bloch Sphere

**Goal:** Connect complex amplitudes to a real three-dimensional geometric representation.

**Setup:** A pure one-qubit state can be parameterized as

$$

|\psi\rangle =

\cos\left(\frac{\vartheta}{2}\right)|0\rangle

+

e^{i\varphi}

\sin\left(\frac{\vartheta}{2}\right)|1\rangle.

$$

Its Bloch vector is

$$

\mathbf{r} =

\begin{bmatrix}

\sin\vartheta\cos\varphi\\

\sin\vartheta\sin\varphi\\

\cos\vartheta

\end{bmatrix}.

$$

**Tasks:**

1. Find the Bloch vector for $|0\rangle$.

2. Find the Bloch vector for $|1\rangle$.

3. Find the Bloch vector for

   $$

   |+\rangle=\frac{|0\rangle+|1\rangle}{\sqrt{2}}.

   $$

4. Apply $R_Z(\theta)$ to $|+\rangle$ and show that its Bloch vector rotates about the $z$-axis.

5. For $\theta=\pi/2$, calculate the new Bloch vector explicitly.

6. Compare the statevector after a $2\pi$ rotation with its Bloch vector. What changed, and what did not?

7. **Qiskit task:** Use `Statevector` to obtain the state after an $R_Z(\pi/2)$ rotation. Calculate the Bloch coordinates from the amplitudes yourself.

**Hint:** For a normalized state with amplitudes $\alpha$ and $\beta$, the Bloch coordinates can also be calculated from

$$

x=2\operatorname{Re}(\alpha^*\beta),

\qquad

y=2\operatorname{Im}(\alpha^*\beta),

\qquad

z=|\alpha|^2-|\beta|^2.

$$

**Reference:** Qiskit's `Statevector` representation. The Bloch vector is a geometric representation of a pure qubit state, not the statevector itself.

## Problem 32: Quantum Rotations Compose

**Goal:** Derive the composition and inverse properties of Z-axis rotations.

**Setup:** Consider two rotations,

$$

R_Z(\alpha)=

\begin{bmatrix}

e^{-i\alpha/2}&0\\

0&e^{i\alpha/2}

\end{bmatrix},

\qquad

R_Z(\beta)=

\begin{bmatrix}

e^{-i\beta/2}&0\\

0&e^{i\beta/2}

\end{bmatrix}.

$$

**Tasks:**

1. Multiply $R_Z(\alpha)R_Z(\beta)$ explicitly.

2. Show that

   $$

   R_Z(\alpha)R_Z(\beta)=R_Z(\alpha+\beta).

   $$

3. Show that

   $$

   R_Z(\theta)^{-1}=R_Z(-\theta).

   $$

4. Explain why applying a rotation followed by its inverse restores the original state.

5. **Qiskit task:** Prepare $|+\rangle$, apply rotations by $\alpha=\pi/3$ and $\beta=\pi/4$ in sequence, and compare the result with a single rotation by $\alpha+\beta$.

6. **Bonus:** Investigate whether the same simple composition rule holds for rotations about different axes. Compare $R_X(\alpha)R_Z(\beta)$ with $R_Z(\beta)R_X(\alpha)$.

**Hint:** Diagonal matrix multiplication reduces to multiplying the corresponding diagonal entries. For the bonus, remember that matrix multiplication is not generally commutative.

**Qiskit note:** `Statevector.equiv(other)` tests whether two statevectors represent the same physical pure state up to a global phase.

## Problem 33: A Two-Level System and Boltzmann Multiplicity

**Goal:** Connect the counting of microscopic configurations to macroscopic entropy.

**Setup:** Consider $N=4$ noninteracting two-level systems. Each system has a ground state with energy $E_0=0$ and an excited state with energy $E_1=\epsilon$.

Suppose exactly $n$ of the four systems are excited. The number of microscopic configurations compatible with this macrostate is

$$

W(N,n)=\binom{N}{n}

=\frac{N!}{n!(N-n)!}.

$$

The Boltzmann entropy associated with this multiplicity is

$$

S_n=k_B\ln W(N,n).

$$

**Tasks:**

1. Calculate $W(4,n)$ for $n=0,1,2,3,4$.

2. Verify that the total number of possible configurations is

   $$

   \sum_{n=0}^{4}W(4,n)=2^4.

   $$

3. Calculate $S_n/k_B$ for each macrostate.

4. Identify the macrostate with the greatest multiplicity and entropy.

5. Explain why the most numerous macrostate is not the only possible macrostate.

6. **Visualization task:** Plot $W(4,n)$ and $S_n/k_B$ as functions of $n$. Label the axes and identify the most numerous macrostate.

7. **Extension:** Repeat the calculation for $N=10$, then $N=50$. What happens to the relative prominence of the central macrostate?

**Hint:** You can use `math.comb(N, n)` or `scipy.special.comb` to calculate binomial coefficients. For the entropy, take the natural logarithm.

**Physical interpretation:** A macrostate can be overwhelmingly more likely than another because many more microscopic configurations correspond to it. This is the combinatorial foundation behind the Boltzmann expression $S=k_B\ln W$.

## Problem 34: Relative Phase, Energy Populations, and Entropy

**Goal:** Discover how a quantum transformation can change relative phase without changing energy-basis populations.

**Setup:** Consider a two-level quantum system with Hamiltonian

$$

H=\epsilon|1\rangle\langle1|

=

\begin{bmatrix}

0&0\\

0&\epsilon

\end{bmatrix}.

$$

The Z-rotation is

$$

R_Z(\theta)=

\begin{bmatrix}

e^{-i\theta/2}&0\\

0&e^{i\theta/2}

\end{bmatrix}.

$$

**Tasks:**

1. Calculate the matrix products $HR_Z(\theta)$ and $R_Z(\theta)H$.

2. Show that

   $$

   [H,R_Z(\theta)]

   =HR_Z(\theta)-R_Z(\theta)H=0.

   $$

3. Explain why an $R_Z$ rotation does not change the probabilities of measuring the system in the energy eigenbasis.

4. Prepare $|+\rangle$, apply $R_Z(\theta)$, and compare the probabilities before and after the rotation.

5. Explain why the relative phase can still matter if a later operation mixes the basis states. Try applying a Hadamard gate after the Z rotation and compare the resulting measurement probabilities for several values of $\theta$.

6. **Statistical-mechanics connection:** For $N$ independent two-level systems, explain why a phase rotation that leaves every computational-basis population unchanged also leaves the probability distribution over computational-basis configurations unchanged.

7. Explain why the Boltzmann configurational entropy $S=k_B\ln W$ should not automatically be identified with the von Neumann entropy of a quantum state.

**Hint:** The computational basis is the energy eigenbasis for the Hamiltonian given above. A diagonal phase transformation changes phases of basis amplitudes but not their squared magnitudes.

**Important distinction:** The Boltzmann expression $S=k_B\ln W$ describes the multiplicity of a macrostate under a specified coarse-graining. The von Neumann entropy is

$$

S_{\mathrm{vN}}=-k_B\operatorname{Tr}(\rho\ln\rho).

$$

A pure quantum state has zero von Neumann entropy, even when a measurement in a chosen basis has more than one possible outcome.

**Qiskit task:**

```python

theta = np.pi / 3

qc = QuantumCircuit(1)

qc.h(0)

before = Statevector.from_instruction(qc)

qc.rz(theta, 0)

after = Statevector.from_instruction(qc)

print("Before:", before.probabilities())

print("After: ", after.probabilities())

# Now add a Hadamard gate and inspect the new probabilities.

qc.h(0)

after_interference = Statevector.from_instruction(qc)

print("After H:", after_interference.probabilities())

```

**Question:** Why can the final Hadamard make the relative phase visible in measurement statistics even though the Z rotation alone did not change the computational-basis probabilities?

## Problem 35: Spinor Sign and the 4π Rotation

**Goal:** Explore the relationship between spinors, SU(2), and ordinary three-dimensional rotations.

**Setup:** Recall the Z-axis rotation matrix

$$

R_Z(\theta)=

\begin{bmatrix}

e^{-i\theta/2}&0\\

0&e^{i\theta/2}

\end{bmatrix}.

$$

**Tasks:**

1. Calculate $R_Z(2\pi)$.

2. Calculate $R_Z(4\pi)$.

3. Show that

   $$

   R_Z(2\pi)=-I,

   \qquad

   R_Z(4\pi)=I.

   $$

4. Apply both transformations to an arbitrary normalized state $|\psi\rangle$. What happens to the statevector?

5. Explain why the Bloch vector is unchanged by the global sign acquired after a $2\pi$ rotation.

6. Research or explain, in your own words, why this behavior is associated with the relationship between $SU(2)$ and $SO(3)$.

**Qiskit task:** Prepare $|+\rangle$, apply rotations by $2\pi$ and $4\pi$ in separate circuits, and compare the resulting statevectors. Use `Statevector.equiv` as well as direct inspection of the amplitudes.

**Hint:** A global phase does not change measurement probabilities or the physical pure state represented by a statevector. The spinor's sign is nevertheless important when considering how quantum rotation operators compose.

**Reference:** This is an introductory preview of spinors and the double-cover relationship $SU(2)\rightarrow SO(3)$. A full derivation is outside the scope of this first exercise set.

---

## ✅ Solutions — Section F: Quantum Computing

### Solution 29 (Meet the Qubit)

1. Both computational basis states have norm $1$:

   $$

   \|\,|0\rangle\,\|=\sqrt{1^2+0^2}=1,

   \qquad

   \|\,|1\rangle\,\|=\sqrt{0^2+1^2}=1.

   $$

2. The equal-superposition state is

   $$

   |+\rangle=\frac{1}{\sqrt{2}}

   \begin{bmatrix}1\\1\end{bmatrix}.

   $$

   Its squared norm is $1/2+1/2=1$.

3. The measurement probabilities are:

   - $|0\rangle$: $P(0)=1$, $P(1)=0$.

   - $|1\rangle$: $P(0)=0$, $P(1)=1$.

   - $|+\rangle$: $P(0)=1/2$, $P(1)=1/2$.

4. Amplitudes are complex probability amplitudes. Their squared magnitudes give measurement probabilities.

5. The Hadamard gate maps $|0\rangle$ to $|+\rangle$. The resulting statevector is $(1/\sqrt{2},1/\sqrt{2})$, with probabilities $(1/2,1/2)$.

### Solution 30 (The Z-Axis Rotation)

1. Matrix multiplication gives

   $$

   R_Z(\theta)|+\rangle

   =

   \frac{1}{\sqrt{2}}

   \begin{bmatrix}

   e^{-i\theta/2}\\

   e^{i\theta/2}

   \end{bmatrix}.

   $$

2. The four states are:

   - $\theta=0$: $(1,1)^T/\sqrt{2}$.

   - $\theta=\pi/2$: $(e^{-i\pi/4},e^{i\pi/4})^T/\sqrt{2}$.

   - $\theta=\pi$: $(-i,i)^T/\sqrt{2}$.

   - $\theta=2\pi$: $(-1,-1)^T/\sqrt{2}=-|+\rangle$.

3. Both amplitudes always have squared magnitude $1/2$, so the probabilities remain $(1/2,1/2)$.

4. The diagonal entries of $R_Z$ have unit magnitude. They change phase but not amplitude magnitude.

5. The basis states each acquire a phase: $|0\rangle$ gets $e^{-i\theta/2}$ and $|1\rangle$ gets $e^{i\theta/2}$. For either basis state alone, this is a global phase and has no observable effect.

6. Qiskit should report equal computational-basis probabilities for every tested angle.

### Solution 31 (The Bloch Sphere)

1. $|0\rangle$ corresponds to $(0,0,1)$.

2. $|1\rangle$ corresponds to $(0,0,-1)$.

3. $|+\rangle$ corresponds to $(1,0,0)$.

4. Applying $R_Z(\theta)$ changes the relative phase from $\varphi=0$ to $\varphi=\theta$. Thus the Bloch vector becomes

   $$

   \mathbf r'=

   \begin{bmatrix}

   \cos\theta\\

   \sin\theta\\

   0

   \end{bmatrix}.

   $$

5. For $\theta=\pi/2$, $\mathbf r'=(0,1,0)$.

6. At $2\pi$, the statevector becomes $-|+\rangle$, but the Bloch vector returns to $(1,0,0)$. The sign is a global phase and does not change the represented Bloch vector.

### Solution 32 (Quantum Rotations Compose)

1. Multiplying the diagonal matrices gives

   $$

   R_Z(\alpha)R_Z(\beta)=

   \begin{bmatrix}

   e^{-i(\alpha+\beta)/2}&0\\

   0&e^{i(\alpha+\beta)/2}

   \end{bmatrix}.

   $$

2. This is exactly $R_Z(\alpha+\beta)$.

3. Setting $\beta=-\alpha$ gives the identity matrix, so the inverse is $R_Z(-\alpha)$.

4. A rotation followed by its inverse gives $R_Z(-\theta)R_Z(\theta)=I$.

5. The two Qiskit circuits produce equivalent statevectors. `Statevector.equiv` should return `True`.

6. Rotations about different axes generally do not commute. Their order can change the resulting state.

### Solution 33 (A Two-Level System and Boltzmann Multiplicity)

1. The multiplicities are

   $$

   W(4,n)=[1,4,6,4,1].

   $$

2. Their sum is $1+4+6+4+1=16=2^4$.

3. The dimensionless entropies are

   $$

   \frac{S_n}{k_B}=\ln W(4,n),

   $$

   giving approximately $[0,1.3863,1.7918,1.3863,0]$.

4. The macrostate with $n=2$ excited systems has the largest multiplicity, $W=6$, and largest entropy, $S=k_B\ln 6$.

5. Other macrostates remain possible; they simply correspond to fewer microscopic configurations.

6. The plots should be symmetric about $n=2$, with their maximum at the central macrostate.

7. As $N$ grows, the multiplicity becomes increasingly concentrated around $n=N/2$ relative to the extreme macrostates.

### Solution 34 (Relative Phase, Energy Populations, and Entropy)

1. Both products are diagonal:

   $$

   HR_Z(\theta)=R_Z(\theta)H

   =

   \begin{bmatrix}

   0&0\\

   0&\epsilon e^{i\theta/2}

   \end{bmatrix}.

   $$

2. Their difference is zero, so the operators commute.

3. The energy eigenbasis populations are the squared magnitudes of the two amplitudes. Multiplying either amplitude by a unit-magnitude phase leaves those populations unchanged.

4. Before and after the Z rotation, the probabilities for $|+\rangle$ are $(1/2,1/2)$.

5. A subsequent Hadamard mixes the amplitudes. The relative phase can then affect constructive or destructive interference and therefore change measurement probabilities.

6. Independent diagonal phase rotations change the phases of computational-basis amplitudes but not their magnitudes. Consequently, the probabilities of the computational-basis configurations remain unchanged.

7. Boltzmann configurational entropy counts the multiplicity of a macrostate under a chosen coarse-graining. Von Neumann entropy characterizes a quantum density operator. A pure state has zero von Neumann entropy even if its measurement outcomes are probabilistic in a particular basis.

### Solution 35 (Spinor Sign and the 4π Rotation)

1. At $\theta=2\pi$, both diagonal entries equal $-1$, so $R_Z(2\pi)=-I$.

2. At $\theta=4\pi$, both diagonal entries equal $1$, so $R_Z(4\pi)=I$.

3. The identities follow directly from $e^{\pm i\pi}=-1$ and $e^{\pm i2\pi}=1$.

4. A $2\pi$ rotation maps every statevector to its negative; a $4\pi$ rotation restores it exactly.

5. The Bloch vector depends on products such as $\alpha^*\beta$, which are unchanged when both amplitudes acquire the same minus sign.

6. $SU(2)$ is a double cover of $SO(3)$: two elements of $SU(2)$, differing by an overall sign, correspond to the same ordinary three-dimensional rotation. This is the mathematical reason a spinor requires a $4\pi$ rotation to return exactly to its original representation.

---

## 📌 Notes on Conventions and Scope

- In this section, $\theta$ denotes the angle parameter supplied to the Qiskit $R_Z(\theta)$ gate. Its matrix contains half-angles, as shown explicitly above.

- A statevector is a complex column vector. Its norm is written with double vertical bars; the magnitude of a scalar amplitude uses single absolute-value bars.

- Statevectors that differ only by a global phase represent the same physical pure state. Relative phase can affect interference when amplitudes are subsequently mixed.

- The Boltzmann entropy $S=k_B\ln W$ and von Neumann entropy are related to different descriptions of statistical structure. Do not treat them as interchangeable.

- These are introductory one-qubit exercises. Multi-qubit entanglement, density matrices, measurement sampling, and hardware noise can be developed in later sections.

