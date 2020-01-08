import timeit
import networkx as nx
import ant_colony.algorithm
import sndlib
import yen


def calculate_total_distance(net, results_dict):
    return sum(
        path[0] for node in net.nodes for neighbour in net.nodes if neighbour != node for path in
        results_dict[node, neighbour])


def create_net():
    return sndlib.create_undirected_net(NETWORK_NAME, calculate_distance=True)


def dist(a, b):
    return DISTANCE[a][b]


def reinforcement_dist(a, b):
    return DISTANCE[a][b] * 0.24


NETWORK_NAME = 'polska'
DISTANCE = sndlib.calculate_haversine_distance_between_each_node(create_net())
DISTANCE_KEY = 'distance'
WEIGHT = 'distance'
FUNCTION = 'dist'
# WEIGHT = 'reinforcement'
# FUNCTION = 'reinforcement_dist'
K = 3
NUMBER = 3  # number of iterations in tests

if __name__ == "__main__":
    # Test time
    score_log = {
        'astar': [],
        'dijkstra': [],
        'ants': []
    }

    # A*
    score = timeit.repeat(
        f'yen.algorithm.ksp_all_nodes(net, nx.algorithms.astar_path, heuristic_fun={FUNCTION}, k={K}, weight=\'{WEIGHT}\')',
        setup='import networkx as nx; import yen; from __main__ import dist, create_net; net=create_net();',
        repeat=2, number=NUMBER)
    score_log['astar'] = score
    print("A* {} {}".format(WEIGHT, score))

    # Dijkstra
    score = timeit.repeat(
        f'yen.algorithm.ksp_all_nodes(net, nx.algorithms.single_source_dijkstra, k={K}, weight=\'{WEIGHT}\')',
        setup='import networkx as nx; import yen; from __main__ import create_net; net=create_net();',
        repeat=2, number=NUMBER)
    score_log['dijkstra'] = score
    print("Dijkstra {} {}".format(WEIGHT, score))

    # Ant colony
    score = timeit.repeat('ant_colony.run(colony)',
                          setup=f'import ant_colony; colony=ant_colony.create_colony(\'{NETWORK_NAME}\')',
                          repeat=2, number=NUMBER)
    score_log['ants'] = score
    print("Ant colonty {}".format(score))

    # Test total distance
    net = create_net()
    colony = ant_colony.create_colony(NETWORK_NAME)

    a_star_paths_dict = yen.ksp_all_nodes(net, nx.astar_path, heuristic_fun=dist, k=K, weight=WEIGHT)
    dijkstra_paths_dict = yen.ksp_all_nodes(net, nx.single_source_dijkstra, k=K, weight=WEIGHT)
    ant_colony_path_dict = ant_colony.run(colony)

    total_a_star_distance = sum(
        path[0] for node in net.nodes for neighbour in net.nodes if neighbour != node for path in
        a_star_paths_dict[node, neighbour])
    total_dijkstra_distance = sum(
        path[0] for node in net.nodes for neighbour in net.nodes if neighbour != node for path in
        dijkstra_paths_dict[node, neighbour])
    total_ant_colony_distance = sum(result[0] for goal in colony.goals for result in ant_colony_path_dict[goal])

    print(f"Number of paths {K}: net {NETWORK_NAME}: edge_attribute {WEIGHT}")
    print(
        f"Total distance astar {total_a_star_distance}, dijkstra {total_dijkstra_distance}, ant_colony {total_ant_colony_distance}")
