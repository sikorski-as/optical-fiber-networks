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
