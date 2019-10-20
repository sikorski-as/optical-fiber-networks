from geneticlib import creator
from geneticlib import toolkit
import random
import copy
import pydoc
import hill_climbinglib as hc
import SimulatedAnnealing as sa


class A:
    def __init__(self, text, number):
        self.text = text
        self.number = random.randint(0, number)


def fitness(chromosome):
    return chromosome.binary.count(1)


def fit2(chromosome):
    return chromosome.count(0)


def fit3(chromosome):
    return chromosome.binary.count(0)


def fit_int(chromosome):
    return chromosome


def main():
    # a = A()
    crt = creator.Creator(Chromosome)
    chromosomes = crt.create(10, 10)
    tools = toolkit.Toolkit()
    tools.set_fitness_weights(weights=(-1, 1))
    population = tools.create_individuals(chromosomes)
    tools.calculate_fitness_values(population, [fit3, fit3])
    pop = population
    population = tools.select_threshold(population, k=5, n=0.2, key=0, replacement=True)
    # pop = population
    # population = tools.select_tournament(population, 10, 5, key=1, replacement=True)
    # couples = tools.create_couples(pop, 2, 4, key=1, replacement=False, select_function=tools.select_linear)
    # try:
    #     creator.create("a")
    #
    # except Exception as e:
    #     print(e.args)
    # for chromosome in chromosomes:
    #     print(chromosome.number, end=" ")
    # for individual in pop:
    #     print("{} -> {}".format(individual.chromosome.binary, individual.values))
    # print()
    for individual in population:
        print(f"{individual.__hash__()} -> {individual.chromosome.binary} {individual.values}")
    print()

    for individual in pop:
        print(f"{individual.__hash__()} -> {individual.chromosome.binary} {individual.values}")

    # for couple in couples:
    #     print("{}".format(couple))


def test():
    doc = pydoc.allmethods(Chromosome)
    print(doc)


class Chromosome:
    def __init__(self, n):
        self.binary = [random.randint(0, 1) for _ in range(0, n)]

    def __str__(self):
        return str(self.binary)


def crossing(parents, crossover_prob):
    chromosome1 = copy.deepcopy(parents[0].chromosome)
    chromosome2 = copy.deepcopy(parents[1].chromosome)
    for i in range(0, len(chromosome1.binary)):
        if random.randint(0, 101) < crossover_prob:
            chromosome1.binary[i], chromosome2.binary[i] = chromosome2.binary[i], chromosome1.binary[i]

    return [toolkit.Individual(chromosome1), toolkit.Individual(chromosome2)]


def mutating(individual):
    for i in range(0, len(individual.chromosome.binary)):
        if random.randint(0, 101) < 20:
            individual.chromosome.binary[i] = (individual.chromosome.binary[i] + 1) % 2


def algos():
    CPB = 50
    MPB = 40
    pop_size = 100
    chromosome_size = 100
    crt = creator.Creator(Chromosome)
    initial_population = crt.create(pop_size, chromosome_size)
    tools = toolkit.Toolkit(crossing_probability=CPB, mutation_probability=MPB)
    tools.set_fitness_weights(weights=(1,))
    individuals = tools.create_individuals(initial_population)
    tools.calculate_fitness_values(individuals, [fitness])
    best = tools.select_best(individuals, 1)
    iteration = 0
    print("{}. {}".format(iteration, best))
    while best.values[0] < chromosome_size:
        couples = tools.create_couples(individuals, 2, int(pop_size / 2))
        offspring = tools.cross(couples, crossing)
        tools.mutate(offspring, mutating)
        tools.calculate_fitness_values(offspring, [fitness])
        individuals = tools.select_tournament(individuals + offspring, pop_size, n=5, replacement=True)
        # individuals = tools.select_best(individuals + offspring, pop_size)
        best = tools.select_best(individuals, 1)
        iteration += 1
        print("{}. {}".format(iteration, best))


def get_neighbour(value):
    neighbour = copy.copy(value)
    place = random.randint(0, len(neighbour) - 1)
    neighbour[place] = (neighbour[place] + 1) % 2
    return neighbour


def hill():
    size = 10
    n = 100
    initial_value = [random.randint(0, 1) for _ in range(size)]
    best = hc.run(initial_value=initial_value, random_neighbour_function=get_neighbour, compare_function=sum, n=n,
                  descending=True)
    print(best)


def annealing():
    size = 10
    n = 100
    initial_value = [random.randint(0, 1) for _ in range(size)]
    best = sa.run(initial_value=initial_value, random_neighbour_function=get_neighbour, compare_function=sum, n=n,
                  descending=True)
    print(best)


if __name__ == "__main__":
    # test()
    # algos()
    hill()
    annealing()
