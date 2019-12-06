import os
import re
from collections import defaultdict
from pprint import pprint

import matplotlib.pyplot as plt
import numpy as np

import draw
import geomanip
import jsonmanip
import mapbox
import sndlib


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
            print('{}:{}:{} -> {}'.format(i, j, k, self.X[i, j, :, k, :].sum()))

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


def legend():
    plt.clf()
    ticks = [0.0, 0.25, 0.5, 0.75, 1.0]
    labels = ['{}%'.format(int(x * 100)) for x in ticks]

    # w, h = 1, 1
    # ax = blues_bar.ax
    # l = ax.figure.subplotpars.left
    # r = ax.figure.subplotpars.right
    # t = ax.figure.subplotpars.top
    # b = ax.figure.subplotpars.bottom
    # figw = float(w) / (r - l)
    # figh = float(h) / (t - b)
    # ax.figure.set_size_inches(figh)

    reds = plt.cm.ScalarMappable(cmap=plt.cm.get_cmap('Reds'))
    reds_bar = plt.colorbar(reds, ticks=ticks, orientation='horizontal')
    reds_bar.ax.set_xticklabels(labels)
    reds_bar.ax.set_title('Band L')

    blues = plt.cm.ScalarMappable(cmap=plt.cm.get_cmap('Blues'))
    blues_bar = plt.colorbar(blues, ticks=ticks, orientation='horizontal')
    blues_bar.ax.set_xticklabels(labels)
    blues_bar.ax.set_title('Band C')

    plt.axis('off')
    # plt.xlim(0, 0)
    # plt.ylim(0, 0)

    draw.save_as('legend.pdf')


def main():
    from scripts.slices_configs import polska as setup
    draw_topology = False
    draw_usage = True

    # settings for appropriate mercator displaying
    net = sndlib.UndirectedNetwork.load_native(setup.sndlib_file)
    points = net.get_list_of_coordinates()
    projection = geomanip.MercatorProjection.from_points(points=points, map_size=setup.size, padding=setup.padding)
    net.add_pixel_coordinates(projection)

    with open(setup.out_file) as file, open(setup.data_file) as path_file:
        data_info = SlicesAnalyzer(
            result_file=file, paths_file=path_file,
            nvertices=net.number_of_nodes(),
            nedges=net.number_of_edges(),
            npaths=setup.npaths,
            nslices=setup.nslices
        )
        data_info.upload_data()
        data_info.upload_paths()
        data_info.upload_bands_data()
        slices_in_edges = data_info.compute_used_slices()
        slices_in_bands = data_info.compute_used_slices_in_bands()
        slice_usage = {k: (v / data_info.number_of_slices * 100) for (k, v) in slices_in_edges.items()}
        print('slices in edges (by band):')
        pprint(slices_in_bands)

    import json
    with open('data/usage.json') as jsonf:
        raw = json.load(jsonf)

    done = {}

    for edge in range(1, net.number_of_edges() + 1):
        raw_one = raw.get('Edge {}'.format(edge), {})
        done[edge] = {
            1: raw_one.get('Band 1', 0),
            2: raw_one.get('Band 2', 0),
        }

    slices_in_bands = done

    if setup.download_map:
        status = mapbox.get_map_as_file(
            setup.map_file,
            replace=True,
            api_token=os.environ['MAPBOX_API_KEY'],
            projection=projection,
            style='countries_basic',
        )
        print('Map ' + ('' if status else 'not ') + 'dowloaded')

    draw.prepare(setup.map_file, draw=setup.draw_map)
    if setup.draw_border:
        for feature in jsonmanip.get_features(jsonmanip.load_geojson(setup.country)):
            polys = jsonmanip.get_list_of_polygons(feature)
            for poly in polys:
                for j, point in enumerate(poly):
                    poly[j] = projection.get_xy(*point)
            draw.polygons(
                polys,
                closed=True,
                facecolor='white',
                # alpha=1.0,
                linewidth=1,
                edgecolor='black',
            )

    linewidth = 5.5
    nslices_L = sum(1 for band in data_info.bands.values() if band == 1)
    nslices_C = sum(1 for band in data_info.bands.values() if band == 2)
    for u, v, d in net.edges(data=True):
        if draw_usage:
            eid = d['edge_id']
            C_slices = slices_in_bands[eid][1]
            L_slices = slices_in_bands[eid][2]
            C_color = (0, 0, 1, linear_map(C_slices, 0, 100, 0.0, 1))
            L_color = (1, 0, 0, linear_map(L_slices, 0, 100, 0.0, 1))

            oxs, oys = draw.offset_curve([u.x, v.x], [u.y, v.y], linewidth)
            draw.line(oxs[0], oys[0], oxs[1], oys[1], color=C_color, linewidth=linewidth, zorder=1)
            draw.line(u.x, u.y, v.x, v.y, color=L_color, linewidth=linewidth, zorder=1)
        elif draw_topology:
            draw.line(u.x, u.y, v.x, v.y, color=(0.5, 0.5, 0.5, 1), linewidth=3, zorder=1)

    for node in net.nodes:
        # draw.point([node.x], [node.y], color='black', marker='o', s=100)
        draw.circle((node.x, node.y), radius=11, color=(0.5, 0.5, 0.5, 1), zorder=2)
        if draw_topology:
            text = setup.name_mapping.get(node.name, node.name)
            draw.text(node.x, node.y - 10, text, fontsize=12, color='black', weight='bold', horizontalalignment='center')

    # blues = plt.cm.ScalarMappable(cmap=plt.cm.get_cmap('Blues'))
    # blues_bar = plt.colorbar(blues, ticks=[0, 1])
    # blues_bar.ax.set_yticklabels(['0%', '100%'])
    #
    # # w, h = 1, 1
    # # ax = blues_bar.ax
    # # l = ax.figure.subplotpars.left
    # # r = ax.figure.subplotpars.right
    # # t = ax.figure.subplotpars.top
    # # b = ax.figure.subplotpars.bottom
    # # figw = float(w) / (r - l)
    # # figh = float(h) / (t - b)
    # # ax.figure.set_size_inches(figh)
    #
    # blues_bar.ax.set_title('Band C')
    #
    # reds = plt.cm.ScalarMappable(cmap=plt.cm.get_cmap('Reds'))
    # reds_bar = plt.colorbar(reds, ticks=[0, 1])
    # reds_bar.ax.set_yticklabels(['0%', '100%'])
    # # reds_bar.ax.subplots_adjust()
    # # plt.bar(range(len(y)), y, color=colors)
    # reds_bar.ax.set_title('Band L')

    if setup.save_output:
        draw.save_as(setup.output_image_file)
    else:
        draw.show()


if __name__ == '__main__':
    main()
    # legend()
