import sndlib
from ant_colony import world, ant


def length(edges):
    return 1 / len(edges)


def calculate_distance(edges):
    total_distance = sum([edge[2]['distance'] for edge in edges])
    return total_distance


def create_colony(network_name):
    net = sndlib.UndirectedNetwork.load_native(f'data/sndlib/native/{network_name}/{network_name}.txt')
    view = sndlib.NetworkView(net, f'data/sndlib-images/{network_name}.png')

    edge_dumping = {edge: 0.24 for edge in net.edges}

    w = world.World(
        net,
        evaporation_level=0.1,
        basic_pheromone_level=0.01,
        calculate_distance=True,
        alpha=1,
        beta=1,
        Q=1,
        edge_dumping=edge_dumping,
        node_dumping=15,
    )

    iterations = 40
    number_of_ants = 35
    number_of_solutions = 3
    assessment_fun = calculate_distance
    select_fun = min
    goals = [(n1, n2) for n1 in net.nodes for n2 in net.nodes if n1 != n2]

    return ant.Colony(number_of_ants, number_of_solutions, w, select_fun, assessment_fun, goals, iterations)


def run(colony):
    solutions = {}
    for goal in colony.goals:
        best_ants = colony.find_best_solution(goal, n=colony.iterations)
        _add_solutions(solutions, goal, best_ants)
        colony.world.reset_edges()
    return solutions


def _add_solutions(solutions_dict, goal, ants):
    solutions_dict[goal] = []
    for ant in ants:
        solutions_dict[goal].append((ant.total_distance, ant.solution))
