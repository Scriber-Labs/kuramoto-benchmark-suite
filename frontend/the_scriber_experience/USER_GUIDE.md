# 🧿 The Scriber Experience (TSE) — Frontend, CLI & Visualization User Guide

`the_scriber_experience` (TSE) is the unified frontend design system, terminal styling framework, Mermaid diagram builder, and scientific visualization bootstrap developed by **Eigenscribe Inc.** and **Scriber Labs**. 

This package provides a standardized, high-contrast visual architecture designed for maximum scannability, ADHD cognitive load optimization, and publication-ready dark-mode aesthetics.

---

## 🧭 1. Architectural Philosophy: The 4-Layer Taxonomy

Following the canonical Eigenscribe structural standard (*"What exists → what you're allowed to call → how it works → proof it works"*), all components follow a strict 4-layer hierarchy:

```
0️⃣ What Exists              -> Layer 1: Design Tokens & Primitives (256-Color Palette, TrueColor Gradients, Hex Tokens)
1️⃣ What You're Allowed to Call -> Layer 2: Public API (Semantic Messages, Diagram Builders, Matplotlib Boostraps)
2️⃣ How It Works             -> Layer 3: Internal Logic & Linear Interpolators (Color Math, Graph Scaffolding)
3️⃣ Proof It Works           -> Layer 4: Interactive Baseline CLI, In-Module Smoke Tests, Boilerplate Generators
```

---

## 📦 2. Installation & Environment Setup

`the_scriber_experience` can be imported into any arbitrary Python project as a standard library via `pip` or `uv`.

### 2.1 Standard Installation via Pip

```bash
# Install directly from wheel / package index
pip install the-scriber-experience

# Or install locally in editable mode from repository root
pip install -e ./frontend/the_scriber_experience
```

### 2.2 Installation with `uv`

```bash
uv add the-scriber-experience
# or for local development:
uv pip install -e ./frontend/the_scriber_experience
```

### 2.3 Core Dependencies
- **Runtime**: `click>=8.0`, `tabulate>=0.9`, `matplotlib>=3.5`, `numpy>=1.23`
- **Optional / Recommended**: `seaborn>=0.12`, `networkx>=3.0`, `pytest>=7.0`

---

## 🚀 3. Quick Start

```python
from the_scriber_experience.cli import cli_banner, cli_info, cli_success, multi_gradient, PRESETS
from the_scriber_experience.theme import MermaidDiagram, save_mermaid_diagram
from the_scriber_experience.visuals import apply_eigenscribe_style, create_styled_figure

# 1. Print a branded gradient banner and semantic messages
cli_banner("MY SCIENTIFIC APPLICATION", "Powered by The Scriber Experience", preset="electric")
cli_info("Initializing simulation pipeline...")
cli_success("All numerical invariants verified successfully.")

# 2. Build a dark-mode Mermaid architecture diagram
diag = MermaidDiagram(title="Data Processing Pipeline", direction="TD")
sg = diag.add_subgraph("Core", "1️⃣ Core Pipeline")
sg.add_node("A", "Input Dataset", style_class="primary")
sg.add_node("B", "Numerical Solver", style_class="success")
diag.add_link("A", "B", "Integrate")
save_mermaid_diagram(diag.render(), "architecture.mmd")

# 3. Create a dark-mode scientific plot
apply_eigenscribe_style()
fig, ax = create_styled_figure(figsize=(8, 4))
ax.plot([0, 1, 2, 3], [0.1, 0.4, 0.8, 0.99], label="Order Parameter r(t)")
ax.set_title("Synchronization Dynamics")
ax.legend()
```

---

## 🛠️ 4. Feature Walkthroughs (Guided by Kuramoto Benchmark Suite)

### 4.1 Feature A: Semantic CLI Output & 256-Color Messaging

The CLI module replaces unstyled `print()` statements with semantic, color-coded levels tailored for rapid status scanning:

