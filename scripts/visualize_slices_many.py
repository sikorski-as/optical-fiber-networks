import json
from enum import Enum

import matplotlib.pyplot as plt

import draw
import geomanip
import jsonmanip
import sndlib


def linear_map(value, a, b, new_a, new_b):
    ret = new_a + (value - a) / (b - a) * (new_b - new_a)
    return ret


def legend():
    plt.clf()
    ticks = [0.0, 0.25, 0.5, 0.75, 1.0]
    labels = ['{}%'.format(int(x * 100)) for x in ticks]

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


class DrawMode(Enum):
    TOPOLOGY = 0
    USAGE_AS_COLORS = 1
    USAGE_AS_STYLED_LINES = 2


class setup:
    # sndlib_file = 'data/sndlib/json/abilene/abilene.json'
    sndlib_file = 'data/sndlib/json/polska/polska.json'
    usage_file = 'data/slices_usage_from_preprocessed_excel.json'

    size = (768 * 2, 768 * 2)
    padding = 250
    linewidth = 6.5
    node_size = 6

    latitude_center_translation = 0.0
    longitude_center_translation = 0
    zoom_modifier = 0.15

    draw_border = True
    countries = ['pol']

    fontsize = 25
    draw_topology = True
    name_mapping = {
        'SanFrancisco': 'San\nFrancisco',
        'Lodz': 'Łódź',
        'Bialystok': 'Białystok',
        'Kolobrzeg': 'Kołobrzeg',
        'Poznan': 'Poznań',
        'Krakow': 'Kraków',
        'Wroclaw': 'Wrocław',
        'Warsaw': 'Warszawa',
        'Rzeszow': 'Rzeszów',
        'Gdansk': 'Gdańsk',
        'Bydgoszcz': 'Bydgoszcz',
        'Katowice': 'Katowice',
        'Szczecin': 'Szczecin',
    }

    edge_draw_mode = DrawMode.USAGE_AS_STYLED_LINES
    assert isinstance(edge_draw_mode, DrawMode)

    save_output = True
    output_image_file_template = 'output/{}.pdf'

    # converts dict-like object loaded from setup.usage_file
    # into iterator of (NAME, SLICES_USAGE_DATA) tuples
    iterator_maker = lambda data: ((table_name + '_' + year, year_data)
                                   for table_name, table_data in data.items()
                                   for year, year_data in table_data.items())


def main():
    # settings for appropriate mercator displaying
    net = sndlib.UndirectedNetwork.load_json(setup.sndlib_file)
    points = net.get_list_of_coordinates()
    projection = geomanip.MercatorProjection.from_points(points=points, map_size=setup.size, padding=setup.padding)
    projection.center_lati += setup.latitude_center_translation
    projection.center_long += setup.longitude_center_translation
    projection.zoom += setup.zoom_modifier

    net.add_pixel_coordinates(projection)

    with open(setup.usage_file) as jsonf:
        raw = json.load(jsonf)

    for output_filename, data in setup.iterator_maker(raw):
        done = {}
        for edge in range(1, net.number_of_edges() + 1):
            raw_one = data.get('Edge {}'.format(edge), {})
            done[edge] = {
                1: raw_one.get('Band 1', 0),
                2: raw_one.get('Band 2', 0),
            }

        slices_in_bands = done

        draw.prepare_empty(*setup.size)
        if setup.draw_border:
            for country in setup.countries:
                for feature in jsonmanip.get_features(jsonmanip.load_geojson(country)):
                    polys = jsonmanip.get_list_of_polygons(feature)
                    for poly in polys:
                        for j, point in enumerate(poly):
                            poly[j] = projection.get_xy(*point)
                    draw.polygons(
                        polys,
                        closed=True,
                        facecolor='white',
                        alpha=1,
                        linewidth=1,
                        edgecolor=(0.5, 0.5, 0.5, 1.0),
                    )

        for u, v, d in net.edges(data=True):
            eid = d['edge_id']
            if setup.edge_draw_mode == DrawMode.TOPOLOGY:
                draw.line(u.x, u.y, v.x, v.y, color=(0.5, 0.5, 0.5, 1), linewidth=3, zorder=1)
            elif setup.edge_draw_mode == DrawMode.USAGE_AS_COLORS:
                C_slices = slices_in_bands[eid][1]
                # L_slices = slices_in_bands[eid][2]
                C_color = (0, 0, 1, linear_map(C_slices, 0, 192, 0.0, 1))
                # L_color = (1, 0, 0, linear_map(L_slices, 0, 100, 0.0, 1))
                # oxs, oys = draw.offset_curve([u.x, v.x], [u.y, v.y], linewidth)
                # draw.line(oxs[0], oys[0], oxs[1], oys[1], color=C_color, linewidth=linewidth, zorder=1)
                draw.line(u.x, u.y, v.x, v.y, color=C_color, linewidth=setup.linewidth, zorder=1)
            elif setup.edge_draw_mode == DrawMode.USAGE_AS_STYLED_LINES:
                percent = slices_in_bands[eid][1] / 96 * 100

                linestyle, linecolor = \
                    ('-', (0, 0, 0, 0)) if percent == 0 \
                        else ('-', 'lightgreen') if percent < 70 \
                        else ('--', 'yellow') if percent < 90 \
                        else ('-.', 'orange') if percent < 99 \
                        else (':', 'red')

                print(linestyle, percent)
                draw.line(u.x, u.y, v.x, v.y,
                          color=linecolor,
                          linewidth=setup.linewidth,
                          linestyle=linestyle,
                          zorder=1)

        for node in net.nodes:
            BLACK = (0.0, 0.0, 0.0, 1)
            GREY = (0.5, 0.5, 0.5, 1)
            draw.circle((node.x, node.y), radius=setup.node_size, color=BLACK, zorder=2)
            if setup.draw_topology:
                text = setup.name_mapping.get(node.name, node.name)
                draw.text(node.x, node.y - 10, text, fontsize=setup.fontsize, color='black', weight='bold',
                          horizontalalignment='center')

        if setup.save_output:
            draw.save_as(setup.output_image_file_template.format(output_filename))
        else:
            draw.show()


if __name__ == '__main__':
    main()
