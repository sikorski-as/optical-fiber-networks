import copy
import math
import random

import sortedcontainers

from geneticlib import Creator, Toolkit


class Chromosome:
    def __init__(self, demand, transponders, configuration=None):
        self.transponders = transponders
        self.demand = demand
        if configuration is None:
            self.configuration = [random.randint(0, math.ceil(demand / transponder.transfer)) for transponder in transponders]
        else:
            self.configuration = configuration

    @property
    def total_capacity(self):
        return sum([self.configuration[i] * self.transponders[i].transfer for i in range(len(self.transponders))])

    def __str__(self):
        return f"{self.configuration}"

    def __eq__(self, other):
        return self.configuration == other.configuration

    def __hash__(self):
        return hash(tuple(self.configuration))


def fitness(chromosome: Chromosome):
    if chromosome.total_capacity < chromosome.demand:
        return math.inf
    else:
        ntransponders = len(chromosome.transponders)
        return sum(chromosome.configuration[i] * chromosome.transponders[i].width for i in range(ntransponders))


def mutating(individual):
    chromosome = individual.chromosome
    if chromosome.total_capacity < chromosome.demand:
        missing_value = chromosome.demand - chromosome.total_capacity
        while missing_value > 0:
            for i, transponder in enumerate(chromosome.transponders):
                if transponder.transfer > missing_value:
                    chromosome.configuration[i] += 1
                    missing_value -= transponder[0]
                elif i == len(chromosome.transponders) - 1:
                    chromosome.configuration[i] += 1
                    missing_value -= transponder[0]
    return chromosome


def crossing(parent1, parent2):
    CPB = 20
    chromosome1 = copy.deepcopy(parent1.chromosome)
    chromosome2 = copy.deepcopy(parent2.chromosome)
    config_len = len(chromosome1.configuration)
    for i in range(config_len):
        if random.randint(0, 101) < CPB:
            chromosome1.configuration[i], chromosome2.configuration[i] = chromosome2.configuration[i], \
                                                                         chromosome1.configuration[i]

    return [chromosome1, chromosome2]


def create_config(demand, transponders, n, initial=None):
    best_results = sortedcontainers.SortedSet(key=lambda el: fitness(el))
    if initial is not None:
        best_results.update(Chromosome(demand, transponders, conf) for conf in initial)
    CPB = 20
    MPB = 100
    pop_size = 40
    ITERATIONS = 150
    new_pop_size = 10
    crt = Creator(Chromosome)
    initial_population = crt.create(pop_size, demand, transponders)
    tools = Toolkit(crossing_probability=CPB, mutation_probability=MPB)
    tools.set_fitness_weights(weights=(-1,))
    individuals = tools.create_individuals(initial_population)
    tools.calculate_fitness_values(individuals, [fitness])
    best = tools.select_best(individuals, pop_size)
    for individual in best:
        best_results.add(individual.chromosome)
        if len(best_results) == n:
            break
    iteration = 0
    while iteration < ITERATIONS:
        couples = tools.create_couples(individuals, 2, int(pop_size / 2))
        offspring = tools.cross(couples, crossing)
        tools.mutate(offspring, mutating)
        tools.calculate_fitness_values(offspring, [fitness])
        individuals = tools.select_tournament(individuals + offspring, pop_size - new_pop_size, n=5, replacement=True)
        new_population = crt.create(new_pop_size, demand, transponders)
        new_individuals = tools.create_individuals(new_population)
        tools.calculate_fitness_values(new_individuals, [fitness])
        individuals += new_individuals
        best = individuals[0]
        if best.chromosome not in best_results:
            if len(best_results) < n:
                best_results.add(best.chromosome)
            elif best.values[0] < fitness(best_results[n - 1]):
                best_results.pop()
                best_results.add(best.chromosome)
        iteration += 1
    configuration = []
    for result in best_results:
        # print(f"{result} {fitness(result)}")
        configuration.append(result.configuration)
    print('done with demand =', demand)

    return configuration
