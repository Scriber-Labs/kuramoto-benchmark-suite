# 🏅 Gold Standard Python Script Template 
Overall structure (with numbered emoji sections)
```python
"""
<filename>.py

Script description and theoretical summary.

Author: Eigenscribe
Review status: Reviewed and maintained by Eigenscribe.
Date: May 2026
"""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from typing import Final, Protocol, TypeAlias

# -----------------------------------------------------------------------------------------------------------
# 🎭 Typing helpers / protocols / constants (0️⃣ What exists)
# -----------------------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------------------
# 1️⃣ Core definitions
# -----------------------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------------------
# 2️⃣ Public API (functions users are meant to call)
# -----------------------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------------------
# 3️⃣ Private helpers
# -----------------------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------------------
# 💨 Smoke tests / example usage
# -----------------------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry point
# -----------------------------------------------------------------------------------------------------------
```

>[!important] 👍 Rule of Thumb
> If someone scrolls your file top-to-bottom, the conceptual story should flow:
> 	"What exists -> what you're allowed to call -> how it works -> proof it works"

>[!important]   🗝️ Key Features
>1. Number-emoji sectioning
>     - Helps to make long scripts scannable
>     - Meant to be used as semantic anchors, not decoration
>2. `if name=="main"`
> 	- Used only for:
> 		- smoke tests		   
> 		- minimal demonstrations
> 		- sanity checks
> 		- Never for:
> 			- training loops
> 			- hyperparameter sweeps
> 			- long-running jobs
>3. `def main() -> None:`
> 	- Always exists
> 	- Orchestrates section 4
> 	- Never contains math or logic directly
> 		```python
> 		def main() -> None:
> 		    run_smoke_test()
> 		```
>
>4. Standardized File Header Metadata
>    - Every source module and script must include a canonical header docstring:
>      ```python
>      """
>      <filename>.py
>
>      <Description of module function and physics/math>.
>
>      Author: Eigenscribe
>      Review status: Reviewed and maintained by Eigenscribe.
>      Date: May 2026
>      """
>      ```
>
>5. Type Annotations & Signatures (Python 3.10+)
>    - Always include `from __future__ import annotations` at the top of each file.
>    - Use PEP 604 union types: `float | NDArray`, `str | None` (avoid legacy `Optional`, `Union`).
>    - Use built-in generics: `dict[str, Any]`, `list[str]`, `tuple[int, ...]` (avoid `Dict`, `List`, `Tuple`).
>    - Use `NDArray[np.floating]` or `NDArray[np.float64]` for NumPy arrays.
>    - Use `Final` for constants:
> 		```python 
> 		DEFAULT_SEED: Final[int] = 27
> 		omega: Final[float | NDArray] = 1.0
> 		```
>    - Standardize solver call signatures: `simulate(self, K: float, t_eval: NDArray, ...)` returning `(t_eval, phases)`.
>
>6. NumPy-style docstrings with explicit dimensions
>    - These should always appear on: 
> 	    - public functions
> 	    - public classes
> 	    - nontrivial private helpers
>    - Minimal viable structure with dimension specs:
>    ```python
>    """
>    Parameters
>    ----------
>    phases : NDArray[np.float64]
>        Active phase array with shape `(n_oscillators,)` or `(n_timesteps, n_oscillators)`.
>    omega : NDArray[np.float64]
>        Natural frequency vector with shape `(n_oscillators,)`.
>    dt : float
>        Time step size.
>    
>    Returns
>    -------
>    NDArray[np.float64]
>        Updated state array with shape matching `phases`.
>    """
>    ```

>[!important] 📦 Package Hygiene
>7. Explicit `__init__.py` exports
>    - Every package `__init__.py` should define an explicit `__all__` list.
>    - Either populate with proper re-exports or remove the file if the subpackage is never imported as a whole.
>    - Avoid empty `__init__.py` files that silently expose nothing.

>[!important] 🚫 Import Discipline
>8. No wildcard imports
>    - Never use `from module import *` in production code.
>    - Always import explicitly: `from module import func_a, func_b, ClassC`.
>    - Wildcard imports pollute the namespace and obscure which symbols are actually used.

