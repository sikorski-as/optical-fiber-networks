import copy
import random
from collections import defaultdict
from pprint import pprint, pformat

import bitstring

import geneticlib
import hill_climbing as hc
import sndlib
import utils
import vns as vns
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


def crossing(individual1, individual2):
    child1 = copy.deepcopy(individual1.chromosome)
    child2 = copy.deepcopy(individual2.chromosome)
    for key in child1.genes:
        if random.randrange(0, 100) < config.GSPB:
            child1.genes[key], child2.genes[key] = child2.genes[key], child1.genes[key]

    return [child1, child2]


def mutating(individual):
    chromosome = individual.chromosome
    for key, gene in chromosome.genes.items():
        for i, subgene in enumerate(gene):
            if random.randrange(0, 100) < config.CPPB:
                gene[i] = _change_path(subgene, chromosome.predefined_paths[key])
    return chromosome


def _change_path(gene, predefined_paths):
    new_gene = gene[0], random.choice(predefined_paths), gene[2]
    return new_gene


def fitness(chromosome):
    cost = chromosome.transponders_cost
    total_cost = 0
    for gene in chromosome.genes.values():
        for subgene in gene:
            band = 0 if subgene[2].value <= chromosome.bands[1][0] else 1
            total_cost += cost[subgene[0], band]

    # version 1
    slices_overflow = _check_if_fits(chromosome.genes.values(), chromosome.bands, chromosome.slices_usage)
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

    power_overflow = _check_power(chromosome)

    # print(slices_overflow)
    # print(total_cost)
    return total_cost + pow(slices_overflow, 2)


def _check_power(chromosome: Chromosome):
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
    node_reinforcement = sndlib.calculate_reinforcement_for_each_node(chromosome.net)
    P = 0.001

    power_overflow = 0
    for gene in chromosome.genes.values():
        for transponder_type, path, slice in gene:
            band = 0 if slice.value <= chromosome.bands[0][1] else 1
            total = 0
            for edge in utils.pairwise(path):
                total += chromosome.net.edges[edge]['ila'] * (pow(e, l[band] * chromosome.net.edges[edge]['distance'] /
                                                                  (1 + chromosome.net.edges[edge]['ila'])) + V - 2)
                total += pow(e,
                             l[band] * chromosome.net.edges[edge]['distance'] / (1 + chromosome.net.edges[edge]['ila'])
                             ) + W - 2
            total *= h * freq[band] * OSNR[transponder_type] * bandwidth[transponder_type]
            # print(total)
            if total > P:
                power_overflow += total
    chromosome.power_overflow = power_overflow
    return power_overflow


def _check_if_fits(genes, bands, transponder_slices_usage):
    slices_usage = defaultdict(lambda: bitstring.BitArray(bands[1][1]))
    flatten_genes = [subgene for gene in genes for subgene in gene]
    sorted_genes = sorted(flatten_genes, key=lambda x: len(x[1]), reverse=True)
    slices_overflow = 0

    for gene in sorted_genes:
        path_slices_utilization = None
        for edge in utils.pairwise(gene[1]):
            edge = tuple(sorted(edge))
            if path_slices_utilization is not None:
                path_slices_utilization = path_slices_utilization | slices_usage[edge]
            else:
                path_slices_utilization = slices_usage[edge]
        slices_used = _use_slices(transponder_slices_usage[gene[0]], path_slices_utilization, bands)
        if slices_used:
            for edge in utils.pairwise(gene[1]):
                edge = tuple(sorted(edge))
                slices_usage[edge].set(1, [i for i in range(slices_used[0], slices_used[1] + 1)])
                #
            gene[2].value = slices_used[0]
        else:
            slices_overflow += transponder_slices_usage[gene[0]]
            # jaki slice ustawić jak sie nie miesci?

    return slices_overflow


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


def main():
    adapted_predefined_paths = {key: [value[1] for value in values] for key, values in config.predefined_paths.items()}
    # pprint(adapted_predefined_paths)
    best_individual = run_genetic(config.POP_SIZE, config.net, adapted_predefined_paths, config.transponders_config,
                                  config.demands, config.bands,
                                  config.slices_usage, config.transponders_cost)

    best_result = hc.run(best_individual, random_neighbour_function=random_neighbour, compare_function=compare,
                         n=config.HILL_ITERATIONS)
    save_result(best_result.chromosome)


def compare(individual: geneticlib.Individual):
    return individual.values[0]


def random_neighbour(individual: geneticlib.Individual):
    neighbour = copy.deepcopy(individual)
    chromosome = neighbour.chromosome
    genes = chromosome.genes
    chosen_gene_key = random.choice(list(genes.keys()))
    genes[chosen_gene_key] = chromosome._create_gene(chosen_gene_key)
    tools = geneticlib.Toolkit(crossing_probability=config.CPB, mutation_probability=config.MPB)
    tools.set_fitness_weights(weights=(-1,))
    tools.calculate_fitness_values([neighbour], [fitness])
    print(f"{neighbour.chromosome} {neighbour.values[0]}")
    return neighbour


