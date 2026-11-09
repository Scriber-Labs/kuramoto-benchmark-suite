# ✅ TODO: Verification Infrastructure (Methods Section)

- [ ] *MANUALLY* go through LUMO-generated todo list:
      
      # Verification Infrastructure — Preprint Methods TODO
      
      ## Order Parameter Discrepancy Closure
      - [ ] Formally document the root cause of the GA solver's ~0.675 order-parameter
            reading vs. RK45 parity (higher-order parameter flattening effects) in the
            methods text. A reviewer will see this in ten minutes — it needs to be dead
            and buried in writing, not just resolved in notebooks.
        - [ ] Trace back the original observation: locate the notebook/Obsidian/chat log
              where ~0.675 first appeared; reconstruct the debugging sequence and state
              (a) discrepancy as observed, (b) diagnosed cause, (c) fix, (d) post-fix
              parity evidence. If never fully resolved → escalate to top of preprint risks.
      
      ## Metric Taxonomy & Claim Scoping
      - [ ] Build a metric classification table grouping each benchmark metric by
            category: (a) per-step local truncation error, (b) global error accumulation
            over fixed horizons, (c) invariant preservation (manifold drift, energy-like
            quantities), (d) long-time order-parameter fidelity (r(t), sync time),
            (e) wall-clock cost per unit of fidelity.
        - [ ] Record explicitly which method wins each metric; scope the preprint claim
              narrowly: GA wins on (c)/(d), concede per-step LTE to adaptive RK45 (a).
        - [ ] Document wall-clock accounting methodology: fixed hardware statement,
              cost scaling in N and multivector state-dimension overhead vs. real repr.
      
      ## Specialist Baseline Comparisons
      - [ ] Lie-group control: add (or outline) comparison vs. standard Lie-group method
            (Crouch–Grossman or Magnus-type RKMK). Metrics: manifold drift, invariant
            drift, order-parameter RMSE vs. RK45 parity baseline, cost.
        - [ ] Symplectic comparison: scope now (implementation deferrable). Be explicit
              about which regime (first-order gradient flow vs. Hamiltonian formulation)
              symplectic guarantees apply to. Metrics for symplectic comparisons:
              - backward-error / modified-Hamiltonian drift (near-conservation)
              - long-horizon phase error growth (bounded/linear vs. secular/quadratic)
              - exact conservation of quadratic first integrals
              - stability/resonance windows in step size
              - paired with existing metrics: manifold drift, rk45-parity RMSE
                on identical ICs and seeds
      
      ## Literature Due Diligence
      - [ ] MANUAL (non-AI) prior-art search: Clifford/geometric algebra applied to
            Kuramoto / coupled-oscillator simulation specifically.
            - Google Scholar + arXiv (nlin.PS, math-ph, cs.DM, cs.CE)
            - Keyword permutations: "geometric algebra" AND ("Kuramoto",
              "coupled oscillators", "synchronization")
            - Also survey geometric numerical integration literature generally
            - Log search date, databases, queries (reviewers love a search log;
              protects originality claim either way)
            - If prior art found: cite + one-sentence delta statement
      
      ## Validation Battery (automated checks → methods text)
      - [ ] Enumerate automated validation battery as formal checks:
            max_manifold_drift < 1e-10, hf_psd_ratio, rk45_parity_rmse < 5e-2,
            with render_failure_report / assert_all_passed named as the CI gate.
        - [ ] Sanity checks subsection: K = 0 decorrelation, time-reversal invariance,
              phase-rotation invariance, mesh-refinement (convergence-order) study
              confirming observed vs. theoretical order of scheme.
        - [ ] Long-horizon stress experiment: one extended run (10^4–10^5 steps) per
              solver, reporting invariant drift and order-parameter fidelity as functions
              of horizon length. This is where the GA scheme's "punch" shows up —
              design it as an experiment, not an accident.
        - [ ] Reproducibility statement: seeds (set_global_seed), IC distributions,
              RK45 rtol/atol, per-check tolerances.
        - [ ] Clarify "parity" terminology in text: agreement with an independent
              reference solver (NOT spatial sign-inversion parity / grade involution).
        - [ ] Define parity criteria precisely: trajectory-level RMSE over a chosen
              window AND statistical check (same r(∞) plateau) — justify window length.
      
      ## Framing
      - [ ] Present sanity_check + failure_modes notebooks in the methods narrative as
            "Verification Infrastructure" — a reproducible validation pipeline is
            itself a contribution statement.