| Function | Semantic Role | Eigenscribe Palette Color | Emoji Prefix |
| :--- | :--- | :--- | :--- |
| `cli_info(msg)` | Neutral progress & logs | Bright Sky Cyan (`#00d7ff` / Code 45) | `ℹ️` |
| `cli_success(msg)` | Verified milestones & tests | Neon Spring Green (`#00ff87` / Code 48) | `✅` |
| `cli_warning(msg)` | Non-critical alerts & fallbacks | Gold Amber (`#ffaf00` / Code 214) | `⚠️` |
| `cli_error(msg)` | Validation failures & exceptions | Bright Signal Red (`#ff0000` / Code 196) | `❌` |
| `cli_highlight(msg)` | Key metrics & discoveries | Electric Magenta (`#ff5fff` / Code 207) | `✨` |
| `cli_network(msg)` | Graph & topology states | Medium Purple (`#af5fff` / Code 135) | `🕸️` |
| `cli_quantum(msg)` | Quantum SCF / Statevectors | Electric Cyan (`#00ffff` / Code 51) | `⚛️` |
| `cli_rotor(msg)` | GA Rotor / Multivectors | Vivid Magenta (`#ff00ff` / Code 201) | `🔄` |

#### Example: Benchmark Execution Output
```python
from the_scriber_experience.cli import (
    cli_section,
    cli_info,
    cli_network,
    cli_rotor,
    cli_success,
    cli_table,
    cli_rule,
)

cli_section("1. Network Simulation")
cli_network("Loaded Small-World Graph (N=100, k=4, p=0.1)")
cli_rotor("Advancing Spin(2) rotor states using 4th-Order Lie-RKMK4...")
cli_info("Integration complete across 1,000 steps.")
cli_success("Energy drift < 1e-6 (Noether symmetry preserved).")

# Render tabular metrics
metrics = [
    {"Solver": "Lie-RKMK4", "Steps": 1000, "RMSE": "2.41e-06", "Status": "PASS"},
    {"Solver": "Adaptive DOPRI54", "Steps": 420, "RMSE": "1.18e-06", "Status": "PASS"},
]
cli_table(metrics, headers="keys", title="Solver Verification")
```

---

### 4.2 Feature B: ANSI TrueColor Multi-Stop Linear Gradients

TSE includes a linear RGB TrueColor interpolation engine supporting multi-keyframe gradients and curated brand presets:

```python
from the_scriber_experience.cli import multi_gradient, PRESETS

# Use signature brand presets
print(multi_gradient("Signature Electric", PRESETS["electric"]))
print(multi_gradient("Cosmic Horizon", PRESETS["eigenscribe-1"]))
print(multi_gradient("Solar Sunset", PRESETS["sunset"]))
print(multi_gradient("Deep Forest", PRESETS["forest"]))
print(multi_gradient("Midnight Cosmic", PRESETS["midnight"]))
print(multi_gradient("Quantum Aurora", PRESETS["aurora"]))
print(multi_gradient("Cyberpunk Neon", PRESETS["cyberpunk"]))

# Custom multi-stop gradients with arbitrary hex colors
custom_stops = ["#00f0ff", "#7000ff", "#ff007b", "#ffe600"]
print(multi_gradient("Custom 4-Keyframe Gradient", colors=custom_stops, bold=True))
```

---

### 4.3 Feature C: Baseline CLI User Interface

The `the_scriber_experience.cli.baseline` module delivers a complete baseline terminal application with interactive menus, palette swatches, and command dispatching:

#### Running via Command-Line
```bash
# Launch interactive navigation menu
python -m the_scriber_experience.cli.baseline interactive

# Display full Eigenscribe 256-color palette swatches
python -m the_scriber_experience.cli.baseline palette

# Display TrueColor gradient presets
python -m the_scriber_experience.cli.baseline gradient

# Run full system showcase
python -m the_scriber_experience.cli.baseline showcase
```

#### Embedding into External Tools
```python
from the_scriber_experience.cli.baseline import BaselineCLI

cli = BaselineCLI(
    app_name="KURAMOTO BENCHMARK SUITE",
    tagline="Oscillator Network Simulation & Analysis",
    version="1.0.0",
    preset="electric",
    width=64,
)
cli.render_welcome()
```

---

### 4.4 Feature D: Eigenscribe Mermaid Diagram Generation

TSE's `theme.py` programmatically builds Mermaid.js diagrams formatted with Eigenscribe dark-mode tokens (`#0D1117` background, `#14B5FF` cyan lines, `'Aclonica'` font, and MathJax styling):

