import copy
import random
from collections import defaultdict
import bitstring
import geneticlib
import sndlib
import utils
from genetic import structure, config
from main_config import e, l, W, OSNR, freq, h, bandwidth, P, V, tools, b_cost
import main_config


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
                gene[i] = change_path(subgene, chromosome.predefined_paths[key])
    return chromosome


def change_path(gene, predefined_paths):
    new_gene = gene[0], random.choice(predefined_paths), gene[2]
    return new_gene


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
    amplifiers_cost = sum([b_cost[key] * value for key, value in bands_usage.items()])
    return total_cost * pow(2.72, power_overflow*1000) + pow(slices_overflow, 2) + amplifiers_cost


def _check_power(chromosome: structure.Chromosome):
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


def run_genetic(pop_size, net, adapted_predefined_paths, transponders_config, bands, slices_usage,
                transponders_cost):
    crt = geneticlib.Creator(structure.Chromosome)
    initial_population = crt.create(pop_size, net, adapted_predefined_paths, transponders_config, bands,
                                    slices_usage, transponders_cost)
    population = tools.create_individuals(initial_population)
    tools.calculate_fitness_values(population, list_of_funcs=[fitness])
    best = tools.select_best(population, 1)
    print(best)
    iteration = 0
    while iteration < config.GA_ITERATIONS:
        iteration += 1
        couples = tools.create_couples(population, 2, int(pop_size / 2))
        offspring = tools.cross(couples, crossover_fun=crossing, CPB=config.CPB)
        tools.mutate(offspring, mutation_fun=mutating, MPB=config.MPB)
        tools.calculate_fitness_values(offspring, [fitness])
        # new_population = tools.select_best(population + offspring, pop_size - config.NEW_POP_SIZE)
        # new_population = tools.select_tournament(population + offspring, pop_size - config.NEW_POP_SIZE, n=5)
        new_population = tools.select_linear(population + offspring, pop_size - config.NEW_POP_SIZE)
        additional_population = crt.create(config.NEW_POP_SIZE, net, adapted_predefined_paths, transponders_config,
                                           bands, slices_usage, transponders_cost)
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


def main():
    adapted_predefined_paths = {key: [value[1] for value in values] for key, values in main_config.predefined_paths.items()}
    # pprint(adapted_predefined_paths)
    main_config.clock.start()
    best_individual = run_genetic(config.POP_SIZE, main_config.net, adapted_predefined_paths, main_config.transponders_config,
                                  main_config.bands, main_config.slices_usage, main_config.transponders_cost)
    main_config.clock.stop()
    file_name = f"{main_config.net_name}_Genetic_I{main_config.intensity}_PS{config.POP_SIZE}_CPB{config.GSPB}_MPB{config.CPPB}_N{config.GA_ITERATIONS}"
    main_config.save_result(best_individual, file_name)
    return best_individual


if __name__ == '__main__':
    main()
