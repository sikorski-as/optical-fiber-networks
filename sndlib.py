import json
import math
import os
from contextlib import suppress
from pathlib import Path
from typing import Callable

import networkx as nx

import draw
import geomanip
import mapbox
from geomanip import MercatorProjection


class Node:
    def __init__(self, name, long=0.0, lati=0.0):
        self.name = name
        self.long = long
        self.lati = lati
        self.x = 0
        self.y = 0

    def __repr__(self):
        return "<{}>".format(self.name)

    def __eq__(self, other):
        return other and self.name == other.name

    def __hash__(self):
        return hash(self.long) + hash(self.lati)

    def __lt__(self, other):
        return other and self.name < other.name


class _Network:
    def __init__(self, name='', *args, **kwargs):
        # super(_Network, self).__init__(*args, **kwargs)
        self.node_by_name = {}
        self.name = name
        self._demands = {}
        self.node_by_id = {}  # numer node'a (1..|V|) -> obiekt typu node

    DISTANCE_KEY = 'distance'

    def load_demands_from_datfile(self, filename):
        self._demands = {}
        with open(filename) as f:
            fiter = iter(f)
            while not next(fiter).startswith('param demand'):
                pass
            for line in fiter:
                if not line.startswith(';'):  # pomija średnik
                    splitted = line.split()
                    if splitted:  # pomija puste listy
                        v1 = int(splitted[0])
                        splitted = splitted[1:]
                        for v2, demand in enumerate(splitted, start=1):
                            with suppress(ValueError):
                                demand = float(demand)
                                s, t = self.node_by_id[v1], self.node_by_id[v2]
                                self._demands[(s, t)] = demand

    @classmethod
    def load_native(cls, filename):
        network = cls(name=filename)
        print('Using depricated method load_native()')
        with open(filename) as data_file:
            state = ''
            link_id = 1
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
                        network.add_edge(network.node_by_name[n1], network.node_by_name[n2], edge_id=link_id)
                        network.add_edge(network.node_by_name[n2], network.node_by_name[n1], edge_id=link_id)
                        link_id += 1
        return network

    @classmethod
    def load_json(cls, filename):
        network = cls(name=filename)
        with open(filename) as f:
            model = json.load(f)
            network.model = model
            for i, n in enumerate(model['nodes'], start=1):
                node = Node(name=n['id'], long=n['longitude'], lati=n['latitude'])
                network.node_by_name[n['id']] = node
                network.add_node(node)
                network.node_by_id[i] = node
            for link_id, e in enumerate(model['links'], start=1):
                with suppress(KeyError):
                    s, t = e['source'], e['target']
                    s, t = network.node_by_name[s], network.node_by_name[t]
                    network.add_edge(s, t, edge_id=link_id)
            for demand in model['demands']:
                with suppress(KeyError):
                    s, t = demand['source'], demand['target']
                    s, t = network.node_by_name[s], network.node_by_name[t]
                    network._demands[(s, t)] = demand['demand_value']
        return network

    @staticmethod
    def get_nodes_and_edges(filename, has_duplicate_edges=False):
        nodes, edges = [], []
        node_by_name = {}

        with open(filename) as f:
            model = json.load(f)
            for n in model['nodes']:
                node = Node(name=n['id'], long=n['longitude'], lati=n['latitude'])
                node_by_name[n['id']] = node
                nodes.append(node)
            for e in model['links']:
                s, t = e['source'], e['target']
                s, t = node_by_name[s], node_by_name[t]
                if has_duplicate_edges and ((s, t) not in edges and (t, s) not in edges):
                    edges.append((s, t))

        return nodes, edges

    @property
    def demands(self):
        """
        :return: a dict with keys (n1, n2) and values being demanded values between n1 and n2.
        """
        return self._demands

    @property
    def all_demands(self):
        """
        :return: a dict with keys both (n1, n2) and (n2, n1) and values being demanded values between n1 and n2.
        """
        new = {}
        for (n1, n2), value in self._demands.items():
            new[(n1, n2)] = value
            new[(n2, n1)] = value
        return new

    def get_demand(self, n1, n2):
        try:
            return self.demands[(n1, n2)]
        except KeyError:
            return self.demands[(n2, n1)]

    def edge_middle_point(self, u, v, pixel_value=False):
        if self.has_edge(u, v) or self.has_edge(v, u):
            if pixel_value:
                return (u.x + v.x) / 2, (u.y + v.y) / 2
            else:
                return (u.long + v.long) / 2, (u.lati + v.lati) / 2
        else:
            raise ValueError('{}-{} edge does not exists'.format(u.name, v.name))

    def add_pixel_coordinates(self, projection):
        for node in self.nodes:
            node.x = projection.get_x(node.long)
            node.y = projection.get_y(node.lati)

    def get_list_of_coordinates(self):
        return [(n.long, n.lati) for n in self.nodes]

    def initialize_edges(self, metric: Callable = None) -> None:
        for n1, n2 in self.edges:
            self[n1][n2][self.DISTANCE_KEY] = metric(n1, n2) if metric is not None else 1


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
            dist = d['distance']
            alpha = max(pheromone / pheromone_all, 0.1)
            draw.line(u.x, u.y, v.x, v.y, marker='o', color=(0.7, 0.0, 0.0, alpha))
            draw.text(
                sx, sy, '{:.2f}'.format(pheromone),
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


class UndirectedNetwork(_Network, nx.Graph):
    def __init__(self, name, *args, **kwargs):
        nx.Graph.__init__(self, *args, **kwargs)
        _Network.__init__(self, name)


class DirectedNetwork(_Network, nx.DiGraph):
    def __init__(self, name, *args, **kwargs):
        nx.DiGraph.__init__(self, *args, **kwargs)
        _Network.__init__(self, name)


def create_undirected_net(network_name, calculate_distance=False, calculate_reinforcement=False, calculate_ila=False):
    base_path = Path(__file__).parent
    file_path = (base_path / 'data/sndlib/json/{}/{}.json'.format(network_name, network_name)).resolve()
    file_path = str(file_path)
    net = UndirectedNetwork.load_json(file_path)
    if calculate_distance:
        for edge in net.edges:
            distance = int(geomanip.haversine(edge[0].long, edge[0].lati, edge[1].long,
                                              edge[1].lati))
            net.edges[edge]['distance'] = distance
            if calculate_ila:
                net.edges[edge]['ila'] = int(distance / 80)
    if calculate_reinforcement:
        nodes_reinforcement = calculate_reinforcement_for_each_node(net)
        edges_reinforcement = calculate_reinforcement_for_each_edge(net)
        for edge in net.edges:
            reinforcement = nodes_reinforcement[edge[0]] + edges_reinforcement[edge]
            net[edge[0]][edge[1]]['reinforcement'] = reinforcement
    return net


def create_directed_net(network_name, calculate_distance=False, calculate_reinforcement=False, calculate_ila=False):
    base_path = Path(__file__).parent
    file_path = (base_path / 'data/sndlib/json/{}/{}.json'.format(network_name, network_name)).resolve()
    file_path = str(file_path)
    net = DirectedNetwork.load_json(file_path)
    if calculate_distance:
        for edge in net.edges:
            distance = math.ceil(geomanip.haversine(edge[0].long, edge[0].lati, edge[1].long,
                                              edge[1].lati))
            net.edges[edge]['distance'] = distance
            if calculate_ila:
                net.edges[edge]['ila'] = int(distance / 80)
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
