from functools import lru_cache

import networkx as nx

import sndlib
import yen
import genetic.transponder_config as t_config

net = sndlib.create_undirected_net('polska', calculate_distance=True, calculate_reinforcement=True)


@lru_cache(maxsize=1024)
def dist(a, b):
    return sndlib.calculate_haversine_distance_between_each_node(net)[a][b]


K = 3  # number of predefined paths
predefined_paths = yen.ksp_all_nodes(net, nx.astar_path, heuristic_fun=dist, k=K)

slices_usage = {
    0: 4,
    1: 4,
    2: 8,
    3: 12
}

transponders_cost = {
    0: 2,
    1: 5,
    2: 7,
    3: 9
}

bands = [(0, 191), (192, 383)]  # ranges of slices per band

DEMAND = 250
POP_SIZE = 50
NEW_POP_SIZE = 10

demands = {key: DEMAND for key in predefined_paths}
transponders_config = {DEMAND: t_config.create_config([(40, 4), (100, 4), (200, 8), (400, 12)], DEMAND, 3)}

CPB = 100
MPB = 50
GA_ITERATIONS = 50

HILL_ITERATIONS = 300
