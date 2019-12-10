import random

from genetic.algorithm import crossing, mutating
from hybrid import config
from main_config import tools, SolutionTracer
import main_config
import structure
from structure import random_neighbour, compare
from utils import Timer


def run_genetic_with_hill(random_neighbour_function, compare_function, h_n=1, descending=True, pop_size=config.POP_SIZE, g_n=config.GA_ITERATIONS, new_pop_size=config.NEW_POP_SIZE, MPB=config.MPB,
                CPB=config.CPB):

    file_name = "{}_Hybrid_I{}_GI{}_HI{}".format(main_config.net_name, main_config.intensity, config.GA_ITERATIONS, config.HILL_ITERATIONS)

    with Timer() as timer, main_config.SolutionTracer(file_name) as solution_tracer:
        print("Hybrid - genetic:\n")
        population = [structure.create_individual(main_config.chromosome_type) for _ in range(pop_size)]
        main_config.tools.calculate_fitness_values(population, list_of_funcs=[structure.fitness])

        iteration = 0
        while iteration < g_n:
            iteration += 1
            couples = tools.create_couples(population, 2, int(pop_size / 2))
            offspring = tools.cross(couples, crossover_fun=crossing, CPB=CPB)
            tools.mutate(offspring, mutation_fun=mutating, MPB=MPB)
            tools.calculate_fitness_values(offspring, [structure.fitness])
            new_population = tools.select_best(population + offspring, pop_size - new_pop_size)
            # new_population = tools.select_tournament(population + offspring, pop_size - config.NEW_POP_SIZE, n=5)
            # new_population = tools.select_linear(population + offspring, pop_size - config.NEW_POP_SIZE)
            additional_population = [structure.create_individual(main_config.chromosome_type) for _ in
                                     range(new_pop_size)]
            tools.calculate_fitness_values(additional_population, list_of_funcs=[structure.fitness])
            population = new_population + additional_population
            random.shuffle(population)
            best = tools.select_best(population, 1)

            solution_tracer.update(best, timer.elapsed)
            print('Iteration {} ended\n'.format(iteration) + str(solution_tracer))
            if solution_tracer.repetitions_exceeded:
                break

        best_result = solution_tracer.best
        iteration = 0
        print("Hybrid - hill:\n")
        while iteration < h_n:

            neighbour = random_neighbour_function(best_result)
            best_cost = compare_function(best_result)
            neighbour_cost = compare_function(neighbour)

            if best_cost > neighbour_cost and descending or best_cost < neighbour_cost and not descending:
                best_result = neighbour

            solution_tracer.update(best_result, timer.elapsed)
            print('Iteration {} ended\n'.format(iteration + g_n) + str(solution_tracer))
            iteration += 1
            if solution_tracer.repetitions_exceeded:
                break

        return solution_tracer.best


def main():
    return run_genetic_with_hill(pop_size=config.POP_SIZE, new_pop_size=config.NEW_POP_SIZE, g_n=config.GA_ITERATIONS, random_neighbour_function=random_neighbour, compare_function=compare,
                         h_n=config.HILL_ITERATIONS)


if __name__ == "__main__":
    main()


