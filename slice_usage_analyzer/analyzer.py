from pprint import pprint
from collections import defaultdict
import numpy as np
import mapbox
import geomanip
import draw
import sndlib


class DataInfo:
    """
        transponders -> key - int, value -> (x, y) x - bitrate, y - slices used
        number_of_vertices -> amount of cities
    """

    def __init__(self, result_file, paths_file, cities_file, edges_file):
        # demanded value, unused
        self.demand = 450

        # transponder type -> (bitrate, used slices)
        self.transponders = {1: (40, 1), 2: (100, 1), 3: (200, 1)}

        # summary number of slices
        self.number_of_slices = 384

        # number of paths per demand
        self.number_of_paths = 3

        # number of nodes in the network
        self.number_of_vertices = 12

        # number of edges in the network
        self.number_of_edges = 18

        # filename with data for X(t, n, n', p, s)
        self.file = result_file

        # filename with paths data
        self.paths_file = paths_file

        # filename with cities data
        self.cities_file = cities_file
        self.cities_dict = self.upload_cities()

        # filename with edges data
        self.edges_file = edges_file
        self.edges_dict = self.upload_edges()

        vertices_pairs = filter(lambda v: v[0] != v[1], np.ndindex(self.number_of_vertices, self.number_of_vertices))
        nodes_pairs = [(sndlib.Node(*self.cities_dict[v1]), sndlib.Node(*self.cities_dict[v2])) for v1, v2 in
                       vertices_pairs]
        self.paths_dict = {nodes: [list() for _ in range(self.number_of_paths)] for nodes in nodes_pairs}

        shape = (len(self.transponders),  # 0: t  - transponder type
                 self.number_of_vertices,  # 1: n  - node 1
                 self.number_of_vertices,  # 2: n' - node 2
                 self.number_of_paths,  # 3: p  - path
                 self.number_of_slices)  # 4: s  - slice

        self.X = np.zeros(shape=shape, dtype=int)

    def upload_edges(self):
        edges = {}
        for i, line in enumerate(self.edges_file, start=1):
            # load names of cities that are end of each edge
            link_info = line.split()[0]
            # n1, n2 = line.split()[2:4]
            n1, n2 = link_info.split('_')[1:]
            # save pixel coordinates of each edge's end
            edges[i] = sndlib.Node(*self.cities_dict[int(n1)]), sndlib.Node(*self.cities_dict[int(n2)])
        return edges

    def upload_cities(self):
        cities = {}
        for i, line in enumerate(self.cities_file):
            # load name of the city and its degree coordinates
            name, long, lati = line.replace('(', '').replace(')', '').split()

            cities[i] = name, float(long), float(lati)
        return cities

    def upload_data(self):
        """
        Load X(t, n, n', p, s) data.

        :return: five dimensional X(...) array
        """
        shape = (self.X.shape[0], self.X.shape[1], self.X.shape[3])
        for t, n1, p in np.ndindex(shape):
            self.file.readline()
            self.file.readline()
            for s in range(self.number_of_slices):
                row = self.file.readline().split()
                for n2, x in enumerate(row[1:]):
                    self.X[t, n1, n2, p, s] = int(x)
            self.file.readline()
        return self.X

    def statistics(self):
        for i, j, k in np.ndindex(self.X.shape[0], self.X.shape[1], self.X.shape[3]):
            print('{}:{}:{} -> {}'.format(i, j, k, self.X[i, j, :, k, :].sum()))

    def upload_path_row(self):
        vertex, path, edge, *row = self.paths_file.readline().split()
        vertex1, path, edge = int(vertex) - 1, int(path) - 1, int(edge)
        for vertex2, result in enumerate(row):
            if int(result):
                # if (vertex1, vertex2) in self.paths_dict:
                node1 = sndlib.Node(*self.cities_dict[vertex1])
                node2 = sndlib.Node(*self.cities_dict[vertex2])
                node3 = self.edges_dict[edge]
                self.paths_dict[(node1, node2)][path].append(node3)

    def upload_paths(self):
        """
        Load paths data.
        
        :return: dictionary of loaded paths (key: tuple of nodes, value: list of paths)
        """
        self.paths_file.readline()
        for _ in range(self.number_of_edges):
            for _ in range(self.number_of_paths):
                for _ in range(self.number_of_vertices):
                    self.upload_path_row()
                self.paths_file.readline()
            self.paths_file.readline()
        # print(self.paths_dict)
        self.organise_paths()
        return self.paths_dict

    def organise_paths(self):
        for key, values in self.paths_dict.items():
            new_values = []
            for value in values:
                organised_path = self.organise_path(key, value)
                new_values.append((len(organised_path), organised_path))
            self.paths_dict[key] = new_values

    def organise_path(self, key, path: list):
        start_node, end_node = key
        current_node = start_node
        organised_path = [start_node]
        while path:
            for edge in path:
                if edge[0] == current_node:
                    organised_path.append(edge[1])
                    path.remove(edge)
                    current_node = edge[1]
                elif edge[1] == current_node:
                    organised_path.append(edge[0])
                    path.remove(edge)
                    current_node = edge[0]
        return organised_path

    def compute_used_slices(self):
        """
        Compute used slices.

        :return: dictionary of slice usage (key: edge ID, value: used slices)
        """
        slices_in_edges = defaultdict(int)
        for t, n1, n2, p in np.ndindex(self.X.shape[:4]):
            if n1 != n2:
                used_slices = self.X[t, n1, n2, p].sum() * self.transponders[t + 1][1]
                if used_slices:
                    # print(f't={t}, n={n1}, n\'={n2}, p={p}, used_slices={used_slices}')
                    print('[{}, {}, {}, {}, {}]'.format(t + 1, n1 + 1, n2 + 1, p + 1, used_slices))
                for edge in self.paths_dict[(n2, n1)][p]:
                    slices_in_edges[edge] += used_slices
        return slices_in_edges


