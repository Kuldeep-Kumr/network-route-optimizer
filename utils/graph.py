"""Graph structures and algorithms for route optimization (scaffold)."""

from typing import Any


def build_adjacency_list(
    edges: list[dict[str, Any]],
) -> dict[int, list[tuple[int, float]]]:
    """
    Build an adjacency list: node_id -> list of (neighbor_id, weight).

    Parameters are untyped dicts for now; replace with models or DTOs later.
    """
    _ = edges
    return {}
