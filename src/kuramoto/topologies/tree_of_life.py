"""
tree_of_life.py

Construction of the Tree of Life (Etz Hayim) graph topology.

Author: Eigenscribe
Date: May 2026
"""

from __future__ import annotations

import networkx as nx
from typing import List, Tuple, Dict, Final

# -----------------------------------------------------------------------------------------------------------
# 1️⃣ Core definitions
# -----------------------------------------------------------------------------------------------------------

def sefirot_labels() -> List[str]:
    """
    Return an ordered list of the ten sefirot labels.
    
    Returns
    -------
    List[str]
        The 10 sefirot names.
    """
    return [
        "Keter",
        "Chokhmah",
        "Binah",
        "Chesed",
        "Gevurah",
        "Tiferet",
        "Netzach",
        "Hod",
        "Yesod",
        "Malkhut",
    ]

def sefirot_indices() -> Dict[str, int]:
    """
    Map sefirot names to indices.
    
    Returns
    -------
    Dict[str, int]
        Mapping from name to integer index.
    """
    labels: List[str] = sefirot_labels()
    return {name: i for i, name in enumerate(labels)}

def etz_hayim_edges() -> List[Tuple[str, str]]:
    """
    Canonical 22 undirected edges of Etz Hayim.
    
    Returns
    -------
    List[Tuple[str, str]]
        List of edges as (source, target) name pairs.
    """
    return [
        ("Keter", "Chokhmah"),
        ("Keter", "Binah"),
        ("Chokhmah", "Binah"),
        ("Chokhmah", "Chesed"),
        ("Binah", "Gevurah"),
        ("Chesed", "Gevurah"),
        ("Keter", "Tiferet"),
        ("Chokhmah", "Tiferet"),
        ("Binah", "Tiferet"),
        ("Chesed", "Tiferet"),
        ("Gevurah", "Tiferet"),
        ("Tiferet", "Netzach"),
        ("Tiferet", "Hod"),
        ("Netzach", "Hod"),
        ("Netzach", "Yesod"),
        ("Hod", "Yesod"),
        ("Tiferet", "Yesod"),
        ("Yesod", "Malkhut"),
        ("Netzach", "Malkhut"),
        ("Hod", "Malkhut"),
        ("Chesed", "Netzach"),
        ("Gevurah", "Hod"),
    ]

def build_tree_of_life() -> nx.Graph:
    """
    Build the Tree of Life graph using NetworkX.
    
    Returns
    -------
    nx.Graph
        The constructed graph with 10 nodes and 22 edges.
    """
    G = nx.Graph()

    nodes = sefirot_labels()
    G.add_nodes_from(nodes)

    edges = etz_hayim_edges()
    G.add_edges_from(edges)

    return G

def tree_of_life_positions() -> Dict[str, Tuple[float, float]]:
    """
    Canonical positions for the Tree of Life nodes for visualization.
    
    Returns
    -------
    Dict[str, Tuple[float, float]]
        Mapping from sefirot name to (x, y) coordinates.
    """
    return {
        "Keter": (0.0, 1.0),
        "Chokhmah": (0.5, 0.8),
        "Binah": (-0.5, 0.8),
        "Chesed": (0.5, 0.4),
        "Gevurah": (-0.5, 0.4),
        "Tiferet": (0.0, 0.4),
        "Netzach": (0.5, 0.0),
        "Hod": (-0.5, 0.0),
        "Yesod": (0.0, -0.4),
        "Malkhut": (0.0, -1.0),
    }

# -----------------------------------------------------------------------------------------------------------
# 4️⃣ Smoke tests / example usage
# -----------------------------------------------------------------------------------------------------------

def _run_smoke_test() -> None:
    """
    Verify the Tree of Life construction.
    """
    print("💨 Running Tree of Life smoke tests...")
    G = build_tree_of_life()
    assert G.number_of_nodes() == 10
    assert G.number_of_edges() == 22
    print("✅ Tree of Life smoke tests passed.")

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