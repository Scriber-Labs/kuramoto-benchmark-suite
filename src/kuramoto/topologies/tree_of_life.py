import networkx as nx
from typing import List, Tuple, Dict

def sefirot_labels() -> List[str]:
    """Return an ordered list of the ten sefirot labels."""
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
    """Map sefirot names to qubit indices."""
    labels: List[str] = sefirot_labels()
    return {name: i for i, name in enumerate(labels)}


def etz_hayim_edges() -> List[Tuple[str, str]]:
    """Canonical 22 undirected edges of Etz Hayim."""
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

    G = nx.Graph()

    nodes = sefirot_labels()
    G.add_nodes_from(nodes)

    edges = etz_hayim_edges()
    G.add_edges_from(edges)

    return G