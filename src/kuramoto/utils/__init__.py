# src/kuramoto/utils/__init__.py
"""
kuramoto.utils

Lightweight, project-agnostic helper package.

These helpers deliberately avoid depending on any project-specific modules so
they are easy to reuse in notebooks and future projects. The public helpers are
re-exported here so that existing imports such as
``from kuramoto.utils import get_rng, set_global_seed, wrap_phase`` keep working
after ``utils`` was promoted from a flat module to a package.

Submodules
----------
seeding
    Canonical RNG, seeding and reproducibility helpers (single source of truth
    for random-number generation).
phase
    Phase-angle helpers (e.g. :func:`wrap_phase`).
"""

from __future__ import annotations

from .phase import wrap_phase
from .seeding import (
    DEFAULT_SEED,
    derive_seed,
    get_rng,
    resolve_rng,
    set_global_seed,
    spawn_generators,
)

__all__ = [
    "DEFAULT_SEED",
    "derive_seed",
    "get_rng",
    "resolve_rng",
    "set_global_seed",
    "spawn_generators",
    "wrap_phase",
]
