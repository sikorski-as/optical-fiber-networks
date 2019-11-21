import jsonpickle
import math
from functools import lru_cache
from pprint import pformat, pprint
import networkx as nx
import structure
import geneticlib
import time
import sndlib
import timer
import utils
import yen
import genetic.transponders as tconfiger
# import genetic.transponder_config as t_config
from geneticlib import Individual


@lru_cache(maxsize=1024)
def dist(a, b):
    return sndlib.calculate_haversine_distance_between_each_node(net)[a][b]


K = 3  # number of predefined paths

net_name = 'janos-us'
dat_source_prefix = 'janos-us'
intensity = 1

intensity_str = f"{intensity}".replace(".", "")
net = sndlib.create_undirected_net(net_name, calculate_distance=True, calculate_reinforcement=True, calculate_ila=True)
net.load_demands_from_datfile(f'data/{dat_source_prefix}{intensity_str}.dat')
predefined_paths = utils.get_predefined_paths(network_filename=f"data/sndlib/json/{net_name}/{net_name}.json",
                                              dat_filename=f"data/{dat_source_prefix}{intensity_str}.dat", npaths=K)

# demands = {key: DEMAND for key in predefined_paths}
# transponders_config = {DEMAND: t_config.create_config([(40, 4), (100, 4), (200, 8), (400, 12)], DEMAND, 3)}
t_config_file = 'data/transponder_configs_ip_5.json'
transponders_config = tconfiger.load_config(t_config_file)

# for config_key in transponders_config:
#     transponders_config[config_key] = transponders_config[config_key][2:]

demands = {key: math.ceil(value) for key, value in net.demands.items()}

chromosome_type = structure.MultipleSubgeneChromosome

slices_usage = {
    0: 1,
    1: 1,
    2: 2,
    3: 3
}

b_cost = {
    0: 1,
    1: 2
}

transponders_cost = {
    (0, 0): 2,
    (1, 0): 5,
    (2, 0): 7,
    (3, 0): 9,
    (0, 1): 2.4,
    (1, 1): 6,
    (2, 1): 8.4,
    (3, 1): 11.8,
}

clock = timer.Clock()

bands = [(0, 192), (192, 384)]  # ranges of slices per band

OSNR = {
    0: 10,
    1: 15.85,
    2: 31.62,
    3: 158.49
}
e = 2.718
h = 6.62607004 * pow(10, -34)
freq = {
    0: 193800000000000.0,
    1: 188500000000000.0
}
l = {
    0: 0.046,
    1: 0.055
}
bandwidth = {
    0: 25000000000.0,
    1: 25000000000.0,
    2: 50000000000.0,
    3: 75000000000.0
}

V = 31.62
W = 31.62
P = 0.001

tools = geneticlib.Toolkit()
tools.set_fitness_weights(weights=(-1,))


def save_result(best_result: Individual, file_name: str):
    """
    demandy, użyte transpondery dla danego połączenia, stan sieci(slice`y)?
    suma użytych transponderów każdego typu
    :param best_result:
    :param file_name
    :return:
    """
    best_chromosome = best_result.chromosome
    ndemands = len(best_chromosome.demands.values())
    # structure = pformat(best_chromosome.genes, indent=1)
    structure = best_chromosome.genes
    total_transponders_used = best_chromosome.total_transponders_used
    band_usage, edge_usage = best_chromosome.calculate_band_edge_usage()
    sorted_subgenes = best_chromosome.sorted_subgenes(sortfun=lambda x: x[2].value)

    result = {
        "Number of demands": ndemands,
        "Cost": best_result.values[0],
        "Transponders used": total_transponders_used,
        "Sorted paths": sorted_subgenes,
        "Power overflow": best_chromosome.power_overflow,
        "Slices overflow": best_chromosome.slices_overflow,
        "Transponders config": t_config_file,
        "Total time": clock.time_elapsed(),
        "Structure": structure,
        "Band info": band_usage,
        "Edge info": edge_usage,
        "Chromosome type": best_chromosome.__class__
    }
    print(result)
    file_name = f"{file_name}_{time.time()}"

    with open(f'results/{file_name}', mode='w') as file:
        file.write(jsonpickle.encode(result))