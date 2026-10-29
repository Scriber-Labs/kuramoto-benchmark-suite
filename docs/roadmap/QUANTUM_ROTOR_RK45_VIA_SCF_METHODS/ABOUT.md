# Using Qiskit Practically to Implement RK45 via SCF Methods

## Introduction
To construct an architecture that implements qiskit in a practical manner for rk45 integration with clifford algebra, we 
have to solve a fundamental mathematical conflict -- quantum mechanics is strictly linear, governed by the linear Schrödinger equation:
$$\frac{d|{}\psi \rangle }{dt}=-iH|{}\psi \rangle \, .$$

Our issue lies with the fact that the Kuramoto model is inherently non-linear due to the sinusoidal interaction terms between pairs of oscillators:
$$\frac{d\theta _{i}}{dt}=\omega _{i}+\frac{K}{N}\sum _{j=1}^{N}\sin (\theta _{j}-\theta _{i})\)$$
If we try to map this non-linear interaction directly to qubits using standard quantum gates, we are forced to use 
dense, multi-qubit entangling operations (like Controlled-NOT arrays). This causes the quantum circuit depth to explode 
exponentially with the number of steps, rendering an adaptive scheme like RK45 practically useless.

We can bypass this bottleneck and build a flat $\mathcal{O}(1)$ depth circuit for the RK45 stages, via implementation of
a Self-Consistent Field (SCF) approximation. 

## Step-by-step mathematical derivation of SCF approach.

### **Step 1:** The Mean-Field Reduction (SCF Linearization)

We apply a mean-field reduction to rewrite the coupled system. We define the complex order parameter 
$$R(t)e^{i\psi(t)}$$ as the geometric average of all phase positions in the complex plane:
$$R(t)e^{i\psi (t)}=\frac{1}{N}\sum _{j=1}^{N}e^{i\theta _{j}(t)}\, .$$

To see how this decouples the system, we multiply both sides by $e^{-i\theta _{i}(t)}$:
$$R(t)e^{i(\psi (t)-\theta _{i}(t))}=\frac{1}{N}\sum _{j=1}^{N}e^{i(\theta _{j}(t)-\theta _{i}(t))} \, .$$

Next, we apply Euler's formula $e^{ix} = \cos x + i\sin x$ and extract only the imaginary part of both sides:
$$\text{Im}\left[R(t)\left(\cos (\psi -\theta _{i})+i\sin (\psi -\theta _{i})\right)\right]=\text{Im}\left[\frac{1}{N}\sum _{j=1}^{N}\left(\cos (\theta _{j}-\theta _{i})+i\sin (\theta _{j}-\theta _{i})\right)\right]$$
$$R(t)\sin (\psi (t)-\theta _{i}(t))=\frac{1}{N}\sum _{j=1}^{N}\sin (\theta _{j}(t)-\theta _{i}(t))$$

Substituting this identity back into the original Kuramoto equation yields the decoupled, self-consistent field equation 
for each individual oscillator:
$$\frac{d\theta _{i}}{dt}=\omega _{i}+KR(t)\sin (\psi (t)-\theta _{i}(t)) \, .$$

**Mathematical Insight:** The oscillators no longer calculate interactions with each other. They each interact only 
with the global background fields $R(t)$ and $\psi(t)$. This effectively linearizes the structure of the system 
equations at any specific snapshot in time.

### **Step 2:** Mapping Phase Space to Hilbert Space

We map each classical oscillator $i$ to its own independent qubit state $\vert{}\psi_i\rangle$. We restrict the qubit 
state to the equatorial plane (i.e., the $X$-$Y$ plane) of the Bloch sphere, parameterizing it by its relative phase 
$\theta _{i}$:
$$|{}\psi _{i}(t)\rangle =\frac{1}{\sqrt{2}}\left(|{}0\rangle +e^{i\theta _{i}(t)}|{}1\rangle \right)$$

The complete state of our 10-oscillator system is the simple unentangled product state:
$$|{}\Psi (t)\rangle =\bigotimes _{i=1}^{10}|{}\psi _{i}(t)\rangle$$

### **Step 3:** Deriving the Time-Dependent Effective Hamiltonian

