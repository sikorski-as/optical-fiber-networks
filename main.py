from pprint import pprint
from ant_colony import ant, world
import sndlib
import networkx as nx
import draw
import os
from geomanip import MercatorProjection
import mapbox


def algorithm():

    net = sndlib.DirectedNetwork(nx.DiGraph).load_native('data/polska.txt')
    w = world.World(net, 0.05, 0.1, False, 1, 1, 1)

    iterations = 200
    number_of_ants = 50
    goals = [(n1, n2) for n1 in net.nodes for n2 in net.nodes if n1 != n2]
    solutions = {}
    prepare_map(net)

    for goal in goals:
        ants = []
        for _ in range(0, number_of_ants):
            ants.append(ant.Ant(w, goal[0], goal[1]))

        global_best_solution = find_solution_for_goal(ants, iterations)
        w.reset_edges()
        solutions[goal] = global_best_solution
        draw.prepare('data/map-pl.png')
        show_map(ants[0].world.net)

        print(f"{goal} - {global_best_solution}")
    pprint(solutions)


def find_solution_for_goal(ants, iterations):
    global_best_solution = None

    for _ in range(0, iterations):
        for a in ants:
            # print(a.find_solution())
            a.find_solution()
        local_best_ant = ant.find_best_ant(ants)
        if local_best_ant is not None:
            if global_best_solution is None:
                global_best_solution = local_best_ant.solution
            elif len(local_best_ant.solution) < len(global_best_solution):
                global_best_solution = local_best_ant.solution
        ants[0].world.evaporate_pheromone()
        for a in ants:
            a.update_path()
            a.reset()
    return global_best_solution


def prepare_map(net):
    projection = MercatorProjection(map_size=(1024, 512), center=(19.6153711, 52.0892499), zoom=5)

    status = mapbox.get_map_as_file(
        'data/map-pl.png',
        replace=True,
        api_token=os.environ['MAPBOX_API_KEY'],
        projection=projection,
        style='countries_basic',
    )
    print('Map ' + ('' if status else 'not ') + 'dowloaded')
    net.add_pixel_coordinates(projection)


def show_map(net):
    for node in net.nodes:
        draw.text(node.x, node.y, node.name, fontsize=8, color='black', weight='bold', horizontalalignment='center')

    for u, v, d in net.edges(data=True):
        sx, sy = net.edge_middle_point(u, v, pixel_value=True)
        pher = d['pheromone_level']
        draw.line(u.x, u.y, v.x, v.y, marker='o', color='gray')
        draw.text(sx, sy, f'{pher:.2f}', fontsize=7, color='navy', weight='bold', horizontalalignment='center')

    draw.show()


if __name__ == "__main__":
    algorithm()
