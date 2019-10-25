import copy
import random
from pprint import pprint

import hill_climbinglib as hc
import geneticlib
from genetic import config, structure, fitness
from hill_climbinglib import vns


def compare(individual: geneticlib.Individual):
    return individual.values[0]


def random_neighbour(individual: geneticlib.Individual):
    neighbour = copy.deepcopy(individual)
    chromosome = neighbour.chromosome
    genes = chromosome.genes
    chosen_gene_key = random.choice(list(genes.keys()))
    genes[chosen_gene_key] = chromosome._create_gene(chosen_gene_key)
    config.tools.calculate_fitness_values([neighbour], [fitness])
    print(f"{neighbour.chromosome} {neighbour.values[0]}")
    return neighbour


def random_neighbour_ksize(individual: geneticlib.Individual, k):
    neighbour = copy.deepcopy(individual)
    chromosome = neighbour.chromosome
    genes = chromosome.genes
    keys = random.sample(list(genes.keys()), k=k)
    for key in keys:
        genes[key] = chromosome._create_gene(key)
    config.tools.calculate_fitness_values([neighbour], [fitness])
    print(f"{neighbour.chromosome} {neighbour.values[0]} {k}")
    return neighbour


def run_vns():
    individual = structure.create_individual()
    config.tools.calculate_fitness_values([individual], [fitness])
    best = vns.run(individual, random_neighbour_function=random_neighbour_ksize, compare_function=compare, n=1000,
                   m=100, K=10)
    pprint(best)


def run_hill():
    n = config.HILL_ITERATIONS
    size = 10
    individuals = [structure.create_individual() for _ in range(size)]
    config.tools.calculate_fitness_values(individuals, [fitness])
    config.clock.start()
    best = hc.run(individuals, random_neighbour_function=random_neighbour, compare_function=compare, n=n)
    config.clock.stop()
    file_name = f"{config.net_name}_Hill_I{config.intensity}_SIZE{size}_N{n}"
    config.save_result(best, file_name)
    pprint(best)


if __name__ == "__main__":
    run_hill()
    # run_vns()
