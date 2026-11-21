"""
kuramoto.analysis.graphs

Re-exports from kuramoto.graphs for adjacency building and graph statistics.
Provides a convenient namespace within the analysis subpackage.

Author: Eigenscribe
Date: November 2026
"""

from __future__ import annotations

from kuramoto.graphs import build_adjacency, graph_stats

__all__: list[str] = ["build_adjacency", "graph_stats"]


# -----------------------------------------------------------------------------------------------------------
# 💨 Smoke tests
# -----------------------------------------------------------------------------------------------------------


def _run_smoke_test() -> None:
    """Quick sanity check that re-exports work correctly."""
    A = build_adjacency(3, None)
    assert A.shape == (3, 3)
    stats = graph_stats(A)
    assert stats["num_edges"] == 3
    print("✅ Analysis graphs smoke test passed.")


# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry point
# -----------------------------------------------------------------------------------------------------------


def main() -> None:
    """Entry point for module-level smoke testing."""
    _run_smoke_test()


if __name__ == "__main__":
    main()
