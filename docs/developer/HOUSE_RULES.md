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
