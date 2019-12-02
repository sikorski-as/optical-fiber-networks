import math
from typing import Tuple
from operator import itemgetter


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
    def __init__(self, map_size, center=(0.0, 0.0), zoom=1.0):
        super(MercatorProjection, self).__init__(map_size, center, zoom, chunk_size=(256, 256))

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

    @classmethod
    def from_points(cls, points, map_size, padding=0):
        print(f'Warning: calling experimental function {cls.__name__}.from_points')
        if any(point[0] < -180 or point[0] > 180 or point[1] > 90 or point[1] < -90 for point in points):
            raise ValueError('Coordinates not in ranges [-180, 180], [-90, 90]')

        projection = cls(map_size=map_size, center=(0, 0), zoom=0)

        x, y = itemgetter(0), itemgetter(1)
        left = min(points, key=x)
        right = max(points, key=x)
        top = min(points, key=y)
        bottom = max(points, key=y)

        bounds = [left, right, top, bottom]
        px_bounds = [projection.get_xy(*point) for point in bounds]

        projection.center_long = (left[0] + right[0]) / 2
        projection.center_lati = (top[1] + bottom[1]) / 2

        while all(padding < p[0] < map_size[0] - padding and padding < p[1] < map_size[1] - padding for p in px_bounds):
            px_bounds = [projection.get_xy(*point) for point in bounds]
            projection.zoom += 0.05

        projection.zoom -= 0.05

        return projection


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
    r = 6373  # Radius of earth in kilometers. Use 3956 for miles
    return c * r