For a quantum state vector to evolve its phase according to our linearized velocity equation, it must undergo unitary 
time evolution driven by a Hamiltonian operator $H_{\text{eff}}(t)$.
Let's look at the action of a standard Pauli-$Z$ operator on our phase-encoded state:
$$Z=\left(\begin{matrix}1&0\\ 0&-1\end{matrix}\right)$$

If we evolve our single-qubit state using an arbitrary time-dependent frequency $\Omega_i(t)$ as the weight for our $Z$ 
operator, the unitary evolution operator $$U(t, \Delta t) = \exp\left(-i \int \frac{\Omega_i(t)}{2} Z dt\right)$$ 
operating on our state produces:
$$\exp \left(-i\frac{\Omega _{i}\Delta t}{2}Z\right)\left[\frac{1}{\sqrt{2}}\left(|{}0\rangle +e^{i\theta _{i}}|{}1\rangle \right)\right]=\frac{1}{\sqrt{2}}\left(e^{-i\frac{\Omega _{i}\Delta t}{2}}|{}0\rangle +e^{i\frac{\Omega _{i}\Delta t}{2}}e^{i\theta _{i}}|{}1\rangle \right)\, .\)$$

Factoring out the global phase factor $e^{-i\frac{\Omega _{i}\Delta t}{2}}$ gives:
$$\equiv \frac{1}{\sqrt{2}}\left(|{}0\rangle +e^{i(\theta _{i}+\Omega _{i}\Delta t)}|{}1\rangle \right) \, .$$

Comparing this to our classical phase-velocity framework, we can see that the new phase is exactly 
$$\theta_i + \Omega_i \Delta t$$. 

Therefore, to perfectly mirror the Kuramoto trajectory, we set the time-dependent eigenvalues of our quantum Hamiltonian 
to match our physical velocities exactly:
$$H_{\text{eff}}(t)=\sum _{i=1}^{10}\frac{\Omega _{i}(t)}{2}Z_{i}\ \, $$
where $$\Omega _{i}(t)=\omega _{i}+KR(t)\sin (\psi (t)-\theta _{i}(t)) \, .$$

Because $H_{\text{eff}}(t)$ contains only single-qubit $Z$ terms, all operators commute ($[Z_i, Z_j] = 0$). This means 
the total system unitary time evolution factors exactly into parallel, independent single-qubit phase gates:
$$U(t,\Delta t)=\bigotimes _{i=1}^{10}\exp \left(-i\frac{\Omega _{i}(t)\Delta t}{2}Z_{i}\right)=\bigotimes _{i=1}^{10}R_{z}\left(\Omega _{i}(t)\Delta t\right)_{i}\)$$

### **Step 4:** The RK45 Stage Integration Derivation

To resolve these time-dependent operators using the adaptive Dormand-Prince (RK45) scheme, the classical co-processor 
$$k_{1,i}=\Omega _{i}\left(\vec{\theta }^{(n)}\right)$$
$$k_{2,i}=\Omega _{i}\left(\vec{\theta }^{(n)}+\Delta t\cdot a_{21}\vec{k}_{1}\right)$$
$$\vdots$$
$$k_{6,i}=\Omega _{i}\left(\vec{\theta }^{(n)}+\Delta t\cdot \sum _{m=1}^{5}a_{6m}\vec{k}_{m}\right) \, .$$

Crucially, because we decoupled the system equations in Step 1, all six intermediate trial steps can be computed 
completely within the classical host memory using simple vector arithmetic.

Once the classical host compares the 4th-order and 5th-order updates to check the truncation error, it computes the 
final accepted net phase change:
$$\Delta \theta _{i,\text{net}}=\Delta t\sum _{m=1}^{6}c_{m}k_{m,i} \, .$$

Only now do we communicate with the quantum hardware. Instead of performing six sequential quantum steps, we accumulate 
the entire RK45 step classically and execute it on the QPU in a single step via parallel phase gates:
$$|{}\Psi (t_{n+1})\rangle =\left[\bigotimes _{i=1}^{10}R_{z}\left(2\Delta \theta _{i,\text{net}}\right)_{i}\right]|{}\Psi (t_{n})\rangle$$

