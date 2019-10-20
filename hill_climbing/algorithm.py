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
    individual = structure.create_individual()
    config.tools.calculate_fitness_values([individual], [fitness])
    best = hc.run(individual, random_neighbour_function=random_neighbour, compare_function=compare, n=1000)
    pprint(best)


if __name__ == "__main__":
    run_hill()
    # run_vns()
