from pprint import pprint
from collections import defaultdict
import numpy as np
import mapbox
import geomanip
import draw
import os
import sndlib
import re


def linear_map(value, a, b, new_a, new_b):
    ret = new_a + (value - a) / (b - a) * (new_b - new_a)
    return ret


class SlicesAnalyzer:
    """
        transponders -> key - int, value -> (x, y) x - bitrate, y - slices used
        number_of_vertices -> amount of cities
    """

    def __init__(self, result_file, paths_file, nvertices, nedges, nslices, npaths, transponders=None):
        """

        :param result_file: .out file
        :param paths_file: .dat_file
        :param transponders: dictionairy of usage
        :param nslices: number of slices
        :param npaths: number of paths
        :param nvertices: number of vertices
        :param nedges: number of edges
        """
        # demanded value, unused
        self.demand = 1600

        # transponder type -> (bitrate, used slices)
        self.transponders = transponders if transponders is not None else {1: (40, 1), 2: (100, 1), 3: (200, 1)}

        # summary number of slices
        self.number_of_slices = nslices  # 384

        # number of paths per demand
        self.number_of_paths = npaths  # 3

        # number of nodes in the network
        self.number_of_vertices = nvertices  # 17

        # number of edges in the network
        self.number_of_edges = nedges  # 26

        # filename with data for X(t, n, n', p, s) and FREQB (which slices are in which band)
        self.file = result_file

        # filename with paths data
        self.paths_file = paths_file

        # slices in bands
        self.bands = {}

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
        Load X(t, n, n', p, s).

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

    def upload_bands_data(self):
        line = ''
        while not line.startswith('set FREQB['):
            line = self.paths_file.readline()

        while line.startswith('set FREQB['):
            match = re.search(r'set FREQB\[(\d+)\]:= ((\d+\s?)+)', line)
            band, numbers = int(match.group(1)), [int(x) for x in match.group(2).split()]
            # print(band, numbers)
            for slice_num in numbers:
                self.bands[slice_num] = band
            line = self.paths_file.readline()

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

    def compute_used_slices_in_bands(self):
        """
        Compute used slices.

        :return: dictionary of slice usage (key: edge ID, value: dict of used slices)
        """
        slices_in_edges = defaultdict(dict)
        for t, n1, n2, p, s in np.ndindex(self.X.shape):
            if n1 != n2:
                used_slices = self.X[t, n1, n2, p, s] * self.transponders[t + 1][1]
                band = self.bands[s + 1]

                for edge in self.paths_dict[(n2, n1)][p]:
                    slices_in_edges[edge][band] = slices_in_edges[edge].get(band, 0) + used_slices
        return slices_in_edges


if __name__ == '__main__':
    with open("../data/ger3.out") as file, open("../data/ger3.dat") as path_file:
        data_info = SlicesAnalyzer(
            result_file=file, paths_file=path_file,
            nvertices=17,
            nedges=26,
            npaths=3,
            nslices=384
        )
        data_info.upload_data()
        data_info.upload_paths()
        data_info.upload_bands_data()
        slices_in_edges = data_info.compute_used_slices()
        slices_in_bands = data_info.compute_used_slices_in_bands()
        slice_usage = {k: (v / data_info.number_of_slices * 100) for (k, v) in slices_in_edges.items()}
        print('slices in edges (by band):')
        pprint(slices_in_bands)

    # settings for appropriate mercator displaying
    net = sndlib.UndirectedNetwork.load_native('../data/nobel-germany.txt')
    points = net.get_list_of_coordinates()
    projection = geomanip.MercatorProjection.from_points(points=points, map_size=(768, 1024), padding=75)
    net.add_pixel_coordinates(projection)

    status = mapbox.get_map_as_file(
        '../data/map-germany.png',
        replace=True,
        api_token=os.environ['MAPBOX_API_KEY'],
        projection=projection,
        style='countries_basic',
    )
    print('Map ' + ('' if status else 'not ') + 'dowloaded')

    draw.prepare('../data/map-germany.png', draw=True)

    linewidth = 3
    nslices_L = sum(1 for band in data_info.bands.values() if band == 1)
    nslices_C = sum(1 for band in data_info.bands.values() if band == 2)
    for u, v, d in net.edges(data=True):
        eid = d['edge_id']
        C_slices = slices_in_bands[eid][1]
        L_slices = slices_in_bands[eid][2]
        C_color = (0, 0, 1, linear_map(C_slices, 0, nslices_C, 0.0, 1))
        L_color = (1, 0, 0, linear_map(L_slices, 0, nslices_L, 0.0, 1))

        oxs, oys = draw.offset_curve([u.x, v.x], [u.y, v.y], linewidth)
        # draw.line(u.x, u.y, v.x, v.y, marker='', color=(1.0, 0.0, 0.0, L_slices / 384), linewidth=lw)
        # draw.line(u.x + xtr, u.y + ytr, v.x + xtr, v.y + ytr, marker='', color='orange', linewidth=lw / 2)

        draw.line(oxs[0], oys[0], oxs[1], oys[1], color=C_color, linewidth=linewidth)
        draw.line(u.x, u.y, v.x, v.y, color=L_color, linewidth=linewidth)

        # draw.line(u.x, u.y, v.x, v.y, marker='o', color='gray', linewidth=2)
        # sx, sy = net.edge_middle_point(u, v, pixel_value=True)
        # draw.text(
        #     sx, sy,
        #     f'L: {L_slices}, C: {C_slices}',
        #     fontsize=8,
        #     color='navy',
        #     weight='bold',
        #     horizontalalignment='center'
        # )

    for node in net.nodes:
        text = node.name
        draw.text(node.x, node.y, text, fontsize=8, color='black', weight='bold', horizontalalignment='center')

    draw.show()
    # draw.save_as('../output/lc_band.png')
