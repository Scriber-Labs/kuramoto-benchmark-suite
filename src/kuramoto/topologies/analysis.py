"""
analysis.py

Advanced topological analysis for Kuramoto networks.
Provides tools for computing graph invariants like the chromatic polynomial.

Author: Eigenscribe
Date: May 2026
"""

from __future__ import annotations

import networkx as nx
import numpy as np
from typing import Dict, Any, Final
from numpy.typing import NDArray

from sympy import symbols

# -----------------------------------------------------------------------------------------------------------
# 0️⃣ Type aliases
# -----------------------------------------------------------------------------------------------------------
AdjacencyMatrix = NDArray[np.floating]

# -----------------------------------------------------------------------------------------------------------
# 1️⃣ Core definitions
# -----------------------------------------------------------------------------------------------------------

def compute_chromatic_polynomial(G: nx.Graph) -> Dict[int, int]:
    """
    Compute the chromatic polynomial of a graph.
    
    The chromatic polynomial P(G, k) counts the number of ways to color 
    the vertices of G with k colors such that no two adjacent vertices 
    share the same color.

    Parameters
    ----------
    G : nx.Graph
        The input graph.

    Returns
    -------
    Dict[int, int]
        Dictionary where keys are exponents and values are coefficients 
        of the chromatic polynomial.
    """
    # Base case: If the graph has no edges, the chromatic polynomial is k^n
    if G.number_of_edges() == 0:
        k = symbols('k')
        return k ** G.number_of_nodes()

    # Pick an edge (u, v)
    u, v = list(G.edges())[0]

    # Deletion: Remove the edge (u, v)
    G_deletion = G.copy()
    G_deletion.remove_edge(u, v)

    # Contraction: Merge u and v into a single vertex
    G_contraction = nx.contracted_nodes(G, u, v, self_loops=False)

    # Recursive computation
    return compute_chromatic_polynomial(G_deletion) - compute_chromatic_polynomial(G_contraction)


def get_graph_metadata(G: nx.Graph) -> Dict[str, Any]:
    """
    Compute a suite of graph metrics for benchmark metadata.

    Parameters
    ----------
    G : nx.Graph
        The input graph.

    Returns
    -------
    Dict[str, Any]
        Dictionary of graph statistics.
    """
    stats = {
        "n_nodes": G.number_of_nodes(),
        "n_edges": G.number_of_edges(),
        "density": nx.density(G),
        "is_connected": nx.is_connected(G),
    }
    
    if stats["is_connected"]:
        stats["diameter"] = nx.diameter(G)
        stats["avg_shortest_path"] = nx.average_shortest_path_length(G)
        
    return stats

# -----------------------------------------------------------------------------------------------------------
# 4️⃣ Smoke tests / example usage
# -----------------------------------------------------------------------------------------------------------

def _run_smoke_test() -> None:
    """
    Sanity check for graph analysis.
    """
    print("💨 Running graph analysis smoke tests...")
    
    # Test with a simple cycle
    G = nx.cycle_graph(4)
    stats = get_graph_metadata(G)
    assert stats["n_nodes"] == 4
    assert stats["n_edges"] == 4
    
    # Chromatic polynomial of C4 is k(k-1)^3 - k(k-1)(k-2) = k^4 - 4k^3 + 6k^2 - 3k
    poly = compute_chromatic_polynomial(G)
    print(f"Chromatic polynomial of C4: {poly}")
    
    print("✅ Graph analysis smoke tests passed.")

# -----------------------------------------------------------------------------------------------------------
# 5️⃣ Entry point
# -----------------------------------------------------------------------------------------------------------

def main() -> None:
    """
    Main entry point for smoke tests.
    """
    _run_smoke_test()

if __name__ == "__main__":
    main()
