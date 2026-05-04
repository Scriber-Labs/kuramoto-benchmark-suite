# 🏅 Gold Standard Python Script Template 
Overall structure (with numbered emoji sections)
```python
"""
example.py

Script descriptiion

Author:
Date:
"""
# imports and typing

# -----------------------------------------------------------------------------------------------------------
# 0️⃣ Typing helpers / protocols / constants (if needed)
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
# 4️⃣ Smoke tests / example usage
# -----------------------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------------------
# 5️⃣ Entry point
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



