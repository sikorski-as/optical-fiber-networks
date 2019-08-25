from pprint import pprint
from collections import defaultdict
import numpy as np
import mapbox
import geomanip
import draw
import os
import sndlib


class DataInfo:
    """
        transponders -> key - int, value -> (x, y) x - bitrate, y - slices used
        number_of_vertices -> amount of cities
    """

    def __init__(self, result_file, paths_file):
        # demanded value, unused
        self.demand = 1600

        # transponder type -> (bitrate, used slices)
        self.transponders = {1: (40, 1), 2: (100, 1), 3: (200, 1)}

        # summary number of slices
        self.number_of_slices = 384

        # number of paths per demand
        self.number_of_paths = 3

        # number of nodes in the network
        self.number_of_vertices = 17

        # number of edges in the network
        self.number_of_edges = 26

        # filename with data for X(t, n, n', p, s)
        self.file = result_file

        # filename with paths data
        self.paths_file = paths_file

        vertices_pairs = filter(lambda v: v[0] != v[1], np.ndindex(self.number_of_vertices, self.number_of_vertices))
        self.paths_dict = {verts: [list() for _ in range(self.number_of_paths)] for verts in vertices_pairs}

        shape = (len(self.transponders),  # 0: t  - transponder type
                 self.number_of_vertices,  # 1: n  - node 1
                 self.number_of_vertices,  # 2: n' - node 2
                 self.number_of_paths,  # 3: p  - path
                 self.number_of_slices)  # 4: s  - slice

        self.X = np.zeros(shape=shape, dtype=int)

    def upload_data(self):
        """
        Load X(t, n, n', p, s) data.

        :return: five dimensional X(...) array
        """
        # ones = 0
        shape = (self.X.shape[0], self.X.shape[1], self.X.shape[3])
        for t, n1, p in np.ndindex(shape):
            self.file.readline()
            self.file.readline()
            for s in range(self.number_of_slices):
                row = self.file.readline().split()
                for n2, x in enumerate(row[1:]):
                    self.X[t, n1, n2, p, s] = int(x)
                    # if int(x) == 1:
                    #     ones += 1
            self.file.readline()
        # print(ones)
        return self.X

    def statistics(self):
        for i, j, k in np.ndindex(self.X.shape[0], self.X.shape[1], self.X.shape[3]):
            print(f'{i}:{j}:{k} -> {self.X[i, j, :, k, :].sum()}')

    def upload_path_row(self):
        vertex, path, edge, *row = self.paths_file.readline().split()
        vertex1, path, edge = int(vertex) - 1, int(path) - 1, int(edge)
        for vertex2, result in enumerate(row):
            if int(result):
                self.paths_dict[(vertex1, vertex2)][path].append(edge)

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
        return self.paths_dict

    def compute_used_slices(self):
        """
        Compute used slices.

        :return: dictionary of slice usage (key: edge ID, value: used slices)
        """
        slices_in_edges = defaultdict(int)
        for t, n1, n2, p in np.ndindex(self.X.shape[:4]):
            if n1 != n2:
                used_slices = self.X[t, n1, n2, p].sum() * self.transponders[t + 1][1]
                # print(f't={t}, n={n1}, n\'={n2}, p={p}, used_slices={used_slices}')
                for edge in self.paths_dict[(n2, n1)][p]:
                    slices_in_edges[edge] += used_slices
        return slices_in_edges


if __name__ == '__main__':
    # load slices usage data and compute percentage usage
    # slice_usage = {}
    with open("../data/ger3.out") as file, open("../data/ger3.dat") as path_file:
        data_info = DataInfo(result_file=file, paths_file=path_file)
        data_info.upload_data()
        data_info.upload_paths()
        slices_in_edges = data_info.compute_used_slices()
        slice_usage = {k: (v / data_info.number_of_slices * 100) for (k, v) in slices_in_edges.items()}
        print('slices in edges:')
        pprint(slices_in_edges)
        print(sum(slices_in_edges.values()))

    # settings for appropriate mercator displaying
    net = sndlib.UndirectedNetwork.load_native('../data/nobel-germany.txt')
    points = net.get_list_of_coordinates()
    projection = geomanip.MercatorProjection.from_points(points=points, map_size=(768, 1024), padding=125)
    net.add_pixel_coordinates(projection)

    status = mapbox.get_map_as_file(
        '../data/map-germany.png',
        replace=True,
        api_token=os.environ['MAPBOX_API_KEY'],
        projection=projection,
        style='countries_basic',
    )
    print('Map ' + ('' if status else 'not ') + 'dowloaded')

    draw.prepare('../data/map-germany.png')
    for node in net.nodes:
        draw.text(node.x, node.y, node.name, fontsize=6, color='black', weight='bold', horizontalalignment='center')

    for u, v, d in net.edges(data=True):
        sx, sy = net.edge_middle_point(u, v, pixel_value=True)
        draw.line(u.x, u.y, v.x, v.y, marker='o', color='gray')
        draw.text(
            sx, sy,
            f'{slices_in_edges[d["edge_id"]]}',
            fontsize=7,
            color='navy',
            weight='bold',
            horizontalalignment='center'
        )

    draw.show()
