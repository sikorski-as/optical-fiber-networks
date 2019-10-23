import random

import geneticlib
from genetic import config


class Slice:

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"{self.value}"


class Chromosome:

    def __init__(self, net, predefined_paths, transponders_config, demands, bands, slices_usage, transponders_cost):
        """
        :param predefined_paths: {} key (city1, city2)
        :param transponders_config: {} key demand
        :param demands: {} key (city1, city2)
        :param bands: [(begin, end), (begin, end)]
        :param slices_usage: amount of slices used by transponder
        """
        self.net = net
        self.predefined_paths = predefined_paths
        self.transponders_config = transponders_config
        self.demands = demands
        self.bands = bands
        self.slices_usage = slices_usage
        self.transponders_cost = transponders_cost
        self._structure = self._create_structure()
        self.slices_overflow = None
        self.power_overflow = None

    def clear_structure(self):
        self._structure = {}

    def set_structure(self, structure):
        self._structure = structure

    def _create_structure(self):
        structure = {}
        for key in self.demands:
            structure[key] = self._create_gene(key)
        return structure

    def _create_gene(self, key):
        demand = self.demands[key]
        transponder_config = random.choice(self.transponders_config[demand])
        L = []
        for transponder_type, ntransonders in enumerate(transponder_config):
            for _ in range(ntransonders):
                L.append(
                    (transponder_type, random.choice(self.predefined_paths[key]),
                     Slice(self._choose_slice(transponder_type))))
        return L

    def _choose_slice(self, transponder_type):
        slices_used = self.slices_usage[transponder_type]
        begin, end = random.choice(self.bands)
        return random.randrange(begin, end - slices_used)

    def __repr__(self):
        return f"PO:{self.power_overflow} SO:{self.slices_overflow}"

    @property
    def genes(self):
        return self._structure


def create_individual():
    """
    Creates individual without fitness value.
    :return: Individual
    """
    adapted_predefined_paths = {key: [value[1] for value in values] for key, values in config.predefined_paths.items()}
    individual = geneticlib.Individual(
        Chromosome(config.net, adapted_predefined_paths, config.transponders_config, config.demands, config.bands,
                   config.slices_usage, config.transponders_cost))
    return individual
