import timeit
from pprint import pprint

import networkx as nx
import ant_colony
import sndlib
import yen


def compare_results(first_dict, f_dict_name, second_dict, s_dict_name):
    diffs = []
    print(f"First dict keys {len(first_dict.keys())}, Second dict keys {len(second_dict.keys())}")

    for i, ((first_key, first_values), (second_key, second_values)) in enumerate(
            zip(sorted(first_dict.items()), sorted(second_dict.items()))):
        print(f"{i}.\n {f_dict_name}| {first_key} {first_values} \n {s_dict_name}| {second_key} {second_values}")
        if first_key != second_key:
            diffs.append(f"{i}. {first_key} != {second_key}")
        if len(first_values) != len(second_values):
            diffs.append(f"{i}. ")
        for ((f_key, f_values), (s_key, s_values)) in zip(sorted(first_values.items()), sorted(second_values.items())):
            for j, (f_value, s_value) in enumerate(zip(f_values, s_values)):
                if f_value != s_value:
                    diffs.append(f"{i}.{j}.{f_key} {f_value} {s_value}")
    return diffs


def create_net():
    return sndlib.create_undirected_net(NETWORK_NAME, calculate_distance=True)


NETWORK_NAME = 'janos-us'
DISTANCE = sndlib.calculate_haversine_distance_between_each_node(create_net())
DISTANCE_KEY = 'distance'
K = 3
NUMBER = 1


def dist(a, b):
    return DISTANCE[a][b]


if __name__ == "__main__":

    score = timeit.timeit('copy.deepcopy(G)', setup="import copy; from __main__ import create_net; G = create_net()", number=10)
    print(score)

    score = timeit.timeit('find_k_shortest_paths_between_every_node(net, k)',
                          setup='from BFS import find_k_shortest_paths_between_every_node; from __main__ import create_net; net=create_net(); k=3',
                          number=100)
    print(score)

    score = timeit.timeit(
        'yen.algorithm.ksp_all_nodes(net, nx.algorithms.astar_path, heuristic_fun=dist, k=3, weight=\'distance\')',
        setup='import networkx as nx; import yen; from __main__ import dist, create_net; net=create_net();',
        number=NUMBER)
    print(score)
    score = timeit.timeit(
        'yen.algorithm.ksp_all_nodes(net, nx.algorithms.single_source_dijkstra, k=3, weight=\'distance\')',
        setup='import networkx as nx; import yen; from __main__ import create_net; net=create_net();',
        number=NUMBER)
    print(score)

    # colony = ant_colony.create_colony(NETWORK_NAME)
    # solutions = ant_colony.algorithm(colony)
    # print(solutions)

    # score = timeit.timeit('ant_colony.algorithm(colony)', setup='import ant_colony; colony=ant_colony.create_colony(\'polska\')', number=NUMBER)
    # print(score)
    ###
    net = create_net()
    colony = ant_colony.create_colony(NETWORK_NAME)

    a_star_paths_dict = yen.ksp_all_nodes(net, nx.astar_path, heuristic_fun=dist, k=K, weight=DISTANCE_KEY)
    dijkstra_paths_dict = yen.ksp_all_nodes(net, nx.single_source_dijkstra, k=K, weight=DISTANCE_KEY)
    # ant_colony_path_dict = ant_colony.algorithm(colony)

    total_a_star_distance = sum(
        path[0] for node in net.nodes for neighbour in net.nodes if neighbour != node for path in
        a_star_paths_dict[node][neighbour])
    total_dijkstra_distance = sum(
        path[0] for node in net.nodes for neighbour in net.nodes if neighbour != node for path in
        dijkstra_paths_dict[node][neighbour])

    pprint(compare_results(a_star_paths_dict, 'a_star', dijkstra_paths_dict, 'dkstra'))
    # total_ant_colony_distance = sum(result[0] for goal in colony.goals for result in ant_colony_path_dict[goal])
    print(f"astar {total_a_star_distance}, dijkstra {total_dijkstra_distance}")
    # print(f"astar {total_a_star_distance}, dijkstra {total_dijkstra_distance}, ant_colony {total_ant_colony_distance}")

