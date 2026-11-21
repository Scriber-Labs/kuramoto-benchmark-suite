# Quasi-Periodic RKMK4 Hybrid Method

**Status:** Idea / Future Exploration  
**Date:** November 2026  
**Priority:** Low — explore after preprint is complete

---

## Motivation

Current `RotorSolver` provides two complementary approaches to reducing numerical drift in geometric algebra rotor integration:

1. **`quasi_periodic_step`** (Fibonacci-word Strang splitting) — A 2nd-order-per-step method that uses the golden-ratio-based Fibonacci word sequence to alternate operator splitting order. It avoids rational resonances, achieving RKMK4-level accuracy at ~2.3× the speed.

2. **`step_rkmk4`** (Runge-Kutta-Munthe-Kaas 4th-order) — A classic Lie group integrator that strictly preserves the Spin(n) manifold through 4-stage Runge-Kutta on the Lie algebra of bivectors. Computationally expensive but theoretically robust with 4th-order accuracy guarantees.

Both methods preserve the rotor manifold to near machine precision (~1e-13 norm deviation) and produce nearly identical order parameter trajectories (RMS divergence ~5e-4). The coprime sampler confirms both are numerically faithful with channel discrepancies around ~3e-4.

**The question:** Can the resonance-avoidance principle of Fibonacci-word sequencing be extended to RKMK4 to yield a method that combines RKMK4's 4th-order accuracy with the drift-reduction benefits of aperiodic patterning?

---

## Core Concept

Standard RKMK4 evaluates the bivector field at 4 fixed stages per step using a classic Butcher tableau `(1, 2, 2, 1)/6`. While there is no explicit operator splitting, the sequence of evaluation points on the manifold forms a trajectory through bivector space. For systems with near-resonant frequencies, these stages might sample the bivector field at points that accidentally align with resonances, causing systematic error accumulation.

**Hypothesis:** Alternating between two RKMK4 variants according to the Fibonacci word sequence would break any such alignment, similar to how `quasi_periodic_step` reduces drift for Strang splitting.

---

## Potential Approaches

### Approach 1: Dual Butcher Tableau Alternation

Use two different 4th-order Runge-Kutta methods, alternated by the Fibonacci word:

- **Frame A (symbol 0):** Classic RKMK4 with Butcher tableau `(1, 2, 2, 1)/6`.
- **Frame B (symbol 1):** RKMK4 variant using a different 4th-order tableau (e.g., Cash-Karp `(37/378, 250/648, 125/648, 512/1771, 500/55, 125/216, 512/856)` — though this is 5th-order, a 4th-order variant exists).

The Fibonacci word determines which tableau to use at each step:
```python
symbol = fibonacci_word_symbol(step_index)
if symbol == 0:
    step_rkmk4_classic(K, dt)
else:
    step_rkmk4_cash_karp(K, dt)
```

**Pros:** Well-defined; leverages existing Butcher tableau theory.  
**Cons:** The two tableaus have different error constants — does alternation help or hurt?

### Approach 2: Time-Reversed RKMK4 Alternation

Alternate between forward and time-reversed RKMK4 stages:

- **Frame A (symbol 0):** Standard RKMK4 stage order `(k₁, k₂, k₃, k₄)`.
- **Frame B (symbol 1):** Time-reversed RKMK4 — run the 4 stages in reverse order `(k₄, k₃, k₂, k₁)` with negative weights, then correct.

This is a known technique in geometric integration (time-symmetric integrators).

**Pros:** Time-reversal symmetry is well-studied; pairs naturally with Fibonacci sequencing.  
**Cons:** More complex implementation; requires careful handling of the correction step.

### Approach 3: Permutation of Stage Evaluation

Instead of evaluating bivector velocity at `ω(y₀) → ω(y₁) → ω(y₂) → ω(y₃)`, use a permuted sequence of intermediate points for Frame B:

- **Frame A (symbol 0):** Standard evaluation order.
- **Frame B (symbol 1):** Swapped evaluation order (e.g., coupling torque before intrinsic frequency at each stage).

**Pros:** Conceptually simplest; directly parallels the `quasi_periodic_step` Frame A/B distinction.  
**Cons:** The "swap" is less clearly defined for RKMK4 than for Strang splitting, where the two operators are explicit.

---

## Experimental Validation

If explored, the proposed validation pipeline would be:

1. **Implement** one of the above approaches as `step_rkmk4_quasi_periodic(K, dt, step_index)`.
2. **Benchmark** against pure RKMK4 using the existing `scripts/compare_quasi_vs_rkmk4.py` framework.
3. **Use the coprime sampler** (`CoprimeSamplerWrapper`) to measure channel discrepancy — the key metric for detecting whether the hybrid method reduces residual drift compared to pure RKMK4.
4. **Compare** manifold preservation (norm deviation), order parameter accuracy, and computational cost.

**Success criterion:** The hybrid method shows measurably lower coprime channel discrepancy than pure RKMK4, while maintaining comparable or better speed and accuracy.

---

## References

- `src/kuramoto/solvers/rotor.py` — `step_quasi_periodic()`, `step_rkmk4()`, `fibonacci_word_symbol()`
- `src/kuramoto/solvers/coprime.py` — `CoprimeSamplerWrapper`, `detect_spectral_drift()`
- `scripts/compare_quasi_vs_rkmk4.py` — Benchmark comparing quasi_periodic vs rkmk4
- Munthe-Kaas, H. (1999). "Runge-Kutta methods on Lie groups." *BIT Numerical Mathematics*, 39(3), 459-475.
- Iserles, A., Munthe-Kaas, H., Zanna, A., & Owren, B. (2000). "Lie-group methods." *Acta Numerica*, 9, 215-283.

---

## Notes

- This idea is **not urgent** — the current `quasi_periodic_step` and `step_rkmk4` methods both perform well for practical Kuramoto simulations.
- The coprime sampler already provides the diagnostic tool needed to validate any improvement.
- This would be a fun theoretical exploration once the preprint on existing methods is complete.
