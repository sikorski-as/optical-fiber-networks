from sndlib import Network
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
	print('Map ' + ('' if status else 'not ') + 'dowloaded')

	net = Network.load_native('data/polska.txt')
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


if __name__ == '__main__':
	example_sndlib_draw_geomanip()