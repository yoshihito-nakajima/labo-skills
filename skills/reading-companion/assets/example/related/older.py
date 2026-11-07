# Fictional earlier method: a plain k-nearest-neighbour graph with distance weights.
import math

def plain_graph(points, k=3):
    edges = []
    for i, p in enumerate(points):
        d = sorted((math.dist(p, q), j) for j, q in enumerate(points) if j != i)
        edges += [(i, j, w) for w, j in d[:k]]
    return edges
