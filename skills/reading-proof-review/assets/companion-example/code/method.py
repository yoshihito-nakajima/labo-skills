# Fictional "ordering method" used only to exercise the companion skeleton.
import math

def neighbour_graph(points, k=3, boost=1.5):
    """Join each point to its k nearest points; edges in sparse places cost `boost` times more."""
    edges = []
    for i, p in enumerate(points):
        d = sorted((math.dist(p, q), j) for j, q in enumerate(points) if j != i)
        edges += [(i, j, w * (boost if w > 1.0 else 1.0)) for w, j in d[:k]]
    return edges


def shortest_path(edges, start, goal):
    """Cheapest path between two points over the weighted edges (Dijkstra)."""
    import heapq
    adj = {}
    for i, j, w in edges:
        adj.setdefault(i, []).append((j, w))
        adj.setdefault(j, []).append((i, w))
    best, queue = {start: 0.0}, [(0.0, start)]
    while queue:
        d, u = heapq.heappop(queue)
        if u == goal:
            return d
        for v, w in adj.get(u, []):
            if d + w < best.get(v, 1e9):
                best[v] = d + w
                heapq.heappush(queue, (d + w, v))
