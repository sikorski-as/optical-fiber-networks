import copy
import itertools
import heapq
import networkx as nx

import sndlib


def ksp_all_nodes(G, searching_fun, heuristic_fun=None, k=1, weight=None):
    paths_dict = {}
    net = copy.deepcopy(G)
    for node in G.nodes:
        paths_dict[node] = {}
        for neighbour in G[node]:
            paths_dict[node][neighbour] = ksp(net, node, neighbour, searching_fun, heuristic_fun, k, weight)
    return paths_dict


"""
    https://en.wikipedia.org/wiki/Yen%27s_algorithm
    nie dziala dla skierowanego gdy krawedz (1, 2, ...) i (2, 1, ...) mają różne atrybuty
"""


def ksp(G: nx.Graph, source, target, searching_fun, heuristic_fun=None, k=1, weight=None):
    if weight is None:
        length_func = len
    else:
        def length_func(path, skipped_nodes=None):
            score = 0
            for (u, v) in zip(path, path[1:]):
                try:
                    score += G.adj[u][v][weight]
                except KeyError:
                    if skipped_nodes:
                        score += skipped_nodes[u][v][weight]
                    else:
                        raise
            return score

    list_a = list()
    list_b = PathBuffer()
    prev_path = None

    while len(list_a) < k:
        if not prev_path:
            if heuristic_fun:
                path = searching_fun(G, source, target, heuristic_fun, weight=weight)
            else:
                _, path = searching_fun(G, source, target, weight=weight)
            score = length_func(path)
            list_a.append((score, path))
        else:
            skipped_nodes = {}
            skipped_edges = list()
            for i in range(1, len(prev_path)):
                root = prev_path[:i]
                root_score = length_func(root, skipped_nodes)
                for _, path in list_a:
                    if path[:i] == root:
                        skipped_edges.append((path[i - 1], path[i], G[path[i - 1]][path[i]]))
                G.remove_edges_from(skipped_edges)
                try:
                    if heuristic_fun:
                        spur = searching_fun(G, root[-1], target, heuristic_fun, weight=weight)
                    else:
                        _, spur = searching_fun(G, root[-1], target, weight=weight)
                    spur_score = length_func(spur)
                    path = root[:-1] + spur
                    list_b.push(root_score + spur_score, path)
                except nx.NetworkXNoPath:
                    pass
                G.add_edges_from(skipped_edges)
                skipped_edges.clear()
                node = root[-1]
                skipped_nodes[node] = G[node]
                G.remove_node(node)
            _restore_graph(G, skipped_nodes)
            skipped_nodes.clear()
        if list_b:
            list_a.append(list_b.pop())
        elif prev_path:
            raise ValueError(f"Cannot find {k} paths")
        prev_path = path

    return list_a


def _restore_graph(G, skipped_nodes):
    G.add_nodes_from(skipped_nodes.keys())
    G.add_edges_from(_get_edges(skipped_nodes, directed_graph=isinstance(G, sndlib.DirectedNetwork)))


def _get_edges(skipped_nodes, directed_graph=False):
    edges = list()
    for node, values in skipped_nodes.items():
        for neighbour, attrs in values.items():
            if directed_graph:
                edges.append((node, neighbour, attrs))
                edges.append((neighbour, node, attrs))
            else:
                edges.append((node, neighbour, attrs))
    return edges


class PathBuffer:

    def __init__(self):
        self.paths = set()
        self.sortedpaths = list()
        self.counter = itertools.count()

    def __len__(self):
        return len(self.sortedpaths)

    def push(self, cost, path):
        hashable_path = tuple(path)
        if hashable_path not in self.paths:
            heapq.heappush(self.sortedpaths, (cost, next(self.counter), path))
            self.paths.add(hashable_path)

    def pop(self):
        (cost, num, path) = heapq.heappop(self.sortedpaths)
        hashable_path = tuple(path)
        self.paths.remove(hashable_path)
        return cost, path
