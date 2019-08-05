from typing import Tuple


def find_k_shortest_paths_between_every_node(net, amount_of_paths: int):
    paths_dict = {}
    for node in net.nodes:
        for neighbour in net[node]:
            paths_dict[node] = generate_all_paths_between(net, (node, neighbour), amount_of_paths)
    return paths_dict


def generate_all_paths_between(net, pair: Tuple, amount_of_paths: int):
    """
        Generating paths using BFS method.
    """
    paths_created = 0
    start, end = pair
    queue = [(start, [start])]
    while queue:
        (vertex, path) = queue.pop(0)
        for next in set(net[vertex]) - set(path):
            if next == end:
                yield path + [next]
                paths_created += 1
            else:
                queue.append((next, path + [next]))
        if paths_created == amount_of_paths:
            break
