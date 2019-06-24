import math
from typing import Tuple


class Projection:
	"""
	Represent geographical map projection
	"""
	def __init__(self, map_size, center=(0.0, 0.0), zoom=1.0, chunk_size=(256, 256)):
		self.map_width = map_size[0]
		self.map_height = map_size[1]
		self.center_long = center[0]
		self.center_lati = center[1]
		self.zoom = zoom
		self.chunk_width = chunk_size[0]
		self.chunk_height = chunk_size[1]


class MercatorProjection(Projection):
	"""
	Represent Mercator projection
	"""
	def __init__(self, map_size, center=(0.0, 0.0), zoom=1.0, chunk_size=(256, 256)):
		super(MercatorProjection, self).__init__(map_size, center, zoom, chunk_size)

	def longitude_to_x(self, long: float) -> float:
		long = math.radians(long)
		ret = self.chunk_width/math.pi * math.pow(2, self.zoom) * (long + math.pi)
		return ret

	def latitude_to_y(self, lati: float) -> float:
		lati = math.radians(lati)
		a = self.chunk_height/math.pi
		b = math.pow(2, self.zoom)
		c = math.pi - math.log(math.tan((math.pi / 4) + lati / 2))
		return a * b * c

	def get_x(self, long: float) -> float:
		return self.longitude_to_x(long) - self.longitude_to_x(self.center_long) + self.map_width / 2

	def get_y(self, lati: float) -> float:
		return self.latitude_to_y(lati) - self.latitude_to_y(self.center_lati) + self.map_height / 2

	def get_xy(self, long: float, lati: float) -> Tuple[float, float]:
		return self.get_x(long), self.get_y(lati)


def haversine(lon1, lat1, lon2, lat2):
	"""
	Calculate the great circle distance between two points
	on the earth (specified in decimal degrees)
	"""
	# convert decimal degrees to radians
	lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

	# haversine formula
	dlon = lon2 - lon1
	dlat = lat2 - lat1
	a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
	c = 2 * math.asin(math.sqrt(a))
	r = 6371  # Radius of earth in kilometers. Use 3956 for miles
	return c * r
