import copy
import operator
import random
import abc
from collections import defaultdict
import bitstring
import geneticlib
import utils


class Slice:

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"{self.value}"


class Chromosome(abc.ABC):

    def __init__(self, net, predefined_paths, transponders_config, bands, transponder_slices_usage, transponders_cost):
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
        self.transponder_slices_usage = transponder_slices_usage
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

    def _use_slices(self, transponder_slices_used, path_slices_utilization, bands):
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

    def _allocate_slices(self):
        slices_usage_map = defaultdict(lambda: bitstring.BitArray(self.bands[1][1]))
        sorted_subgenes = self.sorted_subgenes(sortfun=lambda x: len(x[1]), reverse=True)
        slices_overflow = 0
        edges_used = defaultdict(set)
        bands_usage = defaultdict(int)  # counts edges used in each band

        for subgene in sorted_subgenes:
            path_slices_utilization = None
            for edge in utils.pairwise(subgene[1]):
                edge = tuple(sorted(edge))
                if path_slices_utilization is not None:
                    path_slices_utilization = path_slices_utilization | slices_usage_map[edge]
                else:
                    path_slices_utilization = slices_usage_map[edge]
            slices_used_by_subgene = self.calculate_slices_demand(subgene[0])
            slices_used = self._use_slices(slices_used_by_subgene, path_slices_utilization,
                                           self.bands)
            if slices_used:
                for edge in utils.pairwise(subgene[1]):
                    edge = tuple(sorted(edge))
                    slices_usage_map[edge].set(1, [i for i in range(slices_used[0], slices_used[1] + 1)])
                    band = 0 if slices_used[0] < self.bands[0][1] else 1
                    if edge not in edges_used[band]:
                        bands_usage[band] += 1
                        edges_used[band].add(edge)
                subgene[2].value = slices_used[0]
            else:
                slices_overflow += self.calculate_slices_demand(subgene[0])
                # jaki slice ustawić jak sie nie miesci?

        return slices_overflow, bands_usage

    @abc.abstractmethod
    def calculate_slices_demand(self, transponders):
        return

    @abc.abstractmethod
    def _create_gene(self, key):
        return

    @abc.abstractmethod
    def _choose_slice(self, transponders):
        return

    @abc.abstractmethod
    def get_transponder_usage_cost(self):
        return

    @abc.abstractmethod
    def _check_power(self):
        return

    @abc.abstractmethod
    def mutate_gene(self, gene, predefined_paths):
        return

    def __repr__(self):
        return f"PO:{self.power_overflow} SO:{self.slices_overflow}"

    @abc.abstractmethod
    def sorted_subgenes(self, sortfun, reverse):
        return

    @abc.abstractmethod
    def calculate_band_edge_usage(self):
        return

    @property
    def genes(self):
        return self._structure


class OneSubgeneChromosome(Chromosome):
    "Warning! Not working for big demands!"

    def __init__(self, net, predefined_paths, transponders_config, bands, slices_usage, transponders_cost):
        super().__init__(net, predefined_paths, transponders_config, bands, slices_usage, transponders_cost)

    @property
    def total_transponders_used(self):
        transponders_used = [0 for _ in range(int(len(self.transponders_cost.values()) / 2))]
        for subgene in self.genes.values():
            transponders_used = [a + b for a, b in zip(transponders_used, subgene[0])]
        return transponders_used

    def sorted_subgenes(self, sortfun, reverse=False):
        return sorted(self.genes.values(), key=sortfun, reverse=reverse)

    def _create_gene(self, key):
        demand = self.demands[key]
        transponder_config = random.choice(self.transponders_config[demand])
        return transponder_config, random.choice(self.predefined_paths[key]), Slice(
            self._choose_slice(transponder_config))

    def _choose_slice(self, transponders):
        slices_used = self.calculate_slices_demand(transponders)
        begin, end = random.choice(self.bands)
        return random.randrange(begin, end - slices_used)

    def calculate_slices_demand(self, transponders):
        return sum([amount * self.transponder_slices_usage[transponder_type] for transponder_type, amount in
                    enumerate(transponders)])

    def get_transponder_usage_cost(self):
        cost = 0
        for subgene in self.genes.values():
            band = 0 if subgene[2].value < self.bands[0][1] else 1
            cost += sum([amount * self.transponders_cost[transponder_type, band] for transponder_type, amount in
                         enumerate(subgene[0])])
        return cost

    def _check_power(self):
        power_overflow = 0
        for transponders, path, slice in self.genes.values():
            for transponder_type, amount in enumerate(transponders):
                band = 0 if slice.value <= self.bands[0][1] else 1
                total = 0
                for edge in utils.pairwise(path):
                    total += self.net.edges[edge]['ila'] * (
                            pow(main_config.e, main_config.l[band] * self.net.edges[edge]['distance'] /
                                (1 + self.net.edges[edge]['ila'])) + main_config.V - 2)
                    total += pow(main_config.e,
                                 main_config.l[band] * self.net.edges[edge]['distance'] / (
                                         1 + self.net.edges[edge]['ila'])
                                 ) + main_config.W - 2
                total *= main_config.h * main_config.freq[band] * main_config.OSNR[transponder_type] * \
                         main_config.bandwidth[transponder_type] * amount
                total = round(total, 9)
                if total > main_config.P:
                    power_overflow += total
        self.power_overflow = power_overflow
        return power_overflow

    def mutate_gene(self, subgene, predefined_paths):
        change_path(subgene, predefined_paths)

    def calculate_band_edge_usage(self):
        band_usage = {i: [0, 0] for i in range(int(len(self.transponders_cost.values()) / 2))}
        edge_usage = {edge: [0, 0] for edge in self.net.edges}
        for transponders, path, slice in self.genes.values():
            band = 0 if slice.value <= self.bands[0][1] else 1
            for t_type, amount in enumerate(transponders):
                band_usage[t_type][band] += amount
            for c1, c2 in utils.pairwise(path):
                try:
                    edge_usage[c1, c2][band] += 1
                except KeyError:
                    edge_usage[c2, c1][band] += 1
        return band_usage, edge_usage


