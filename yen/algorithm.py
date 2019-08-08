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
        for another_node in G.nodes:
            if node != another_node:
                paths_dict[node][another_node] = ksp(net, node, another_node, searching_fun, heuristic_fun, k, weight)
    return paths_dict


"""
    https://en.wikipedia.org/wiki/Yen%27s_algorithm
    nie dziala dla skierowanego gdy krawedz (1, 2, ...) i (2, 1, ...) mają różne atrybuty
"""


def ksp(G: nx.Graph, source, target, searching_fun, heuristic_fun=None, k=1, weight=None):
    info_graph = copy.deepcopy(G) # during ksp graph is changing, info_graph stores whole info all the time
    if weight is None:
        length_func = len
    else:
        def length_func(path):
            score = 0
            for (u, v) in zip(path, path[1:]):
                try:
                    score += G.adj[u][v][weight]
                except KeyError:
                    if skipped_nodes:
                        score += info_graph[u][v][weight]
                    else:
                        raise
            return score

    list_a = list()
    list_b = PathBuffer()
    prev_path = None
    path = None

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
                root_score = length_func(root)
                for _, already_chosen_path in list_a:
                    if already_chosen_path[:i] == root:
                        skipped_edges.append((already_chosen_path[i - 1], already_chosen_path[i],
                                              G[already_chosen_path[i - 1]][already_chosen_path[i]]))
                G.remove_edges_from(skipped_edges)
                try:
                    if heuristic_fun:
                        spur = searching_fun(G, root[-1], target, heuristic_fun, weight=weight)
                    else:
                        _, spur = searching_fun(G, root[-1], target, weight=weight)
                    spur_score = length_func(spur)
                    potential_best_path = root[:-1] + spur
                    list_b.push(root_score + spur_score, potential_best_path)
                except nx.NetworkXNoPath:
                    pass
                G.add_edges_from(skipped_edges)
                skipped_edges.clear()
                node = root[-1]
                skipped_nodes[node] = _find_all_edges(G, node, directed_graph=isinstance(G, sndlib.DirectedNetwork))
                G.remove_node(node)
            _restore_graph(G, skipped_nodes)
            skipped_nodes.clear()
        if list_b:
            score, path = list_b.pop()
            list_a.append((score, path))
        elif prev_path:
            raise ValueError(f"Cannot find {k} paths")
        prev_path = path

    return list_a


def _find_all_edges(G, node, directed_graph=False):
    edges = []
    # firstly edges (node, x)
    for neighbour, attrs in G[node].items():
        edges.append((node, neighbour, attrs))
        # secondly edges(x, node)
        if directed_graph:
            try:
                edges.append((neighbour, node, G[neighbour][node]))
            except KeyError:
                continue
    return edges


def _restore_graph(G, skipped_nodes):
    G.add_nodes_from(skipped_nodes.keys())
    for value in skipped_nodes.values():
        G.add_edges_from(value)


# def _get_edges(skipped_nodes, directed_graph=False):
#     edges = list()
#     for node, values in skipped_nodes.items():
#         for neighbour, attrs in values.items():
#             if directed_graph:
#                 edges.append((node, neighbour, attrs))
#                 edges.append((neighbour, node, attrs))
#             else:
#                 edges.append((node, neighbour, attrs))
#     return edges


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
