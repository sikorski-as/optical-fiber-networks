from main_config import SolutionTracer
import main_config
from utils import Timer


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
    iteration = 0

    file_name = "{}_Hill_I{}_SIZE{}_N{}".format(main_config.net_name, main_config.intensity, len(best_results), n)
    with Timer() as timer, SolutionTracer(file_name) as solution_tracer:

        while iteration < n:
            for i, best_result in enumerate(best_results):
                # print(number_of_iterations)
                neighbour = random_neighbour_function(best_result)
                best_cost = compare_function(best_result)
                neighbour_cost = compare_function(neighbour)

                if best_cost > neighbour_cost and descending or best_cost < neighbour_cost and not descending:
                    best_results[i] = neighbour

            solution_tracer.update(min(best_results), timer.elapsed)
            print('Iteration {} ended\n'.format(iteration) + str(solution_tracer))
            iteration += 1
            if solution_tracer.repetitions_exceeded:
                break

    return min(best_results, key=lambda x: compare_function(x)) if descending \
        else max(best_results, key=lambda x: compare_function(x))