```python
from the_scriber_experience.theme import (
    MermaidDiagram,
    create_boilerplate_diagram,
    save_mermaid_diagram,
)

# 1. Build a custom layered diagram
diag = MermaidDiagram(title="Kuramoto Architecture", direction="TD")

# Define Layer 1: Client API
l1 = diag.add_subgraph("API_Layer", "1️⃣ Client & High-Level API")
l1.add_node("CLI", "CLI Suite (kuramoto)", shape="rect", style_class="primary")
l1.add_node("API", "generate_kuramoto_dataset()", shape="rect", style_class="primary")

# Define Layer 2: Solvers
l2 = diag.add_subgraph("Solvers", "2️⃣ Numerical Solvers")
l2.add_node("ODE", "Classical RK45", shape="rect", style_class="success")
l2.add_node("Rotor", "GA Lie-RKMK4", shape="rect", style_class="success")
l2.add_node("Quantum", "Quantum SCF Statevector", shape="rect", style_class="success")

# Connect nodes
diag.add_link("CLI", "ODE")
diag.add_link("API", "Rotor")
diag.add_link("API", "Quantum")

# Render & Export
mermaid_source = diag.render()
save_mermaid_diagram(mermaid_source, "docs/architecture.mmd")

# 2. Export canonical boilerplate diagram
boilerplate_str = create_boilerplate_diagram()
save_mermaid_diagram(boilerplate_str, "boilerplates/architecture_boilerplate.mmd")
```

---

### 4.5 Feature E: Scientific Visualization & Pyplot Theme Bootstrap

TSE configures Matplotlib and Seaborn with publication-ready dark styling, cyclic phase colormaps, and 10-node distinct color cycles:

```python
import numpy as np
from the_scriber_experience.visuals import (
    apply_eigenscribe_style,
    create_styled_figure,
    plot_phase_series,
    plot_order_parameter,
    phase_cmap,
)

# Apply global dark mode rcParams
apply_eigenscribe_style()

# Generate synthetic simulation data
time = np.linspace(0.0, 10.0, 200)
theta = np.sin(np.outer(time, [1.0, 1.2, 1.5, 1.8]))
r = 0.5 + 0.45 * (1.0 - np.exp(-time / 2.0))

# Create side-by-side styled subplots
fig, (ax1, ax2) = create_styled_figure(nrows=1, ncols=2, figsize=(14, 5))

# Plot multi-oscillator phase trajectories
plot_phase_series(time, theta, title="Phase Trajectories θ_i(t)", ax=ax1)

# Plot order parameter synchronization curve
plot_order_parameter(time, r, title="Global Synchronization r(t)", ax=ax2)

fig.tight_layout()
fig.savefig("plots/sync_dynamics.png", dpi=300)
```

---

## 🎨 5. Design Token Reference

| Token Name | Hex Value / Code | Semantic Role |
| :--- | :--- | :--- |
| `COLOR_BG` | `#0d1117` | Canvas base surface |
| `COLOR_SURFACE` | `#161b22` | Card & axes background |
| `COLOR_SURFACE_ELEVATED` | `#21262d` | Floating menus & legend background |
| `COLOR_BORDER` | `#30363d` | Frame & cluster borders |
| `COLOR_GRID` | `#21262d` | Gridline accent |
| `COLOR_TEXT` | `#f0f6fc` | Primary crisp white text |
| `COLOR_TEXT_MUTED` | `#8b949e` | Secondary / axis label text |
| `EIGEN_CYAN` | `#00e8ff` | Primary interactive / focal cyan |
| `EIGEN_SKY` | `#14b5ff` | Brand blue / primary lines |
| `EIGEN_BLUE` | `#3a98ff` | Secondary active state |
| `EIGEN_PURPLE` | `#7952f5` | Structural / function violet |

---

## 🧪 6. Testing & In-Module Verification

Every module in `the_scriber_experience` includes an in-module self-test function `_run_smoke_test()`:

```bash
# Run all TSE unit and smoke tests
python -c "import sys; sys.path.insert(0, 'frontend'); from the_scriber_experience.cli import gradient, messaging, baseline; from the_scriber_experience import theme, visuals; gradient._run_smoke_test(); messaging._run_smoke_test(); baseline._run_smoke_test(); theme._run_smoke_test(); visuals._run_smoke_test()"
```

---

🔬 *Eigenscribe Inc. & Scriber Labs. Part of The Scriber Experience Framework.*
