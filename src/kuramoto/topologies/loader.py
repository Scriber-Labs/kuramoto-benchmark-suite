# src/kuramoto/topologies/loader.py

"""
loader.py

Functions for loading and generating network topologies.

Author: Eigenscribe
Date: May 2026
"""

from __future__ import annotations

import networkx as nx
import numpy as np
from typing import Any, Final, Optional
from numpy.typing import NDArray

# -----------------------------------------------------------------------------------------------------------
# 0️⃣ Type aliases
# -----------------------------------------------------------------------------------------------------------
AdjacencyMatrix = NDArray[np.floating]

# -----------------------------------------------------------------------------------------------------------
# 1️⃣ Core definitions
# -----------------------------------------------------------------------------------------------------------

def load_topology(
    name: str, 
    return_graph: bool = False, 
    **kwargs: Any
) -> nx.Graph | AdjacencyMatrix:
    """
    Load a network topology by name.

    Parameters
    ----------
    name : str
        Topology name ('ring', 'complete', 'small_world', 'random', 'tree_of_life').
    return_graph : bool, default=False
        If True, returns the NetworkX Graph object. If False, returns the adjacency matrix.
    **kwargs : Any
        Parameters for the topology generator (e.g., n, k, p).

    Returns
    -------
    nx.Graph or AdjacencyMatrix
        The generated topology.
    
    Raises
    ------
    ValueError
        If an unknown topology name is provided.
    """
    if name == "ring":
        G = nx.cycle_graph(kwargs.get("n", 20))

    elif name == "complete":
        G = nx.complete_graph(kwargs.get("n", 20))

    elif name == "small_world":
        G = nx.watts_strogatz_graph(
           kwargs.get("n", 20),
           kwargs.get("k", 4),
           kwargs.get("p", 0.2)
        )

    elif name == "random":
        G = nx.erdos_renyi_graph(
            kwargs.get("n", 20),
            kwargs.get("p", 0.2)
        )

    elif name == "tree_of_life":
        from .tree_of_life import build_tree_of_life
        G = build_tree_of_life()

    else:
        raise ValueError(f"Unknown topology: {name}")

    if return_graph:
        return G
    return nx.to_numpy_array(G)

# -----------------------------------------------------------------------------------------------------------
# 4️⃣ Smoke tests / example usage
# -----------------------------------------------------------------------------------------------------------

def _run_smoke_test() -> None:
    """
    Quick sanity checks for topology loading.
    """
    print("💨 Running topology loader smoke tests...")
    
    # Test ring
    A_ring = load_topology("ring", n=10)
    assert isinstance(A_ring, np.ndarray)
    assert A_ring.shape == (10, 10)
    
    # Test complete
    G_comp = load_topology("complete", n=5, return_graph=True)
    assert isinstance(G_comp, nx.Graph)
    assert G_comp.number_of_nodes() == 5
    
    print("✅ Topology loader smoke tests passed.")

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