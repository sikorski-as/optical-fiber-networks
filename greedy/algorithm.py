from sndlib import UndirectedNetwork
from geomanip import haversine
from collections import defaultdict
from typing import Tuple, List
from queue import Queue


def find_solutions_for_goal(net, goal: Tuple, n: int = 3) -> List[List]:
    start, end = goal
    visited = set()
    to_visit = Queue()
    to_visit.put(start)
    while not to_visit.empty():
        current = to_visit.get()
        visited.add(current)
        for neigh in net[current]:
            if neigh not in visited:
                to_visit.put(neigh)

    return []


def algorithm(filename: str, npaths: int = 3) -> None:
    net = UndirectedNetwork.load_native(filename)
    net.initialize_edges(metric=lambda n1, n2: haversine(n1.long, n1.lati, n2.long, n2.lati))

    goals = ((n1, n2) for n1 in net.nodes for n2 in net.nodes if n1 != n2)
    solutions = {goal: find_solutions_for_goal(net, goal, npaths) for goal in goals}

    # for u, v, d in net.edges(data=True):
    #     print(u, v, d)

    # for u, v in net.edges():
    #     print(net[u][v])

    # for n in net.nodes:
    #     print(net.node[n], n)
    #
    # for n in net.nodes():
    #     print(n, n.name, n.__dict__)
