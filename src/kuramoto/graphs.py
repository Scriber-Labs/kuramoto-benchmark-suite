"""
kuramoto.graphs

Graph adjacency matrix construction and basic graph statistics
for Kuramoto simulation topologies.

Author: Eigenscribe
Date: November 2026
"""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray

# -----------------------------------------------------------------------------------------------------------
# 1️⃣ Core definitions
# -----------------------------------------------------------------------------------------------------------


def build_adjacency(
    n: int, adjacency: NDArray[np.floating] | None
) -> NDArray[np.floating]:
    """
    Build an adjacency matrix for a Kuramoto graph topology.

    If no adjacency matrix is provided, a fully connected graph (excluding
    self-loops) is created.

    Parameters
    ----------
    n : int
        Number of nodes in the graph.
    adjacency : NDArray[np.floating] | None
        Adjacency matrix of the graph of interest. If None, a fully connected
        graph is created.

    Returns
    -------
    NDArray[np.floating]
        The adjacency matrix of the graph, shape ``(n, n)``.
    """
    if adjacency is None:
        A = np.ones((n, n), dtype=np.float64) - np.eye(n, dtype=np.float64)
    else:
        A = adjacency
    return A


# -----------------------------------------------------------------------------------------------------------
# 2️⃣ Public API
# -----------------------------------------------------------------------------------------------------------


def graph_stats(A: NDArray[np.floating]) -> dict[str, Any]:
    """
    Compute basic statistics of the graph represented by the adjacency matrix.

    Parameters
    ----------
    A : NDArray[np.floating]
        Adjacency matrix of the graph, shape ``(n, n)``.

    Returns
    -------
    dict[str, Any]
        A dictionary containing:
        - ``num_edges``: number of undirected edges.
        - ``density``: graph density (fraction of possible edges present).
        - ``is_connected``: boolean flag indicating if the graph is connected.
        - ``avg_degree``: average node degree.
    """
    n = A.shape[0]
    edges = np.count_nonzero(A) / 2  # Undirected graph
    avg_degree = float(np.sum(A)) / n
    density = float((2 * edges) / (n * (n - 1))) if n > 1 else 0.0
    return {
        "num_edges": int(edges),
        "density": density,
        "is_connected": edges >= n - 1,
        "avg_degree": avg_degree,
    }


# -----------------------------------------------------------------------------------------------------------
# 💨 Smoke tests
# -----------------------------------------------------------------------------------------------------------


def _run_smoke_test() -> None:
    """Quick sanity check for graph utilities."""
    # Test fully connected graph
    A = build_adjacency(5, None)
    assert A.shape == (5, 5)
    assert np.all(np.diag(A) == 0.0), "Diagonal should be zero"
    stats = graph_stats(A)
    assert stats["num_edges"] == 10
    assert stats["density"] == 1.0
    assert stats["is_connected"] is True

    # Test custom adjacency
    custom = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]], dtype=float)
    A2 = build_adjacency(3, custom)
    stats2 = graph_stats(A2)
    assert stats2["num_edges"] == 2
    assert stats2["avg_degree"] == 4.0 / 3

    print("✅ Graphs smoke test passed.")


# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry point
# -----------------------------------------------------------------------------------------------------------


def main() -> None:
    """Entry point for module-level smoke testing."""
    _run_smoke_test()


if __name__ == "__main__":
    main()
