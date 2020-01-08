def run(initial_values, random_neighbour_function, compare_function, n=1, m=1, K=1, descending=True):
    """

    :param initial_values: initial values
    :param random_neighbour_function: function returning neighbour, needs to take k as argument
    :param compare_function: compare function
    :param n: number of iterations
    :param m: number of iterations before increasing neighbourhood size
    :param K: max neighbourhood size
    :param descending: determines if we are looking for min or max value
    :return: best result
    """
    size = len(initial_values)
    best_results = initial_values
    number_of_iterations = 1
    k = [1 for _ in range(size)]
    iterations_per_k = [0 for _ in range(size)]

    while number_of_iterations < n and k.count(K) < size:
        for i, best_result in enumerate(best_results):
            if k[i] < K:
                neighbour = random_neighbour_function(best_result, k[i])
                best_cost = compare_function(best_result)
                neighbour_cost = compare_function(neighbour)

                if best_cost > neighbour_cost and descending or best_cost < neighbour_cost and not descending:
                    best_results[i] = neighbour
                    k[i] = 1
                    iterations_per_k[i] = 0
                else:
                    iterations_per_k[i] += 1

                if iterations_per_k[i] >= m:
                    k[i] += 1
                    iterations_per_k[i] = 0
        number_of_iterations += 1
    return min(best_results, key=lambda x: compare_function(x)) if descending \
        else max(best_results, key=lambda x: compare_function(x))
