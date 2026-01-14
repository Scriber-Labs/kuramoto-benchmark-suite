from __future__ import annotations
import numpy as np
from typing import Dict

def build_adjacency(n: int, adjacency: np.ndarray | None) -> np.ndarray:
    """
    Builds an adjacency matrix for a provided adjacency matrix. 
    If no adjacency matrix is provided, a fully connected graph (excluding self-loops) is created.

    Parameters
    ----------
    n : int 
        Number of nodes in the graph.
    adjacency : np.ndarray | None
        Adjacency matrix of the graph of interest. If None, a fully connected graph is created.
    
    Returns 
    -------
    np.ndarray
        The adjacency matrix of the graph. 
    """
    if adjacency is None:
        A = np.ones((n, n)) - np.eye(n)
    else:
        A = adjacency
    return A

def graph_stats(A: np.ndarray) -> Dict[str, float]:
    """
    Computes basic statistics of the graph represented by the adjacency matrix.
    
    Parameters
    ----------
    A : np.ndarray
        Adjacency matrix of the graph.
    
    Returns
    -------
    Dict[str, float]
        A dictionary containing:
          - number of nodes
          - number of edges
          - average degree 
          - density
          - is connected
    """
    n = A.shape[0]
    edges = np.count_nonzero(A) / 2     # Undirected graph
    avg_degree = np.sum(A) / n    
    density = (2 * edges) / (n * (n - 1))
    return {
        "num_edges": int(edges),
        "density": density,
        "is_connected": edges >= n -1,
    }

