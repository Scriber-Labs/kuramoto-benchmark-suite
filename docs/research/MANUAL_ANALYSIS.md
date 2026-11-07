# 🧠 Manual Analysis & Reflection Guide
*Welcome back. Use this document as a structured prompt for your brain to engage with the deliverables we built today.*

> ⚠️ **AI-GENERATED CONTENT NOTICE:** This manual analysis guide was generated with the assistance of an AI (Junie).
> **Last Updated:** October 2026 — Expanded with focus strategies and session check-ins.

---

## 💚 Check-In: Are You Feeling Spread Too Thin?

Before you dive in, take a breath and answer these questions honestly:

1. **Energy level:** On a scale of 1-10, how much mental energy do you have right now?
   - **7-10:** Great time for deep derivation work (Section B problems).
   - **4-6:** Good time for plotting exercises (Section D) — they're more visual and less abstract.
   - **1-3:** Consider doing the scavenger hunt (Section E) — it's mostly reading code, which is lower cognitive load.

2. **Distraction check:** Are you tempted to update repo infrastructure instead of doing math?
   - If **yes**, remind yourself: **The preprint and understanding come first.** Infrastructure can wait.
   - Pick **one** concrete problem from `PRACTICE_PROBLEMS.md` and commit to finishing it before touching anything else.

3. **Turbulence check:** If your mind feels scattered, try this:
   - Set a timer for **25 minutes** (Pomodoro).
   - Work on **one single problem** during that time.
   - After the timer, take a **5-minute break** away from the screen.
   - Repeat.

---

