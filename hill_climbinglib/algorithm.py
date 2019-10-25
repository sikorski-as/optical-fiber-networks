def run(initial_values: iter, random_neighbour_function, compare_function, n=1, descending=True):
    """
    :param initial_values: starting values
    :param random_neighbour_function: function returning neighbour
    :param compare_function: function to compare elements
    :param n: number of iterations
    :param descending: determines if we are looking for min or max value
    :return: best element
    """

    best_results = initial_values
    number_of_iterations = 0

    while number_of_iterations < n:
        for i, best_result in enumerate(best_results):
            print(number_of_iterations)
            neighbour = random_neighbour_function(best_result)
            best_cost = compare_function(best_result)
            neighbour_cost = compare_function(neighbour)

            if best_cost > neighbour_cost and descending or best_cost < neighbour_cost and not descending:
                best_results[i] = neighbour

        number_of_iterations += 1

    return min(best_results, key=lambda x: compare_function(x)) if descending \
        else max(best_results, key=lambda x: compare_function(x))
