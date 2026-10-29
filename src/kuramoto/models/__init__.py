"""
kuramoto.models — Specialized model variants beyond the core KuramotoModel.

This subpackage houses alternative model formulations with custom frequency
distributions, topologies, or dynamic operators that extend the standard
Kuramoto framework.
"""

from __future__ import annotations

from kuramoto.models.zbw_generator import ZBWKuramotoDataGenerator

__all__ = ["ZBWKuramotoDataGenerator"]
