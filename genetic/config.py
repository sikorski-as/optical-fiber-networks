import math
from functools import lru_cache
import networkx as nx
import sndlib
import yen
import genetic.transponders as tconfiger
# import genetic.transponder_config as t_config
from DataAnalyzis.analyzer import DataInfo

net_name = 'polska'
net = sndlib.create_undirected_net(net_name, calculate_distance=True, calculate_reinforcement=True, calculate_ila=True)


@lru_cache(maxsize=1024)
def dist(a, b):
    return sndlib.calculate_haversine_distance_between_each_node(net)[a][b]


def get_kozdro_paths():
    with open("data\less025.dat") as path_file, open("data\cities.txt") as cities_file, open(
            'data\edges.txt') as edges_file:
        data_info = DataInfo(result_file=None, paths_file=path_file, cities_file=cities_file, edges_file=edges_file)
        data_info.upload_paths()

        # for key, values in data_info.paths_dict.items():
        #     data_info.paths_dict[key] = [values[0]]
            # print(f"{key}: {values}\n")
    return data_info.paths_dict


K = 3  # number of predefined paths
# predefined_paths = yen.ksp_all_nodes(net, nx.astar_path, heuristic_fun=dist, k=K)
predefined_paths = get_kozdro_paths()

slices_usage = {
    0: 4,
    1: 4,
    2: 8,
    3: 12
}

b_cost = {
    0: 1,
    1: 2
}

transponders_cost = {
    (0, 0): 2,
    (1, 0): 5,
    (2, 0): 7,
    (3, 0): 9,
    (0, 1): 2.4,
    (1, 1): 6,
    (2, 1): 8.4,
    (3, 1): 11.8,
}

bands = [(0, 191), (192, 383)]  # ranges of slices per band

# DEMAND = 450
POP_SIZE = 100
NEW_POP_SIZE = 20

# demands = {key: DEMAND for key in predefined_paths}
# transponders_config = {DEMAND: t_config.create_config([(40, 4), (100, 4), (200, 8), (400, 12)], DEMAND, 3)}
transponders_config = tconfiger.load_config('data/transponder_config_ea.json')
intensity = 0.25
demands = {key: math.ceil(value * intensity) for key, value in net.demands.items()}

CPB = 100
GSPB = 20  # Gene swap probability
MPB = 50
CPPB = 5  # Change path probability
GA_ITERATIONS = 2

HILL_ITERATIONS = 2000
