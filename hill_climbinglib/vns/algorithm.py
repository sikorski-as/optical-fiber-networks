def run(initial_value, random_neighbour_function, compare_function, n=1, m=1, K=1, descending=True):
    """

    :param initial_value:
    :param random_neighbour_function: function returning neighbour, needs to take k as argument
    :param compare_function:
    :param n: number of iterations
    :param m: number of iterations before increasing neighbourhood size
    :param K: max neighbourhood size
    :param descending: determines if we are looking for min or max value
    :return: best result
    """
    best = initial_value
    number_of_iterations = 1
    k = 1
    iterations_per_k = 0

    while number_of_iterations < n and k < K:
        neighbour = random_neighbour_function(best, k)

        if compare_function(best) > compare_function(neighbour) and descending \
                or compare_function(best) < compare_function(neighbour) and not descending:
            best = neighbour
            k = 1
            iterations_per_k = 0
        else:
            iterations_per_k += 1

        if iterations_per_k >= m:
            k += 1
            iterations_per_k = 0

        number_of_iterations += 1
    return best
