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

    # reds = plt.cm.ScalarMappable(cmap=plt.cm.get_cmap('Reds'))
    # reds_bar = plt.colorbar(reds, ticks=ticks, orientation='horizontal')
    # reds_bar.ax.set_xticklabels(labels)
    # reds_bar.ax.set_title('Band L')

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
    draw_topology = setup.draw_topology
    draw_usage = setup.draw_usage

    # settings for appropriate mercator displaying
    net = sndlib.UndirectedNetwork.load_native(setup.sndlib_file)
    points = net.get_list_of_coordinates()
    projection = geomanip.MercatorProjection.from_points(points=points, map_size=setup.size, padding=setup.padding)
    net.add_pixel_coordinates(projection)

    import json
    with open(setup.usage_file) as jsonf:
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
                alpha=0.5,
                linewidth=1,
                edgecolor='black',
            )

    linewidth = 5.5
    # nslices_L = sum(1 for band in data_info.bands.values() if band == 1)
    # nslices_C = sum(1 for band in data_info.bands.values() if band == 2)
    for u, v, d in net.edges(data=True):
        if draw_usage:
            eid = d['edge_id']
            C_slices = slices_in_bands[eid][1]
            # L_slices = slices_in_bands[eid][2]
            C_color = (0, 0, 1, linear_map(C_slices, 0, 192, 0.0, 1))
            # L_color = (1, 0, 0, linear_map(L_slices, 0, 100, 0.0, 1))

            # oxs, oys = draw.offset_curve([u.x, v.x], [u.y, v.y], linewidth)
            # draw.line(oxs[0], oys[0], oxs[1], oys[1], color=C_color, linewidth=linewidth, zorder=1)
            draw.line(u.x, u.y, v.x, v.y, color=C_color, linewidth=linewidth, zorder=1)
        elif draw_topology:
            draw.line(u.x, u.y, v.x, v.y, color=(0.5, 0.5, 0.5, 1), linewidth=3, zorder=1)

    for node in net.nodes:
        # draw.point([node.x], [node.y], color='black', marker='o', s=100)
        draw.circle((node.x, node.y), radius=11, color=(0.5, 0.5, 0.5, 1), zorder=2)
        if draw_topology:
            text = setup.name_mapping.get(node.name, node.name)
            draw.text(node.x, node.y - 10, text, fontsize=12, color='black', weight='bold',
                      horizontalalignment='center')

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
    # main()
    legend()