## 📋 Part 1: The Deliverable Checklist
*Before you dive into the code, check the outputs of our session.*
- [x] **Benchmarks**: Open `BENCHMARK_RUNDOWN.md` and check the scaling results.
- [ ] **Theory**: Open `LEARNING_GUIDE.md` and read the Bivector Torque derivation.
- [ ] **Practice**: Work through `PRACTICE_PROBLEMS.md` — start with Section B (Canonical Derivation) for deep math, or Section D (Plotting) for visual learning.
- [ ] **Number Theory**: Complete Section C (Bézout's Identity) to understand the coprime sampling in `coprime.py`.
- [x] **Visualization**: Look at `../plots/benchmarks/scaling_performance.png` (if you can view images) or from the project root, run `python3 scripts/rigorous_benchmarks.py` again to see the terminal output.
- [ ] **Quantum**: Inspect `../src/kuramoto/quantum/circuit_gen.py` to see the SCF mapping logic.
- [ ] **Scavenger Hunt**: Complete Section E of `PRACTICE_PROBLEMS.md` to connect the math to the actual code.

---

## 🔍 Part 2: Self-Assessment (The "What I Understand" Check)
*Answer these questions to yourself honestly.*

1. **The Vectorized GA Speedup**: Do I understand *why* the GA solver scaled linearly $O(N)$ while standard solvers often struggle? (Hint: It’s the "Mean-Field" reduction).
2. **The Fluid Flow Analogy**: Can I explain why a "Bivector Torque" is the same thing as "Vorticity" in a fluid? Why does this make sense visually in the streamplots?
3. **The Quantum Bridge**: Do I see the connection between the rotor update $\exp(\Omega \Delta t)$ and the $R_z$ gate in Qiskit? Why did we call it the "Self-Consistent Field" (SCF) approximation?
4. **Lie-Group Integrators (RKMK4 & DOPRI54)**: Why does evaluating Runge-Kutta stages directly in the Lie algebra $\mathfrak{spin}(n)$ guarantee exact rotor unit-norm conservation ($\sum R_k^2 = 1$) without numerical projection?
5. **Time-Reversal Reconstruction**: Why does 5th-order DOPRI54 and 4th-order RKMK4 achieve $\sim 10^{-13}$ machine-precision time-reversal reconstruction over 50 seconds, whereas 2nd-order adaptive schemes accumulate $O(\Delta t^2) \sim 10^{-9}$ error?

---

## 🏗️ Part 3: Deep Dive Prompts (The "Hard Parts")
*These are the "Hard Parts." If these are fuzzy, mark them for our next session.*

- **Manifold Constraints & Lie Exp Map**: Why does exponentiating a bivector $\exp(-\frac{\Delta t}{2}\Omega B)$ preserve unit rotors to machine precision ($10^{-16}$) while standard Euclidean ODE integrators drift away from the circle/sphere?
- **FSAL Velocity Caching**: In Dormand-Prince 5(4), why is the 7th stage evaluate identical to the 1st stage of the subsequent step, and how does that save $O(N^2)$ bivector torque calculations?
- **Cartesian Product Manifolds**: How does the product structure $\operatorname{Spin}(n)^N$ allow decoupled per-oscillator rotor updates while enforcing unified ensemble-level error control?
- **Bivector Algebra**: How exactly does the wedge product $v_i \wedge v_{mean}$ represent a physical pull?

---

## 🎯 Part 4: Your Next Steps — Focused Task List

*Pick **ONE** path below and stick with it. Don't jump between paths.*

### Path A: Deep Math Derivation (High Energy, High Reward)
**Best if:** You have a 7-10 energy level and want to build real understanding.

1. Work through **Problem 13** (Deriving the Coupling Term) on paper.
2. Work through **Problem 14** (Mean-Field Reduction) on paper.
3. Open `RESEARCH_PREPRINT.md` Section 2 and compare your derivation with the written version.
4. **Goal:** You can derive the Kuramoto equation from scratch without looking at notes.

### Path B: Visual Learning Through Plotting (Medium Energy, High Satisfaction)
**Best if:** You want to see what synchronization actually looks like.

1. Open a Jupyter notebook in `examples/notebooks/`.
2. Complete **Problem 19** (Phase Portrait) — run the simulation and plot it.
3. Complete **Problem 20** (Order Parameter Dynamics) — watch R(t) emerge.
4. Complete **Problem 23** (Bifurcation Diagram) — this is the "money plot" for your preprint.
5. **Goal:** You have 3 plots you understand and can explain.

### Path C: Number Theory Foundation (Medium Energy, Builds Confidence)
**Best if:** You want to understand the coprime sampling code in `coprime.py`.

1. Complete **Problem 16** (Bézout's Identity by Hand).
2. Complete **Problem 17** (CRT Reconstruction).
3. Open `src/kuramoto/solvers/coprime.py` and read the `extended_gcd` function.
4. **Goal:** You understand why the code requires `gcd(M, N) == 1`.

### Path D: Code Scavenger Hunt (Lower Energy, Still Productive)
**Best if:** You're tired but still want to make progress.

1. Complete **Problems 25-28** in Section E of `PRACTICE_PROBLEMS.md`.
2. Just read the code — no writing required.
3. **Goal:** You can point to the exact lines that implement the math you're learning.

### Path E: Dash App Integration (If You Want to Connect Systems)
**Best if:** You want to see your simulation data in a web interface.

1. From the project root, run:
   ```bash
   python scripts/export_to_dash.py -i data/examples/demo_dataset.npz -o kuramoto_export.json
   ```
2. Load the output into your `kuramoto-dash-app` project.
3. **Goal:** Your simulation data appears in the Dash dashboard.

---

## ⚠️ Important Reminders

- **The preprint and understanding come first.** Infrastructure updates, CLI styling, and repo maintenance can wait.
- **If you feel yourself drifting toward "updating everything,"** stop and ask: "Does this move me closer to a preprint I understand?" If not, put it down.
- **AI-generated notebooks go in `examples/notebooks/ai-generated/`.** Anything you code yourself goes in the main notebook folder. This keeps your work honest.
- **One problem at a time.** Don't try to do everything. Finish one problem, check the solution, feel good about it, then move to the next.

---
*Signed, Junie.*
