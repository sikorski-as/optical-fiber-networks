import math
import random


def run(initial_values: iter, random_neighbour_function, compare_function, temperature, temperature_function, n=1,
        descending=True):
    """
    :param initial_values: starting values
    :param random_neighbour_function:  function returning neighbour
    :param compare_function: function to compare elements
    :param n: number of iterations
    :param descending: determines if we are looking for min or max value
    :param temperature:
    :param temperature_function: function which changes temperature in each iteration
    :return: best element
    """
    best_results = initial_values
    number_of_iterations = 0

    while number_of_iterations < n:

        for i, best_result in enumerate(best_results):
            neighbour = random_neighbour_function(best_result)
            best_cost = compare_function(best_result)
            neighbour_cost = compare_function(neighbour)
            p = math.exp(-1 * abs(neighbour_cost - best_cost) / temperature)

            if descending:
                if best_cost > neighbour_cost or random.random() < p:
                    best_results[i] = neighbour
            else:
                if best_cost < neighbour_cost or random.random() < p:
                    best_results[i] = neighbour

        temperature = temperature_function(temperature)
        number_of_iterations += 1

    return min(best_results, key=lambda x: compare_function(x)) if descending \
        else max(best_results, key=lambda x: compare_function(x))
