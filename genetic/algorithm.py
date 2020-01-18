import copy
import random
from genetic import config
import structure
import main_config
from main_config import tools
from utils import Timer


def crossing(individual1, individual2):
    child1 = copy.deepcopy(individual1.chromosome)
    child2 = copy.deepcopy(individual2.chromosome)
    for key in child1.genes:
        if random.randrange(0, 100) < config.GSPB:
            child1.genes[key], child2.genes[key] = child2.genes[key], child1.genes[key]

    return [child1, child2]


def mutating(individual):
    chromosome = individual.chromosome
    for key, gene in chromosome.genes.items():
        if random.randrange(0, 100) < config.CPPB:
            chromosome.mutate_gene(key)
    return chromosome


def run_genetic(pop_size=config.POP_SIZE, n=config.GA_ITERATIONS, new_pop_size=config.NEW_POP_SIZE, MPB=config.MPB,
                CPB=config.CPB):
    file_name = "{}_Genetic_I{}_PS{}_CPB{}_MPB{}_N{}".format(main_config.net_name, main_config.intensity, config.POP_SIZE, config.GSPB, config.CPPB, config.GA_ITERATIONS)
    print("Start genetic:")
    with Timer() as timer, main_config.SolutionTracer(file_name, max_repetitions=main_config.max_repetitions) as solution_tracer:
        population = [structure.create_individual(main_config.chromosome_type) for _ in range(pop_size)]
        tools.calculate_fitness_values(population, list_of_funcs=[structure.fitness])

        iteration = 0
        while iteration < n:
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

        return solution_tracer.best


def main():
    return run_genetic()


if __name__ == '__main__':
    main()
