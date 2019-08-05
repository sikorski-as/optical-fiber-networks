import timeit

import networkx as nx

import sndlib
import yen


def create_net():
    return sndlib.create_undirected_net(NETWORK_NAME, calculate_distance=True)


NETWORK_NAME = 'germany50'
DISTANCE = sndlib.calculate_haversine_distance_between_each_node(create_net())
DISTANCE_KEY = 'distance'
K = 3


def dist(a, b):
    return DISTANCE[a][b]


if __name__ == "__main__":

    score = timeit.timeit('find_k_shortest_paths_between_every_node(net, k)',
                          setup='from BFS import find_k_shortest_paths_between_every_node; import ant_colony; net=ant_colony.create_net(); k=3',
                          number=100)
    print(score)

    score = timeit.timeit(
        'yen.algorithm.ksp_all_nodes(net, nx.algorithms.astar_path, heuristic_fun=dist, k=3, weight=\'distance\')',
        setup='import networkx as nx; import yen; from __main__ import dist, create_net; net=create_net();',
        number=10)
    print(score)
    score = timeit.timeit(
        'yen.algorithm.ksp_all_nodes(net, nx.algorithms.single_source_dijkstra, k=3, weight=\'distance\')',
        setup='import networkx as nx; import yen; from __main__ import create_net; net=create_net();',
        number=10)
    print(score)

    ###
    net = create_net()

    a_star_paths_dict = yen.ksp_all_nodes(net, nx.astar_path, heuristic_fun=dist, k=K, weight=DISTANCE_KEY)
    dijkstra_paths_dict = yen.ksp_all_nodes(net, nx.single_source_dijkstra, k=K, weight=DISTANCE_KEY)

    total_a_star_distance = sum(
        path[0] for node in net.nodes for neighbour in net[node] for path in a_star_paths_dict[node][neighbour])
    total_dijkstra_distance = sum(
        path[0] for node in net.nodes for neighbour in net[node] for path in dijkstra_paths_dict[node][neighbour])
    print(f"astar {total_a_star_distance}, dijkstra {total_dijkstra_distance}")
