# src/kuramoto/utils/seeding.py
# Canonical source: scriber-core/templates/seeding.py
# Synced: 2026-10-23 -- do not edit locally without syncing upstream
"""
seeding.py

Canonical RNG, seeding and reproducibility helpers for the Kuramoto benchmark
suite.

This module is the *single source of truth* for random-number generation. It
exists to eliminate stochastic errors and guarantee bitwise reproducibility
across environments by enforcing the project seeding mandate:

- Only the modern ``numpy.random.Generator`` API is used. The legacy global
  state mutations ``np.random.seed`` / ``random.seed`` are never called.
- Every other module obtains randomness through the helpers exported here
  (``get_rng``, ``set_global_seed``, ``resolve_rng``, ``derive_seed``,
  ``spawn_generators``) rather than touching ``np.random.*`` directly.

Run ``python -m kuramoto.utils.seeding`` to execute the reproducibility
self-check.

Author: Eigenscribe
Date: October 2026
"""

from __future__ import annotations

import hashlib
import sys
from typing import Final

import numpy as np

__all__ = [
    "DEFAULT_SEED",
    "get_rng",
    "set_global_seed",
    "derive_seed",
    "spawn_generators",
    "resolve_rng",
]

# ------------------------------------------------------------------------------ #
# 0️⃣ Definitions, Constants & Types
# ------------------------------------------------------------------------------ #

#: Project-wide default seed, used when a reproducible stream is requested but no
#: explicit seed is supplied.
DEFAULT_SEED: Final[int] = 27

#: Process-global canonical generator registered by :func:`set_global_seed`.
_GLOBAL_RNG: np.random.Generator | None = None


# ------------------------------------------------------------------------------ #
# 1️⃣ Public API
# ------------------------------------------------------------------------------ #


def get_rng(seed: int | None = None) -> np.random.Generator:
    """
    Return a fresh modern :class:`numpy.random.Generator`.

    Parameters
    ----------
    seed : int or None, optional
        Seed for the generator. Identical seeds yield bitwise-identical
        streams. If ``None``, the generator is seeded from system entropy and
        is therefore not reproducible across runs.

    Returns
    -------
    numpy.random.Generator
        A new, independent generator instance.
    """
    return np.random.default_rng(seed)


def set_global_seed(
    seed: int = DEFAULT_SEED,
    *,
    deterministic: bool = False,
) -> np.random.Generator:
    """
    Seed and return the process-global canonical generator.

    Unlike the prohibited legacy ``np.random.seed`` / ``random.seed`` pattern,
    this function does **not** mutate any interpreter-global RNG state. It builds
    a fresh ``Generator`` from ``seed``, registers it as the module-level default
    (retrievable and reused across the process), and returns it for immediate
    use.

    Parameters
    ----------
    seed : int, default ``DEFAULT_SEED``
        Integer seed used to initialize the generator.
    deterministic : bool, default ``False``
        Accepted for backward compatibility only; it has no effect. Modern
        ``Generator`` streams are already fully deterministic for a given seed.

    Returns
    -------
    numpy.random.Generator
        The freshly seeded, process-global canonical generator.
    """
    global _GLOBAL_RNG
    _GLOBAL_RNG = np.random.default_rng(seed)
    return _GLOBAL_RNG