def random_neighbour_ksize(individual: geneticlib.Individual, k):
    neighbour = copy.deepcopy(individual)
    chromosome = neighbour.chromosome
    genes = chromosome.genes
    keys = random.sample(list(genes.keys()), k=k)
    for key in keys:
        genes[key] = chromosome._create_gene(key)
    tools = geneticlib.Toolkit(crossing_probability=config.CPB, mutation_probability=config.MPB)
    tools.set_fitness_weights(weights=(-1,))
    tools.calculate_fitness_values([neighbour], [fitness])
    print(f"{neighbour.chromosome} {neighbour.values[0]} {k}")
    return neighbour


def create_individual():
    adapted_predefined_paths = {key: [value[1] for value in values] for key, values in config.predefined_paths.items()}
    individual = geneticlib.Individual(
        Chromosome(config.net, adapted_predefined_paths, config.transponders_config, config.demands, config.bands,
                   config.slices_usage, config.transponders_cost))
    tools = geneticlib.Toolkit(crossing_probability=config.CPB, mutation_probability=config.MPB)
    tools.set_fitness_weights(weights=(-1,))
    tools.calculate_fitness_values([individual], [fitness])
    return individual


def run_hill():
    individual = create_individual()
    best = hc.run(individual, random_neighbour_function=random_neighbour, compare_function=compare, n=1000)
    pprint(best)


def run_vns():
    individual = create_individual()
    best = vns.run(individual, random_neighbour_function=random_neighbour_ksize, compare_function=compare, n=1000,
                   m=100, K=10)
    pprint(best)


def run_genetic(pop_size, net, adapted_predefined_paths, transponders_config, demands, bands, slices_usage,
                transponders_cost):
    crt = geneticlib.Creator(Chromosome)
    initial_population = crt.create(pop_size, net, adapted_predefined_paths, transponders_config, demands, bands,
                                    slices_usage, transponders_cost)
    tools = geneticlib.Toolkit(crossing_probability=config.CPB, mutation_probability=config.MPB)
    tools.set_fitness_weights(weights=(-1,))
    population = tools.create_individuals(initial_population)
    tools.calculate_fitness_values(population, list_of_funcs=[fitness])
    best = tools.select_best(population, 1)
    print(best)
    iteration = 0
    while iteration < config.GA_ITERATIONS:
        iteration += 1
        couples = tools.create_couples(population, 2, int(pop_size / 2))
        offspring = tools.cross(couples, crossover_fun=crossing)
        tools.mutate(offspring, mutation_fun=mutating)
        tools.calculate_fitness_values(offspring, [fitness])
        # new_population = tools.select_best(population + offspring, pop_size - config.NEW_POP_SIZE)
        # new_population = tools.select_tournament(population + offspring, pop_size - config.NEW_POP_SIZE, n=5)
        new_population = tools.select_linear(population + offspring, pop_size - config.NEW_POP_SIZE)
        additional_population = crt.create(config.NEW_POP_SIZE, net, adapted_predefined_paths, transponders_config,
                                           demands, bands,
                                           slices_usage, transponders_cost)
        additional_population = tools.create_individuals(additional_population)
        tools.calculate_fitness_values(additional_population, list_of_funcs=[fitness])
        population = new_population + additional_population
        random.shuffle(population)
        best = tools.select_best(population, 1)
        # pprint(population)
        print(f"{iteration}{best}")

    best_population = sorted(population, key=lambda x: x.values[0])
    # pprint(best_population)
    return best_population[0]


def save_result(best_chromosome: Chromosome):
    """
    demandy, użyte transpondery dla danego połączenia, stan sieci(slice`y)?
    suma użytych transponderów każdego typu
    :param best_chromosome:
    :return:
    """
    file_name = f"{config.net_name}_I{config.intensity}_PS{config.POP_SIZE}_GI{config.GA_ITERATIONS}_HI{config.HILL_ITERATIONS}"
    ndemands = len(best_chromosome.demands.values())
    structure = pformat(best_chromosome.genes, indent=1)
    total_transonders_used = [0 for _ in range(int(len(best_chromosome.transponders_cost.values()) / 2))]
    genes = best_chromosome.genes.values()
    for gene in genes:
        for subgene in gene:
            total_transonders_used[subgene[0]] += 1

    flatten_genes = [subgene for gene in genes for subgene in gene]
    sorted_genes = [gene for gene in sorted(flatten_genes, key=lambda x: x[2].value)]

    result = f"Number of demands: {ndemands}\n Cost: {fitness(best_chromosome)}\n Structure: {structure}\n " \
        f"Transponders used:{total_transonders_used}\n" \
        f"Sorted paths:{sorted_genes},\n Power overflow: {best_chromosome.power_overflow} \n" \
        f" Slices overflow: {best_chromosome.slices_overflow}"
    print(result)

    with open(f'results/{file_name}', mode='w') as file:
        file.write(result)


if __name__ == '__main__':
    main()
    # run_hill()
    # run_vns()