>[!important] 🎯 Single Source of Truth
>9. Centralize shared constants
>    - Any string, enum, or list used in 2+ files must live in a single canonical module (e.g. `kuramoto.solver_types`).
>    - Example: solver aliases, CLI choices, configuration keys — define once, import everywhere.
>    - Eliminates duplication and makes maintenance a one-line change.

>[!important] 🛡️ Path Hygiene
>10. Never mutate `sys.path` at import time
>    - Do not append `sys.path` inside `try/except` import blocks as a fallback.
>    - Properly installed packages should resolve via relative imports.
>    - If a module needs to work standalone, use a launcher script or entry point instead.

>[!important] 🧹 Project Housekeeping
>11. Maintain a `.gitignore`
>    - Exclude generated artifacts: `*.bak`, `*.pyc`, `__pycache__/`, `.idea/`, `.vscode/`.
>    - Exclude data files: `*.npz`, `*.h5`, `plots/`, `logs/`.
>    - Prevents accidental commits of stale or large files.

>[!important] 🎲 Random Number Generation
>12. Use modern NumPy RNG consistently
>    - Prefer `np.random.default_rng(seed)` over legacy `np.random.seed()`.
>    - The legacy API seeds a global `RandomState` which is inconsistent with the modern `Generator` API.
>    - Pass explicit `seed` parameters in tests for reproducibility.

>[!important] 🧪 Test Coverage Targets
>13. Aim for proportional test coverage
>    - Every public module should have at least one dedicated test file.
>    - Bug fixes: create a reproducer test that fails before the fix.
>    - New features: add tests proportional to complexity.
>    - Target 70%+ coverage for core logic modules.

>[!important] ⚡ Environment & Dependency Management
>14. Use `uv` and maintain `pyproject.toml`
>    - Use `uv` as the virtual environment and package management tool.
>    - Keep `pyproject.toml` updated with dependencies, tools, and project metadata.
>    - If `pyproject.toml` does not exist in a project/repository, create one tailored to the needs and requirements of the project.

---

