# ✍️ Practice Problems: Geometric synchronization & GA
*Mastering the foundations of the Kuramoto Benchmark Suite*

> ⚠️ **AI-GENERATED CONTENT NOTICE:** This practice problem set was generated with the assistance of an AI (Junie).

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