class MultipleSubgeneChromosome(Chromosome):

    def __init__(self, net, predefined_paths, transponders_config, bands, slices_usage, transponders_cost):
        super().__init__(net, predefined_paths, transponders_config, bands, slices_usage, transponders_cost)

    @property
    def total_transponders_used(self):
        transponders_used = [0 for _ in range(int(len(self.transponders_cost.values()) / 2))]
        for gene in self.genes.values():
            for subgene in gene:
                transponders_used[subgene[0]] += 1
        return transponders_used

    def sorted_subgenes(self, sortfun, reverse=False):
        flatten_subgenes = [subgene for gene in self.genes.values() for subgene in gene]
        return sorted(flatten_subgenes, key=sortfun, reverse=reverse)

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
        slices_used = self.transponder_slices_usage[transponder_type]
        begin, end = random.choice(self.bands)
        return random.randrange(begin, end - slices_used)

    def calculate_slices_demand(self, transponder_type):
        return self.transponder_slices_usage[transponder_type]

    def get_transponder_usage_cost(self):
        total_cost = 0
        for gene in self.genes.values():
            for subgene in gene:
                band = 0 if subgene[2].value < self.bands[0][1] else 1
                total_cost += self.transponders_cost[subgene[0], band]
        return total_cost

    def _check_power(self):
        power_overflow = 0
        for subgenes in self.genes.values():
            for transponder_type, path, slice in subgenes:
                band = 0 if slice.value <= self.bands[0][1] else 1
                total = 0
                for edge in utils.pairwise(path):
                    total += self.net.edges[edge]['ila'] * (
                            pow(main_config.e, main_config.l[band] * self.net.edges[edge]['distance'] /
                                (1 + self.net.edges[edge]['ila'])) + main_config.V - 2)
                    total += pow(main_config.e,
                                 main_config.l[band] * self.net.edges[edge]['distance'] / (
                                         1 + self.net.edges[edge]['ila'])
                                 ) + main_config.W - 2
                total *= main_config.h * main_config.freq[band] * main_config.OSNR[transponder_type] * \
                         main_config.bandwidth[transponder_type]
                total = round(total, 9)
                if total > main_config.P:
                    power_overflow += total
        self.power_overflow = power_overflow
        return power_overflow

    def mutate_gene(self, gene, predefined_paths):
        for i, subgene in enumerate(gene):
            gene[i] = change_path(subgene, predefined_paths)

    def calculate_band_edge_usage(self):
        band_usage = {i: [0, 0] for i in range(int(len(self.transponders_cost.values()) / 2))}
        edge_usage = {edge: [0, 0] for edge in self.net.edges}
        for t_type, path, slice in self.sorted_subgenes(lambda x: x[2].value):
            band = 0 if slice.value <= self.bands[0][1] else 1
            band_usage[t_type][band] += 1
            for c1, c2 in utils.pairwise(path):
                try:
                    edge_usage[c1, c2][band] += 1
                except KeyError:
                    edge_usage[c2, c1][band] += 1
        return band_usage, edge_usage


def create_individual(ChromosomeType):
    """
    Creates individual without fitness value.
    :return: Individual
    """
    adapted_predefined_paths = {key: [value[1] for value in values] for key, values in
                                main_config.predefined_paths.items()}
    individual = geneticlib.Individual(
        ChromosomeType(main_config.net, adapted_predefined_paths, main_config.transponders_config, main_config.bands,
                       main_config.slices_usage, main_config.transponders_cost))
    return individual


def change_path(gene, predefined_paths):
    new_gene = gene[0], random.choice(predefined_paths), gene[2]
    return new_gene


def fitness(chromosome: Chromosome):
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
    total_cost = 0

    # version 1

    slices_overflow, bands_usage = chromosome._allocate_slices()
    chromosome.slices_overflow = slices_overflow
    total_cost += chromosome.get_transponder_usage_cost()

    power_overflow = chromosome._check_power()
    # print(slices_overflow)
    # print(total_cost)
    amplifiers_cost = sum([main_config.b_cost[key] * value for key, value in bands_usage.items()])
    return total_cost * pow(2.72, power_overflow * 100) + pow(slices_overflow, 2) + amplifiers_cost


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


import main_config