# 🏅 Gold Standard CSS Template
Overall structure (with numbered emoji sections matching Scriber Core Design System)
```css
/*
=============================================================================================================
🏅 Gold Standard CSS Template - Scriber Core Design System
Narrative Flow: "Tokens & Theme -> Resets & Base -> Public Components -> Overrides & Math -> Responsive"
=============================================================================================================
*/

/* ----------------------------------------------------------------------------------------------------------- */
/* 0️⃣ 🎨 Design Tokens, Constants & CSS Variables (What exists)                                               */
/* ----------------------------------------------------------------------------------------------------------- */
:root {
    /* Color Palette */
    --color-bg: #0d1117;
    --color-surface: #161b22;
    --color-primary: #14b5ff;
    --color-secondary: #7952f5;
    --color-accent-purple: #a855f7;
    --color-accent-green: #31ff48;
    --color-text: #f0f6fc;
    --color-muted: #8b949e;
    --color-math: #00f5db;

    /* Multi-stop & Level-Specific Gradients (Color-Changing Spectrum with Pink Accent) */
    --heading-gradient-1: linear-gradient(135deg, #00ffee 0%, #14b5ff 25%, #7952f5 55%, #f72585 80%, #00ffee 100%);
    --heading-gradient-2: linear-gradient(135deg, #14b5ff 0%, #5280ff 30%, #a855f7 60%, #f72585 85%, #14b5ff 100%);
    --heading-gradient-3: linear-gradient(135deg, #00f5db 0%, #22f792 25%, #14b5ff 55%, #9d4edd 80%, #f72585 92%, #00f5db 100%);
    --heading-gradient-4: linear-gradient(135deg, #7952f5 0%, #a855f7 30%, #f72585 60%, #00ffee 85%, #7952f5 100%);

    /* Typography */
    --font-aclonica: 'Aclonica', sans-serif;
    --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    --font-mono: 'Fira Code', 'JetBrains Mono', monospace;
    --font-math: "Times New Roman", "Computer Modern", serif;

    /* Spacing & Radii */
    --space-xs: 4px;
    --space-sm: 8px;
    --space-md: 16px;
    --space-lg: 24px;
    --space-xl: 32px;
    --radius-md: 8px;
    --radius-lg: 16px;
    --radius-pill: 50px;

    /* Glassmorphism */
    --glass-bg: rgba(13, 17, 23, 0.65);
    --glass-border: rgba(255, 255, 255, 0.12);
}

/* ----------------------------------------------------------------------------------------------------------- */
/* 1️⃣ 🧱 Base Resets, Typography & Global Layout (Structural foundation)                                      */
/* ----------------------------------------------------------------------------------------------------------- */
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 0;
    background-color: var(--color-bg);
    color: var(--color-text);
    font-family: var(--font-aclonica);
}

.emoji {
    background: none !important;
    color: initial !important;
    -webkit-background-clip: initial !important;
    background-clip: initial !important;
    -webkit-text-fill-color: initial !important;
    display: inline-block;
}

/* ==== Headings with Color-Changing Animated Gradients ==== */
@keyframes header-gradient-shift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

h1, h2, h3, h4 {
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: header-gradient-shift 8s ease-in-out infinite;
    transition: filter 0.3s ease;
}

h1 { background-image: var(--heading-gradient-1); }
h2 { background-image: var(--heading-gradient-2); }
h3 { background-image: var(--heading-gradient-3); }
h4 { background-image: var(--heading-gradient-4); }

h1:hover, h2:hover, h3:hover, h4:hover {
    animation-duration: 4s;
    filter: brightness(1.25) drop-shadow(0 0 10px rgba(0, 255, 238, 0.3));
}

/* ----------------------------------------------------------------------------------------------------------- */
/* 2️⃣ 🧩 Core UI Components (Buttons, Cards, Glass Panels, Search)                                            */
/* ----------------------------------------------------------------------------------------------------------- */
.btn {
    background-image: linear-gradient(135deg, #00e8ff 0%, #14b5ff 40%, #7952f5 100%);
    background-size: 200% auto;
    border-radius: var(--radius-pill);
    color: white !important;
    font-weight: 700;
    cursor: pointer;
    transition: background-position 0.5s ease, transform 0.3s ease, filter 0.3s ease;
}

.btn:hover {
    background-position: right center;
    filter: brightness(1.2);
    transform: scale(1.03);
}

.glass-card {
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    backdrop-filter: blur(12px);
    border-radius: var(--radius-lg);
}

/* ----------------------------------------------------------------------------------------------------------- */
/* 3️⃣ 📐 Domain Overrides & Mathematical Typography (KaTeX, MathJax, Terminals)                               */
/* ----------------------------------------------------------------------------------------------------------- */
.code-terminal {
    background: rgba(13, 17, 23, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: var(--radius-md);
    backdrop-filter: blur(12px);
}

.cli-prompt { color: #00ffee; font-weight: bold; }
.cli-keyword { color: #c084fc; font-weight: 600; }
.cli-function { color: #38bdf8; font-weight: 600; }
.cli-string { color: #4ade80; }

.katex, .MathJax, mjx-container {
    font-family: var(--font-math) !important;
    color: var(--color-math);
}

/* ----------------------------------------------------------------------------------------------------------- */
/* 4️⃣ 📱 Responsive Breakpoints & Media Queries (Device adaptations)                                          */
/* ----------------------------------------------------------------------------------------------------------- */
@media (max-width: 768px) {
    .container {
        padding: var(--space-sm);
    }
}
```

>[!important] 👍 CSS Rule of Thumb
> Narrative Flow: `0️⃣ Tokens/Variables -> 1️⃣ Resets/Layout -> 2️⃣ Core Components -> 3️⃣ Overrides/Math -> 4️⃣ Responsive`
> 1. Use numbered emoji section dividers as semantic anchors for scannability.
> 2. Wrap emojis in `.emoji` to isolate them from gradient text masking and preserve natural colors.
> 3. Implement level-specific heading gradients infused with cyan, violet, and subtle pink accent stops, paired with continuous animated color-changing gradient flows.
> 4. Use glassmorphic `.code-terminal` containers with traffic light dot headers and attention-friendly semantic CLI syntax tokens.
> 5. Preserve mathematical typography isolation (`var(--font-math)`) for KaTeX / MathJax containers.
