# src/kuramoto/topologies/loader.py

import networkx as nx
import numpy as np

def load_topology(name: str, return_graph: bool = False, **kwargs):
    """
    Load a network topology by name.

    Parameters
    ----------
    name : str
        Topology name ('ring', 'complete', 'small_world', 'random', 'tree_of_life').
    return_graph : bool, default=False
        If True, returns the NetworkX Graph object. If False, returns the adjacency matrix.
    **kwargs :
        Parameters for the topology generator (e.g., n, k, p).

    Returns
    -------
    nx.Graph or np.ndarray
        The generated topology.
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