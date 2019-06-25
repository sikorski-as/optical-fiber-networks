from pprint import pprint
import networkx as nx
import sndlib
from geomanip import MercatorProjection, haversine
import draw
import mapbox
import os


def example_sndlib_draw_geomanip():
    projection = MercatorProjection(map_size=(1024, 512), center=(19.6153711, 52.0892499), zoom=5)

    status = mapbox.get_map_as_file(
        'data/map-pl.png',
        replace=True,
        api_token=os.environ['MAPBOX_API_KEY'],
        projection=projection,
        style='countries_basic',
    )
    print('Map ' + ('' if status else 'not ') + 'downloaded')

    net = sndlib.make_network(nx.Graph).load_native('data/polska.txt')
    net.add_pixel_coordinates(projection)

    draw.prepare('data/map-pl.png')

    for u, v in net.edges:
        sx, sy = net.edge_middle_point(u, v, pixel_value=True)
        distance = haversine(u.long, u.lati, v.long, v.lati)
        draw.line(u.x, u.y, v.x, v.y, marker='o', color='gray')
        draw.text(sx, sy, f'{distance:.0f}km', fontsize=7, color='navy', weight='bold', horizontalalignment='center')

    for node in net.nodes:
        draw.text(node.x, node.y, node.name, fontsize=8, color='black', weight='bold', horizontalalignment='center')
    draw.show()


def example_get_adjusted_map():
    net = sndlib.make_network(nx.Graph).load_native('data/janos-us.txt')
    points = [(n.long, n.lati) for n in net.nodes]
    projection = MercatorProjection.from_points(points, map_size=(1024, 512), padding=50)

    status = mapbox.get_map_as_file(
        'data/map-us.png',
        replace=True,
        api_token=os.environ['MAPBOX_API_KEY'],
        projection=projection,
        style='countries_basic',
    )
    print('Map ' + ('' if status else 'not ') + 'dowloaded')

    net.add_pixel_coordinates(projection)

    draw.prepare('data/map-us.png')
    for u, v in net.edges:
        sx, sy = net.edge_middle_point(u, v, pixel_value=True)
        distance = haversine(u.long, u.lati, v.long, v.lati)
        draw.line(u.x, u.y, v.x, v.y, marker='o', color='gray')
        draw.text(sx, sy, f'{distance:.0f}km', fontsize=7, color='navy', weight='bold', horizontalalignment='center')

    for node in net.nodes:
        draw.text(node.x, node.y, node.name, fontsize=8, color='black', weight='bold', horizontalalignment='center')
    draw.show()


def example_edges_with_attrs():
    pheromone_level = 0.1
    calculate_distance = False

    net = sndlib.make_network(nx.Graph).load_native('data/polska.txt')
    attrs = {'pheromone_level': pheromone_level}
    for edge in net.edges:
        if calculate_distance:
            u, v = edge
            attrs['distance'] = haversine(u.long, u.lati, v.long, v.lati)
        net.add_attributes_to_edge(edge, attrs)
        
    pprint(net.edges.data())

    for edge in net.edges.data():
        print(edge[2]['pheromone_level'])


if __name__ == '__main__':
    example_sndlib_draw_geomanip()
    # example_get_adjusted_map()
    # example_edges_with_attrs()
