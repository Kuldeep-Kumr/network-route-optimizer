"""Graph algorithms for route computation."""

from __future__ import annotations

import heapq
from collections import defaultdict


def build_adjacency(
    edges: list[tuple[int, int, float]],
) -> dict[int, list[tuple[int, float]]]:
    adj: dict[int, list[tuple[int, float]]] = defaultdict(list)
    for u, v, latency in edges:
        adj[u].append((v, latency))
    return dict(adj)


def dijkstra_shortest_path(
    adjacency: dict[int, list[tuple[int, float]]],
    start: int,
    end: int,
) -> tuple[float | None, list[int] | None]:
    """Return (total_cost, path of node ids) or (None, None) if unreachable."""
    if start == end:
        return 0.0, [start]

    dist: dict[int, float] = {start: 0.0}
    prev: dict[int, int] = {}
    heap: list[tuple[float, int]] = [(0.0, start)]

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist.get(u, float("inf")):
            continue
        if u == end:
            break
        for v, w in adjacency.get(u, ()):
            nd = d + w
            if v not in dist or nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, v))

    if end not in dist:
        return None, None

    path: list[int] = []
    cur = end
    while cur != start:
        path.append(cur)
        cur = prev[cur]
    path.append(start)
    path.reverse()
    return dist[end], path
