import sndlib
from pprint import pprint
from ant_colony import ant, world


def length(edges):
    return 1 / len(edges)


def calculate_distance(edges):
    total_distance = sum([edge[2]['distance'] for edge in edges])
    return total_distance


def algorithm():
    network_name = 'polska'
    net = sndlib.UndirectedNetwork.load_native(f'data/{network_name}.txt')
    view = sndlib.NetworkView(net, f'data/{network_name}.png')

    w = world.World(
        net,
        evaporation_level=0.05,
        basic_pheromone_level=0.1,
        calculate_distance=True,
        alpha=1,
        beta=1,
        Q=1
    )

    iterations = 200
    number_of_ants = 50
    assessment_fun = len
    select_fun = min

    goals = [(n1, n2) for n1 in net.nodes for n2 in net.nodes if n1 != n2]
    solutions = {}

    colony = ant.Colony(number_of_ants, w, select_fun, assessment_fun)

    for goal in goals:
        best_solution = colony.find_best_solution(goal, n=iterations)
        solutions[goal] = best_solution
        view.show()
        w.reset_edges()

        print(f'{goal} - {best_solution}')
    pprint(solutions)
