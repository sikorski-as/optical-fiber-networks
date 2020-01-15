import json

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


class setup:
    sndlib_file = 'data/sndlib/json/germany50/germany50.json'
    usage_file = 'data/usage.json'

    size = (512 * 2, 768 * 2)
    padding = 60
    linewidth = 5.5
    node_size = 6

    draw_border = True
    country = 'deu'

    draw_topology = True
    name_mapping = {
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

    draw_usage = False
    save_output = True
    output_image_file = 'results/germany50.png'


def main():
    # settings for appropriate mercator displaying
    net = sndlib.UndirectedNetwork.load_json(setup.sndlib_file)
    points = net.get_list_of_coordinates()
    projection = geomanip.MercatorProjection.from_points(points=points, map_size=setup.size, padding=setup.padding)
    net.add_pixel_coordinates(projection)

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

    draw.prepare_empty(*setup.size)
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

    for u, v, d in net.edges(data=True):
        if setup.draw_usage:
            eid = d['edge_id']
            C_slices = slices_in_bands[eid][1]
            # L_slices = slices_in_bands[eid][2]
            C_color = (0, 0, 1, linear_map(C_slices, 0, 192, 0.0, 1))
            # L_color = (1, 0, 0, linear_map(L_slices, 0, 100, 0.0, 1))

            # oxs, oys = draw.offset_curve([u.x, v.x], [u.y, v.y], linewidth)
            # draw.line(oxs[0], oys[0], oxs[1], oys[1], color=C_color, linewidth=linewidth, zorder=1)
            draw.line(u.x, u.y, v.x, v.y, color=C_color, linewidth=setup.linewidth, zorder=1)
        elif setup.draw_topology:
            draw.line(u.x, u.y, v.x, v.y, color=(0.5, 0.5, 0.5, 1), linewidth=3, zorder=1)

    for node in net.nodes:
        draw.circle((node.x, node.y), radius=setup.node_size, color=(0.5, 0.5, 0.5, 1), zorder=2)
        if setup.draw_topology:
            text = setup.name_mapping.get(node.name, node.name)
            draw.text(node.x, node.y - 10, text, fontsize=12, color='black', weight='bold',
                      horizontalalignment='center')

    if setup.save_output:
        draw.save_as(setup.output_image_file)
    else:
        draw.show()


if __name__ == '__main__':
    main()
    # legend()
