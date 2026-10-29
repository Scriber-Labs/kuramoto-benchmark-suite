# 🏅 Gold Standard Python Script Template 
Overall structure (with numbered emoji sections)
```python
"""
example.py

Script description

Author:
Date:
"""
# imports and typing

# -----------------------------------------------------------------------------------------------------------
# 🎭 Typing helpers / protocols / constants (if needed)
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
> 2. `if name=="main"`
> 	- Used only for:
> 		- smoke tests		   
> 		- minimal demonstrations
> 		- sanity checks
> 		- Never for:
> 			- training loops
> 			- hyperparameter sweeps
> 			- long-running jobs
> 3. `def main() --> None:`
> 	- Always exists
> 	- Orchestrates section 4
> 	- Never contains math or logic directly
> 		```python
> 		def main() --> None:
> 		    run_smoke_test()
> 		```
>
>4. "Big functions" to bundle logic
> 
>5. Type annotations everywhere (but sanely)
>     - Key norms to lock in:
> 	    - Use `Tensor`, not `torch.Tensor`, in signatures.
> 	    - Annotate scalars (`float | Tensor`) when physically meaningful.	
> 	    - Use Final for constants:
> 		    ```python 
> 		     omega: float | Tensor = 1.0
> 		     ```
> 		     
>     >[!note] 📝Want scripts to read like math and code.
>
>1. NumPy-style docstrings
>     - These should always appear on: 
> 	    - public functions
> 	    - public classes
> 	    - nontrivial private helpers
>     - Minimal viable structure:
>     ```python
>     """
>     Parameters
>     -----------
>     name : type
> 	    Description.
>     
>     Returns
>     -------
>     Type
> 	    Description.
> 	"""
> 	```

>[!important] 📦 Package Hygiene
>6. Explicit `__init__.py` exports
>    - Every package `__init__.py` should define an explicit `__all__` list.
>    - Either populate with proper re-exports or remove the file if the subpackage is never imported as a whole.
>    - Avoid empty `__init__.py` files that silently expose nothing.

>[!important] 🚫 Import Discipline
>7. No wildcard imports
>    - Never use `from module import *` in production code.
>    - Always import explicitly: `from module import func_a, func_b, ClassC`.
>    - Wildcard imports pollute the namespace and obscure which symbols are actually used.

>[!important] 🎯 Single Source of Truth
>8. Centralize shared constants
>    - Any string, enum, or list used in 2+ files must live in a single canonical module.
>    - Example: solver aliases, CLI choices, configuration keys — define once, import everywhere.
>    - Eliminates duplication and makes maintenance a one-line change.

>[!important] 🛡️ Path Hygiene
>9. Never mutate `sys.path` at import time
>    - Do not append `sys.path` inside `try/except` import blocks as a fallback.
>    - Properly installed packages should resolve via relative imports.
>    - If a module needs to work standalone, use a launcher script or entry point instead.

>[!important] 🧹 Project Housekeeping
>10. Maintain a `.gitignore`
>    - Exclude generated artifacts: `*.bak`, `*.pyc`, `__pycache__/`, `.idea/`, `.vscode/`.
>    - Exclude data files: `*.npz`, `*.h5`, `plots/`, `logs/`.
>    - Prevents accidental commits of stale or large files.

>[!important] 🎲 Random Number Generation
>11. Use modern NumPy RNG consistently
>    - Prefer `np.random.default_rng(seed)` over legacy `np.random.seed()`.
>    - The legacy API seeds a global `RandomState` which is inconsistent with the modern `Generator` API.
>    - Pass explicit `seed` parameters in tests for reproducibility.

>[!important] 🧪 Test Coverage Targets
>12. Aim for proportional test coverage
>    - Every public module should have at least one dedicated test file.
>    - Bug fixes: create a reproducer test that fails before the fix.
>    - New features: add tests proportional to complexity.
>    - Target 70%+ coverage for core logic modules.

>[!important] ⚡ Environment & Dependency Management
>13. Use `uv` and maintain `pyproject.toml`
>    - Use `uv` as the virtual environment and package management tool.
>    - Keep `pyproject.toml` updated with dependencies, tools, and project metadata.
>    - If `pyproject.toml` does not exist in a project/repository, create one tailored to the needs and requirements of the project.



