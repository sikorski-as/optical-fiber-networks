from typing import Tuple


def find_k_shortest_paths_between_every_node(net, k: int):
    paths_dict = {}
    for node in net.nodes:
        paths_dict[node] = {}
        for another_node in net.nodes:
            if node != another_node:
                paths_dict[node][another_node] = generate_all_paths_between(net, (node, another_node), k)
    return paths_dict


def generate_all_paths_between(net, pair: Tuple, amount_of_paths: int):
    """
        Generating paths using BFS method.
    """
    paths = []
    start, end = pair
    queue = [(start, [start])]
    while queue:
        (vertex, path) = queue.pop(0)
        for next in set(net[vertex]) - set(path):
            if next == end:
                paths.append((len(path) + 1, path + [next]))
            else:
                queue.append((next, path + [next]))
        if len(paths) == amount_of_paths:
            break
    return paths
