import itertools

from genetic.structure import Chromosome, create_individual
from genetic import config, structure, fitness
from hill_climbing.algorithm import random_neighbour, random_neighbour_ksize
from random import randrange


def bee_colony(nscouts=64, m_best=10, e_best=2, n1=20, n2=3, flower_patch_size=5, iterations=100):
    tools = config.tools
    scouts = [create_individual() for _ in range(nscouts)]
    tools.calculate_fitness_values(scouts, list_of_funcs=[fitness])

    for i in range(1, iterations + 1):
        m_bees = tools.select_best(scouts, m_best)
        elite_bees = m_bees[:e_best]
        not_elite_bees = m_bees[e_best:]

        all_bees = []
        for elite_bee in elite_bees:
            for _ in range(n1):
                all_bees.append(random_neighbour_ksize(elite_bee, k=randrange(flower_patch_size)))
        for not_elite_bee in not_elite_bees:
            for _ in range(n2):
                all_bees.append(random_neighbour_ksize(not_elite_bee, k=randrange(flower_patch_size)))

        tools.calculate_fitness_values(all_bees, list_of_funcs=[fitness])
        all_bees.extend(m_bees)
        scouts = tools.select_best(all_bees, m_best)
        print(f'After iteration {i} top 3: {" ".join(str(s.values[0]) for s in scouts[:3])}')
        new_scouts = [create_individual() for _ in range(nscouts - m_best)]
        tools.calculate_fitness_values(new_scouts, list_of_funcs=[fitness])
        scouts.extend(new_scouts)

    print(scouts)


def run(initial_value, random_neighbour_function, compare_function, n=1, descending=True):
    """
    :param initial_value: starting value
    :param random_neighbour_function: function returning neighbour
    :param compare_function: function to compare elements
    :param n: number of iterations
    :param descending: determines if we are looking for min or max value
    :return: best element
    """

    best = initial_value
    number_of_iterations = 1

    while number_of_iterations < n:
        neighbour = random_neighbour_function(best)

        if compare_function(best) > compare_function(neighbour) and descending \
                or compare_function(best) < compare_function(neighbour) and not descending:
            best = neighbour

        number_of_iterations += 1
    return best


if __name__ == '__main__':
    bee_colony()
