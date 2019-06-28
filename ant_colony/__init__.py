import networkx as nx
import sndlib
import draw
import mapbox
import os
from pprint import pprint
from ant_colony import ant, world
from geomanip import MercatorProjection


def length(edges):
    return 1 / len(edges)


def calculate_distance(edges):
    total_distance = sum([edge[2]['distance'] for edge in edges])
    return total_distance


def algorithm():
    net = sndlib.UndirectedNetwork.load_native('data/polska.txt')
    w = world.World(net, 0.05, 0.1, False, 1, 1, 1)
    iterations = 200
    number_of_ants = 50
    assessment_fun = length
    select_fun = max

    goals = [(n1, n2) for n1 in net.nodes for n2 in net.nodes if n1 != n2]
    solutions = {}
    prepare_map(net)

    colony = ant.Colony(number_of_ants, w, select_fun, assessment_fun)

    for goal in goals:
        best_solution = colony.find_best_solution(goal, n=iterations)
        solutions[goal] = best_solution
        draw.prepare('data/map-pl.png')
        show_map(w.net)
        w.reset_edges()

        print(f"{goal} - {best_solution}")
    pprint(solutions)


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
        pheromone = d['pheromone_level']
        draw.line(u.x, u.y, v.x, v.y, marker='o', color='gray')
        draw.text(sx, sy, f'{pheromone:.2f}', fontsize=7, color='navy', weight='bold', horizontalalignment='center')

    draw.show()