if __name__ == '__main__':
    # load slices usage data and compute percentage usage
    slice_usage = {}
    with open("ger3.out") as file, open("ger3.dat") as path_file:
        data_info = DataInfo(result_file=file, paths_file=path_file)
        data_info.upload_data()
        data_info.upload_paths()
        slices_in_edges = data_info.compute_used_slices()
        slice_usage = {k: (v / data_info.number_of_slices * 100) for (k, v) in slices_in_edges.items()}
        print('slices in edges:')
        pprint(slices_in_edges)
        total = sum(slices_in_edges.values())
        print(total)

    # settings for appropriate mercator displaying
    map_data = {
        'style': 'countries_basic',
        'center_long': 19.6153711,
        'center_lati': 52.0892499,
        'zoom': 5,
        'map_width': 1024,
        'map_height': 512,
        'api_token': '<mapbox api token here>'
    }

    cities = {}
    with open('cities.txt') as f:
        for line in f:
            # load name of the city and its degree coordinates
            name, long, lati = line.replace('(', '').replace(')', '').split()

            # convert degree coordinates to pixel coordinates
            x, y = geomanip.get_x(long=float(long), **map_data), geomanip.get_y(lati=float(lati), **map_data)

            # save pixel coordinates of each city
            cities[name] = x, y

    edges = {}
    with open('edges.txt') as f:
        for i, line in enumerate(f, start=1):
            # load names of cities that are end of each edge
            n1, n2 = line.split()[2:4]

            # save pixel coordinates of each edge's end
            edges[i] = cities[n1], cities[n2]

    # print('cities with positions:')
    # pprint(cities)
    # print('edges with positions:')
    # pprint(edges)
    # mapbox.get_map_as_file('map.png', mapdata=map_data)  # download map from the API, needs api_token

    # draw map
    # draw.prepare('map.png')
    #
    # # draw edges between nodes
    # for i, ((x1, y1), (x2, y2)) in enumerate(edges.values(), start=1):
    #     draw.line(x1, y1, x2, y2, marker='o', color='k')
    #     sx, sy = (x1 + x2) / 2, (y1 + y2) / 2  # middle point between nodes for annotation
    #     usage = slice_usage[i]
    #     draw.text(sx, sy, '{:.2f}% ({})'.format(usage, slices_in_edges[i]),
    #               weight='bold',
    #               color='red',
    #               fontsize=9,
    #               horizontalalignment='center')
    #
    # # draw city names
    # for city_name, (x, y) in cities.items():
    #     draw.text(x, y - 10, city_name[:2],
    #               weight='bold',
    #               color='white',
    #               fontsize=12,
    #               horizontalalignment='center',
    #               effects={'linewidth': 1, 'foreground': 'black'})
    # draw.show()
