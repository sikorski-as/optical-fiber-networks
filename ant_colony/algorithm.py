import sndlib
import mapbox
import draw
from pathlib import Path
from geomanip import MercatorProjection
from ant_colony.ant import Ant, Colony
from ant_colony.world import World


def algorithm(filepath, iterations, number_of_ants, select_function, assessment_function):
    filename = Path(filepath).name
    net = sndlib.UndirectedNetwork.load_native(filepath)
    projection = MercatorProjection.from_points(net.get_list_of_coordinates(), map_size=(1024, 768), padding=50)
    world = World(net, 0.05, 0.1, False, 1, 1, 1)
    colony = Colony(...)