def derive_seed(seed: int, label: str) -> int:
    """
    Deterministically derive a stable child seed from a base seed and a label.

    The mapping is stable across processes and Python versions because it uses
    SHA-256 rather than the per-process-salted built-in :func:`hash`. Distinct
    labels map to distinct child seeds with overwhelming probability, which lets
    callers keep logically separate random streams (e.g. ``"frequencies"`` vs
    ``"noise"``) from the same base seed.

    Parameters
    ----------
    seed : int
        Base integer seed.
    label : str
        Human-readable stream label.

    Returns
    -------
    int
        A 64-bit non-negative integer derived from ``(seed, label)``.
    """
    digest = hashlib.sha256(f"{int(seed)}:{label}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def spawn_generators(seed: int, n: int) -> list[np.random.Generator]:
    """
    Spawn ``n`` statistically independent generators from a single seed.

    Uses :class:`numpy.random.SeedSequence` spawning, the recommended way to
    obtain non-overlapping, independent streams for parallel or multi-component
    work.

    Parameters
    ----------
    seed : int
        Base seed for the root :class:`numpy.random.SeedSequence`.
    n : int
        Number of child generators to create (``n >= 0``).

    Returns
    -------
    list of numpy.random.Generator
        ``n`` independent generators.

    Raises
    ------
    ValueError
        If ``n`` is negative.
    """
    if n < 0:
        raise ValueError(f"n must be non-negative, got n={n}")
    root = np.random.SeedSequence(seed)
    return [np.random.default_rng(child) for child in root.spawn(n)]


def resolve_rng(
    rng: np.random.Generator | None = None,
    seed: int | None = None,
) -> np.random.Generator:
    """
    Resolve the generator a numerical routine should use.

    Dependency-injection helper implementing the project RNG-injection policy:
    an explicitly supplied ``rng`` always wins; otherwise a fresh generator is
    built from ``seed`` (system entropy when ``seed`` is ``None``).

    Parameters
    ----------
    rng : numpy.random.Generator or None, optional
        Explicitly injected generator. Returned unchanged when provided.
    seed : int or None, optional
        Fallback seed used only when ``rng`` is ``None``.

    Returns
    -------
    numpy.random.Generator
        The generator the caller should thread through its stochastic steps.
    """
    if rng is not None:
        return rng
    return get_rng(seed)


# ------------------------------------------------------------------------------ #
# 💨 Smoke tests / example usage
# ------------------------------------------------------------------------------ #


def _self_check() -> None:
    """💨 Smoke test: reproducibility, label separation, stream independence."""
    print("💨 Running seeding self-check...")

    seed = DEFAULT_SEED

    # Test 1: global seeding reproducibility
    a = set_global_seed(seed)
    b = set_global_seed(seed)
    assert np.array_equal(
        a.random(10), b.random(10)
    ), "Global seeds are not reproducible."

    # Test 2: derive_seed stability and label separation
    assert derive_seed(seed + 10, "x") == derive_seed(
        seed + 10, "x"
    ), "derive_seed unstable"
    assert derive_seed(seed + 10, "x") != derive_seed(seed + 10, "y"), "labels collided"

    # Test 3: spawned streams are independent
    draws = [g.random(10) for g in spawn_generators(7, 4)]
    for i in range(len(draws)):
        for j in range(i + 1, len(draws)):
            assert not np.array_equal(draws[i], draws[j]), "streams not independent"

    # Test 4: resolve_rng honours injection and falls back to a seed
    injected = get_rng(seed)
    assert (
        resolve_rng(injected) is injected
    ), "resolve_rng must return the injected generator"
    assert np.array_equal(
        resolve_rng(seed=seed).random(5),
        get_rng(seed).random(5),
    ), "resolve_rng seed fallback not reproducible"

    print("✅ Seeding self-check passed.")


# ------------------------------------------------------------------------------ #
# 🔥 Entry point
# ------------------------------------------------------------------------------ #


def main() -> None:
    """Main entry point: run the seeding self-check."""
    # Make the emoji-rich self-check output robust on legacy Windows consoles
    # (e.g. cp1252) so ``python -m kuramoto.utils.seeding`` never dies on an
    # encoding error. Only the entry point touches the streams -- importing the
    # module as a library leaves stdout/stderr untouched.
    for _stream in (sys.stdout, sys.stderr):
        _reconfigure = getattr(_stream, "reconfigure", None)
        if _reconfigure is not None:
            try:
                _reconfigure(encoding="utf-8")
            except (ValueError, OSError):
                pass
    _self_check()


if __name__ == "__main__":
    main()
