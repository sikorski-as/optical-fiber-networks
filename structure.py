import copy
import random
from collections import defaultdict
import bitstring
import geneticlib
import utils
from main_config import e, l, bandwidth, P, OSNR, h, freq, W, V
import main_config


class Slice:

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"{self.value}"


class Chromosome:

    def __init__(self, net, predefined_paths, transponders_config, bands, slices_usage, transponders_cost):
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
        self.demands = net._demands
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
    adapted_predefined_paths = {key: [value[1] for value in values] for key, values in main_config.predefined_paths.items()}
    individual = geneticlib.Individual(
        Chromosome(main_config.net, adapted_predefined_paths, main_config.transponders_config, main_config.bands,
                   main_config.slices_usage, main_config.transponders_cost))
    return individual


def change_path(gene, predefined_paths):
    new_gene = gene[0], random.choice(predefined_paths), gene[2]
    return new_gene


def mutate_gene(gene, predefined_paths):
    for i, subgene in enumerate(gene):
        gene[i] = change_path(subgene, predefined_paths)


def fitness(chromosome):
    cost = chromosome.transponders_cost
    total_cost = 0

    # version 1
    slices_overflow, bands_usage = _allocate_slices(chromosome.genes.values(), chromosome.bands,
                                                    chromosome.slices_usage)
    chromosome.slices_overflow = slices_overflow
    # version 2
    # slices_overflow = 0
    # slices_usage = defaultdict(set)
    # for gene in chromosome.genes.values():
    #     for subgene in gene:
    #         for edge in utils.pairwise(subgene[1]):
    #             for slice in range(subgene[2].value, subgene[2].value + chromosome.slices_usage[subgene[0]]):
    #                 if slice in slices_usage[edge]:
    #                     slices_overflow += 1
    #                 else:
    #                     slices_usage[edge].add(slice)

    for gene in chromosome.genes.values():
        for subgene in gene:
            band = 0 if subgene[2].value <= chromosome.bands[0][1] else 1
            total_cost += cost[subgene[0], band]

    power_overflow = _check_power(chromosome)
    # print(slices_overflow)
    # print(total_cost)
    amplifiers_cost = sum([main_config.b_cost[key] * value for key, value in bands_usage.items()])
    return total_cost * pow(2.72, power_overflow*1000) + pow(slices_overflow, 2) + amplifiers_cost


def _check_power(chromosome: Chromosome):
    # node_reinforcement = sndlib.calculate_reinforcement_for_each_node(chromosome.net)

    power_overflow = 0
    for subgene in chromosome.genes.values():
        for transponder_type, path, slice in subgene:
            band = 0 if slice.value <= chromosome.bands[0][1] else 1
            total = 0
            for edge in utils.pairwise(path):
                total += chromosome.net.edges[edge]['ila'] * (pow(e, l[band] * chromosome.net.edges[edge]['distance'] /
                                                                  (1 + chromosome.net.edges[edge]['ila'])) + V - 2)
                total += pow(e, l[band] * chromosome.net.edges[edge]['distance'] / (1 + chromosome.net.edges[edge]['ila'])
                             ) + W - 2
            total *= h * freq[band] * OSNR[transponder_type] * bandwidth[transponder_type]
            # print(total)
            if total > P:
                power_overflow += total
    chromosome.power_overflow = power_overflow
    return power_overflow


def _allocate_slices(genes, bands, transponder_slices_usage):
    slices_usage = defaultdict(lambda: bitstring.BitArray(bands[1][1]))
    flatten_subgenes = [subgene for gene in genes for subgene in gene]
    sorted_subgenes = sorted(flatten_subgenes, key=lambda x: len(x[1]), reverse=True)
    slices_overflow = 0
    edges_used = defaultdict(set)
    bands_usage = defaultdict(int)  # counts edges used in each band

    for subgene in sorted_subgenes:
        path_slices_utilization = None
        for edge in utils.pairwise(subgene[1]):
            edge = tuple(sorted(edge))
            if path_slices_utilization is not None:
                path_slices_utilization = path_slices_utilization | slices_usage[edge]
            else:
                path_slices_utilization = slices_usage[edge]
        slices_used = _use_slices(transponder_slices_usage[subgene[0]], path_slices_utilization, bands)
        if slices_used:
            for edge in utils.pairwise(subgene[1]):
                edge = tuple(sorted(edge))
                slices_usage[edge].set(1, [i for i in range(slices_used[0], slices_used[1] + 1)])
                band = 0 if slices_used[0] <= main_config.bands[0][1] else 1
                if edge not in edges_used[band]:
                    bands_usage[band] += 1
                    edges_used[band].add(edge)
            subgene[2].value = slices_used[0]
        else:
            slices_overflow += transponder_slices_usage[subgene[0]]
            # jaki slice ustawić jak sie nie miesci?

    return slices_overflow, bands_usage


def _use_slices(transponder_slices_used, path_slices_utilization, bands):
    """
    Finds empty space for transponder.
    :param transponder_slices_used: how many empty slices in a row needs to be found
    :param path_slices_utilization: slices already used by previous transponders
    :param bands:
    :return: slices used or None if there is not enough space
    """
    empty_space = 0
    for i, bit in enumerate(path_slices_utilization):
        if i + transponder_slices_used > bands[0][1] and i < bands[1][0]:
            empty_space = 0
            continue
        if bit == 0:
            empty_space += 1
            if empty_space == transponder_slices_used:
                return i - transponder_slices_used + 1, i
        else:
            empty_space = 0

    return None


def compare(individual: geneticlib.Individual):
    return individual.values[0]


def random_neighbour(individual: geneticlib.Individual):
    neighbour = copy.deepcopy(individual)
    chromosome = neighbour.chromosome
    genes = chromosome.genes
    chosen_gene_key = random.choice(list(genes.keys()))
    genes[chosen_gene_key] = chromosome._create_gene(chosen_gene_key)
    main_config.tools.calculate_fitness_values([neighbour], [fitness])
    print(f"{neighbour.chromosome} {neighbour.values[0]}")
    return neighbour


def random_neighbour_ksize(individual: geneticlib.Individual, k):
    neighbour = copy.deepcopy(individual)
    chromosome = neighbour.chromosome
    genes = chromosome.genes
    keys = random.sample(list(genes.keys()), k=k)
    for key in keys:
        genes[key] = chromosome._create_gene(key)
    main_config.tools.calculate_fitness_values([neighbour], [fitness])
    print(f"{neighbour.chromosome} {neighbour.values[0]} {k}")
    return neighbour


