from pathlib import Path

import networkx as nx

import geomanip
import mapbox
import draw
import os
from geomanip import MercatorProjection


class Node:
    def __init__(self, name, long=0.0, lati=0.0):
        self.name = name
        self.long = long
        self.lati = lati
        self.x = 0
        self.y = 0

    def __repr__(self):
        return f"{self.name}"

    def __eq__(self, other):
        return other and self.name == other.name

    def __hash__(self):
        return hash(self.long) + hash(self.lati)

    def __lt__(self, other):
        return other and self.name < other.name


class _Network:
    def __init__(self, name='', *args, **kwargs):
        super(_Network, self).__init__(*args, **kwargs)
        self.node_by_name = {}
        self.name = name

    @classmethod
    def load_native(cls, filename):
        network = cls(name=filename)
        with open(filename) as data_file:
            state = ''
            for line in data_file:
                if state == '':
                    if line.startswith('NODES ('):
                        state = 'NODES'
                    elif line.startswith('LINKS ('):
                        state = 'LINKS'
                else:
                    if line.startswith(')'):
                        state = ''
                    elif state == 'NODES':
                        name, _, long, lati, _, *_ = line.split()
                        new_node = network.node_by_name[name] = Node(name, float(long), float(lati))
                        network.add_node(new_node)
                    elif state == 'LINKS':
                        _, _, n1, n2, _, *_ = line.split()
                        network.add_edge(network.node_by_name[n1], network.node_by_name[n2])
                        network.add_edge(network.node_by_name[n2], network.node_by_name[n1])
        return network

    def edge_middle_point(self, u, v, pixel_value=False):
        if self.has_edge(u, v) or self.has_edge(v, u):
            if pixel_value:
                return (u.x + v.x) / 2, (u.y + v.y) / 2
            else:
                return (u.long + v.long) / 2, (u.lati + v.lati) / 2
        else:
            raise ValueError(f'{u.name}-{v.name} edge does not exists')

    def add_pixel_coordinates(self, projection):
        for node in self.nodes:
            node.x = projection.get_x(node.long)
            node.y = projection.get_y(node.lati)

    def get_list_of_coordinates(self):
        return [(n.long, n.lati) for n in self.nodes]


class NetworkView:
    def __init__(self, network, map_filename):
        self.network = network
        points = network.get_list_of_coordinates()
        self.projection = MercatorProjection.from_points(points, map_size=(1024, 512), padding=75)

        self.map_filename = map_filename
        self.network.add_pixel_coordinates(self.projection)

        mapbox.get_map_as_file(
            map_filename,
            replace=True,
            api_token=os.environ['MAPBOX_API_KEY'],
            projection=self.projection,
            style='countries_basic',
        )

    def _draw(self):
        net = self.network

        draw.prepare(self.map_filename)
        for node in net.nodes:
            draw.text(node.x, node.y, node.name, fontsize=8, color='black', weight='bold', horizontalalignment='center')

        pheromone_all = max(data['pheromone_level'] for _, _, data in net.edges.data())
        for u, v, d in net.edges(data=True):
            sx, sy = net.edge_middle_point(u, v, pixel_value=True)
            pheromone = d['pheromone_level']
            alpha = max(pheromone / pheromone_all, 0.05)
            draw.line(u.x, u.y, v.x, v.y, marker='o', color=(0.5, 0.5, 0.5, alpha))
            draw.text(
                sx, sy, f'{pheromone:.2f}',
                fontsize=7,
                color='navy',
                alpha=max(alpha, 0.3),
                weight='bold',
                horizontalalignment='center'
            )

    def show(self):
        self._draw()
        draw.show()

    def save(self, filename):
        self._draw()
        draw.save_as(filename)


UndirectedNetwork = type('UndirectedNetwork', (_Network, nx.Graph,), {})
DirectedNetwork = type('DirectedNetwork', (_Network, nx.DiGraph,), {})


def create_undirected_net(network_name, calculate_distance=False, calculate_reinforcement=False):
    base_path = Path(__file__).parent
    file_path = (base_path / f'data/{network_name}.txt').resolve()
    net = UndirectedNetwork.load_native(file_path)
    if calculate_distance:
        for edge in net.edges:
            distance = int(geomanip.haversine(edge[0].long, edge[0].lati, edge[1].long,
                                              edge[1].lati))
            net.edges[edge]['distance'] = distance
    return net


def create_directed_net(network_name, calculate_distance=False, calculate_reinforcement=False):
    base_path = Path(__file__).parent
    file_path = (base_path / f'data/{network_name}.txt').resolve()
    net = DirectedNetwork.load_native(file_path)
    if calculate_distance:
        for edge in net.edges:
            distance = int(geomanip.haversine(edge[0].long, edge[0].lati, edge[1].long,
                                              edge[1].lati))
            net.edges[edge]['distance'] = distance
    if calculate_reinforcement:
        nodes_reinforcement = calculate_reinforcement_for_each_node(net)
        edges_reinforcement = calculate_reinforcement_for_each_edge(net)
        for edge in net.edges:
            reinforcement = nodes_reinforcement[edge[0]] + edges_reinforcement[edge]
            net[edge[0]][edge[1]]['reinforcement'] = reinforcement
    return net


def calculate_haversine_distance_between_each_node(net):
    dist_dict = {}
    for node in net.nodes:
        dist_dict[node] = {}
        for another_node in net.nodes:
            dist_dict[node][another_node] = \
                geomanip.haversine(node.long, node.lati, another_node.long, another_node.lati)
    return dist_dict


def calculate_reinforcement_for_each_node(net):
    reinforcement_dict = {}
    for node in net.nodes:
        reinforcement_dict[node] = 10 + len(net[node])
    return reinforcement_dict


def calculate_reinforcement_for_each_edge(net):
    CONST = 0.24  # db/km
    reinforcement_dict = {}
    for edge in net.edges:
        distance = int(geomanip.haversine(edge[0].long, edge[0].lati, edge[1].long,
                                          edge[1].lati))
        reinforcement_dict[edge] = distance * CONST
    return reinforcement_dict
