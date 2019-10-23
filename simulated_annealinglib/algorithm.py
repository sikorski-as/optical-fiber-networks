import math
import random


def run(initial_value, random_neighbour_function, compare_function, temperature, temperature_function, n=1, descending=True):
    """
    :param initial_value: starting value
    :param random_neighbour_function:  function returning neighbour
    :param compare_function: function to compare elements
    :param n: number of iterations
    :param descending: determines if we are looking for min or max value
    :param temperature:
    :param temperature_function: function which changes temperature in each iteration
    :return: best element
    """
    best = initial_value
    number_of_iterations = 1

    while number_of_iterations < n:
        neighbour = random_neighbour_function(best)
        best_cost = compare_function(best)
        neighbour_cost = compare_function(neighbour)
        p = math.exp(-1 * abs(neighbour_cost - best_cost) / temperature)

        if descending:
            if best_cost > neighbour_cost or random.random() < p:
                best = neighbour
        else:
            if best_cost < neighbour_cost or random.random() < p:
                best = neighbour
        temperature = temperature_function(temperature)
        number_of_iterations += 1

    return best