The quantum computer acts as a high-speed parallel phase carrier. It maintains an exact $\mathcal{O}(1)$ circuit depth 
across the entire simulation, preventing quantum gate error accumulation while fully resolving complex non-linear 
synchronization.

## Tasks & Theoretical Notes

### 1. Mapping Local Truncation Error $\epsilon = |\theta_{5^\text{th}} - \theta_{4^\text{th}}|$ to Quantum State Distance Metrics

For a single qubit state parameterized on the equator of the Bloch sphere:
$$|\psi_i(\theta)\rangle = \frac{1}{\sqrt{2}}(|0\rangle + e^{i\theta}|1\rangle),$$
the overlap (fidelity) between the $5^\text{th}$-order and $4^\text{th}$-order candidate states is:
$$|\langle \psi_i(\theta_{4^\text{th}}) | \psi_i(\theta_{5^\text{th}}) \rangle|^2 = \left| \frac{1 + e^{i(\theta_{5^\text{th}} - \theta_{4^\text{th}})}}{2} \right|^2 = \cos^2\left(\frac{\Delta \theta_i}{2}\right) = 1 - \sin^2\left(\frac{\epsilon_i}{2}\right) \approx 1 - \frac{\epsilon_i^2}{4}.$$

The Fubini-Study / Bures metric distance $D_{\text{FS}}$ on the quantum state space is therefore directly proportional to the local truncation error:
$$D_{\text{FS}}(|\psi_i^{(4)}\rangle, |\psi_i^{(5)}\rangle) = \arccos\left(\left|\langle \psi_i^{(4)} | \psi_i^{(5)} \rangle\right|\right) = \frac{|\theta_{5^\text{th}} - \theta_{4^\text{th}}|}{2} = \frac{\epsilon_i}{2}.$$

For the total unentangled $N$-qubit product state $|\Psi\rangle = \bigotimes_{i=1}^N |\psi_i\rangle$, the total state fidelity satisfies:
$$F = \prod_{i=1}^N \left(1 - \frac{\epsilon_i^2}{4}\right) \approx 1 - \frac{1}{4}\sum_{i=1}^N \epsilon_i^2 = 1 - \frac{1}{4}\|\vec{\epsilon}\|_2^2.$$

Thus, controlling the Euclidean norm of classical truncation errors $\|\vec{\epsilon}\|_2$ provides an exact bound on quantum state infidelity $\Delta F \le \frac{1}{4}\|\vec{\epsilon}\|_2^2$.

---

### 2. Introducing Stochastic Phase Noise (White Noise) into the Effective Hamiltonian

To simulate dephasing / thermal fluctuations and quantum hardware noise (e.g., $T_2^*$ dephasing), we introduce an Itô / Stratonovich stochastic term into the effective single-qubit Hamiltonian:
$$H_{\text{eff}}(t) dt = \sum_{i=1}^N \frac{\Omega_i(t)}{2} Z_i dt + \sum_{i=1}^N \frac{\sigma_i}{2} Z_i \circ dW_i(t),$$
where $W_i(t)$ are standard independent Wiener processes ($\mathbb{E}[dW_i(t) dW_j(t)] = \delta_{ij} dt$).

Under Stratonovich stochastic calculus, this generates the stochastic differential equation (SDE) for phases:
$$d\theta_i(t) = \Omega_i(t) dt + \sigma_i dW_i(t),$$
which is solved via the Euler-Maruyama scheme:
$$\theta_i(t + \Delta t) = \theta_i(t) + \Omega_i(t)\Delta t + \sigma_i \sqrt{\Delta t} \cdot \xi_i, \quad \xi_i \sim \mathcal{N}(0, 1).$$

When translated to the open quantum system Lindblad master equation:
$$\frac{d\rho}{dt} = -i [H_{\text{eff}}(t), \rho] + \sum_{i=1}^N \frac{\gamma_i}{2} \left(Z_i \rho Z_i - \rho\right), \quad \gamma_i = \frac{\sigma_i^2}{2},$$
the off-diagonal density matrix elements decay as $e^{-\gamma_i t} = e^{-\frac{\sigma_i^2}{2} t}$, providing exact correspondence between Kuramoto phase diffusion and pure dephasing in quantum systems.
