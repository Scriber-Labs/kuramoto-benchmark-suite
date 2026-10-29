---
sessionId: session-261028-210546-1o3y
---

# Technical Design

## Current Implementation

### Simulation pipeline
- `KuramotoModel.simulate()` in `src/kuramoto/model.py` returns a `KuramotoDataset` after the full integration completes.
- For RK45: uses SciPy's `solve_ivp` — no per-step callback support.
- For rotor solvers: `RotorSolver.simulate()` in `src/kuramoto/solvers/rotor.py` has an explicit loop (lines 1359–1431) where phases are extracted per output timestep. **This is where we'll inject the streaming callback.**

### Export pipeline
- `export_for_dash()` in `src/kuramoto/dash_export.py` takes a completed dataset dict and writes enriched JSON.
- CLI command `dash_export` in `src/kuramoto/cli/commands.py` calls `generate_kuramoto_dataset()` → `export_for_dash()`.

### Key Decision: Streaming via callback, not server
A per-timestep callback is the simplest path to "near-real-time" export. It requires zero infrastructure (no server, no WebSocket). The callback writes one JSON line per timestep to a `.jsonl` file. Dash can poll this file or use `tail -f`.

```
graph LR
    A[RotorSolver.simulate loop] -->|callback per timestep| B[export_for_dash_stream]
    B -->|writes JSONL line| C[output.jsonl]
    C -->|file polling| D[Dash app updates live]
```

## Proposed Changes

### 1. Streaming JSONL export (`src/kuramoto/dash_export.py`)
- Add `TimestepRecord` NamedTuple: `(time, theta, order_parameter, mean_field_phase, locking_fraction)`
- Add `export_for_dash_stream(dataset, output_path, callback=None)`:
  - Writes a header line (metadata as JSON, prefixed with `# ` so it's a comment)
  - For each timestep, calls `callback(t, theta_t, record)` and writes a JSONL line
  - The callback is invoked from the simulation loop (see below)

### 2. Callback hook in simulation (`src/kuramoto/model.py`)
- Add optional `callback: Callable[[float, NDArray], None] | None = None` parameter to `KuramotoModel.simulate()` and `_simulate_rotor()`.
- In `RotorSolver.simulate()` loop (after line 1429 where phases are extracted), invoke `callback(t_out, current_phases)` if provided.
- For RK45: callback is invoked after integration completes with all timesteps at once (best-effort streaming).

### 3. CLI `--stream` flag (`src/kuramoto/cli/commands.py`)
- Add `--stream / -S` boolean flag to `dash_export` command.
- When set: calls `export_for_dash_stream()` with a file-writing callback.
- Output defaults to `.jsonl` extension.

### 4. Dash component template (`examples/ai_generated_notebooks/dash_component_template.py`)
- Self-contained script with two visualizations:
  - **Phase portrait on S¹**: oscillators as points on unit circle, hue = θ/2π, using project's dark theme colors
  - **Adjacency matrix heatmap**: seaborn heatmap of adjacency matrix from JSON metadata
- Supports both JSON (from `kuramoto dash-export`) and JSONL (from `--stream`) formats
- Follows project conventions: type annotations, NumPy docstrings, section dividers, smoke test

### Data Models

**JSONL format (one line per timestep):**
```json
{"t": 0.0, "theta": [0.1, 0.2, ...], "R": 0.35, "psi": 0.12, "locking": 0.0}
{"t": 0.05, "theta": [0.15, 0.25, ...], "R": 0.38, "psi": 0.14, "locking": 0.02}
```

**Header line (comment, starts with `# `):**
```json

# {"metadata": {"n_oscillators": 50, "coupling": 1.5, "solver": "rk45", ...}}

```

# Delivery Steps

### ✓ Step 1: Add streaming JSONL export to dash_export module
Add `export_for_dash_stream()` that writes one JSON line per timestep as the simulation runs. This requires a per-timestep callback hook in the simulation pipeline.

- Add `TimestepRecord` NamedTuple in `src/kuramoto/dash_export.py` with fields: `time`, `theta` (1D slice), `order_parameter`, `mean_field_phase`, `locking_fraction`.
- Add `export_for_dash_stream(dataset, output_path, callback=None)` function that accepts an optional `callback(t, theta_t, record)` fired after each output timestep. Writes a header line (metadata as JSON) followed by one JSONL line per timestep.
- In `src/kuramoto/model.py`, add optional `callback` parameter to `KuramotoModel.simulate()` and `_simulate_rotor()`. In the rotor solver's `simulate()` loop (line ~1428–1431), invoke the callback after each output point is extracted.
- For RK45 (`_simulate_rk45`), the callback is invoked after the full integration completes (SciPy's `solve_ivp` doesn't support per-step callbacks cleanly), so streaming is best-effort for RK45 and full for rotor-based solvers.
- Add tests in `tests/test_dash_export.py` for the streaming format (header + JSONL lines, backward compatibility with the existing JSON export).

### ✓ Step 2: Add --stream flag to kuramoto dash-export CLI
Wire the streaming export into the existing `kuramoto dash-export` CLI command.

- In `src/kuramoto/cli/commands.py`, add `--stream` / `-S` boolean flag to the `dash_export` command.
- When `--stream` is set, call `export_for_dash_stream()` instead of `export_for_dash()`, passing a callback that writes to the output file.
- The output file extension defaults to `.jsonl` when streaming.
- Update the help text to explain the difference between `--stream` (incremental, one line per timestep) and the default (complete JSON at the end).
- Add a smoke test in the CLI to verify the `--stream` flag is recognized.

### ✓ Step 3: Create Dash component template with phase portrait and adjacency heatmap
Create a standalone Python file `examples/ai_generated_notebooks/dash_component_template.py` that can be dropped into the `kuramoto-dash-app` project.

- **Phase portrait on S¹**: Plot oscillators as points on a unit circle, colored by phase angle (hue = θ/2π). Use matplotlib with the existing dark theme from `kuramoto.analysis.viz` (THEME_BG, PROJECT_COLORS). Include a slider/callback to animate through timesteps.
- **Adjacency matrix heatmap**: Color-coded heatmap of the adjacency matrix from the exported JSON metadata. Oscillator indices match the phase portrait. Use seaborn/matplotlib with the project's color palette.
- **Data loading**: Read the enriched JSON format (from `kuramoto dash-export`) or the streaming JSONL format. Include both loaders.
- The template will be a self-contained script with `if __name__ == "__main__"` that demonstrates the plots with sample data. It follows the project's gold standard structure (section dividers, type annotations, NumPy docstrings).
- Place in `examples/ai_generated_notebooks/dash_component_template.py` per the user's convention for AI-generated code.