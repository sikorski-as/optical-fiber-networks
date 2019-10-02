from typing import Tuple
from collections import deque
from sndlib import Node


def find_k_shortest_paths_between_every_node(net, k: int):
    paths_dict = {}
    for node in net.nodes:
        paths_dict[node] = {}
        for another_node in net.nodes:
            if node != another_node:
                paths_dict[node][another_node] = generate_all_paths_between(net, (node, another_node), k)
    return paths_dict


def generate_all_paths_between(net, pair: Tuple[Node, Node], npaths: int):
    """
    Generating `n` paths using BFS method between pair of nodes.
    """
    if npaths <= 0:
        return []

    paths = []
    start, end = pair
    first_case = (start, [start])
    queue = deque()
    queue.append(first_case)

    while len(queue) > 0:
        vertex, path = queue.popleft()
        for next_node in set(net[vertex]) - set(path):
            if next_node == end:
                new_path = len(path) + 1, path + [next_node]
                paths.append(new_path)
            else:
                new_case = next_node, path + [next_node]
                queue.append(new_case)
        if len(paths) == npaths:
            break
    return paths
