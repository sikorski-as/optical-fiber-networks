import copy
import random
from genetic import config
import structure
import main_config
from main_config import tools


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
        for i, subgene in enumerate(gene):
            if random.randrange(0, 100) < config.CPPB:
                gene[i] = structure.change_path(subgene, chromosome.predefined_paths[key])
    return chromosome


def run_genetic(pop_size=config.POP_SIZE, n=config.GA_ITERATIONS, new_pop_size=config.NEW_POP_SIZE, MPB=config.MPB,
                CPB=config.CPB):
    population = [structure.create_individual(main_config.chromosome_type) for _ in range(pop_size)]
    tools.calculate_fitness_values(population, list_of_funcs=[structure.fitness])
    best = tools.select_best(population, 1)
    print(best)
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
        additional_population = [structure.create_individual(main_config.chromosome_type) for _ in range(new_pop_size)]
        tools.calculate_fitness_values(additional_population, list_of_funcs=[structure.fitness])
        population = new_population + additional_population
        random.shuffle(population)
        best = tools.select_best(population, 1)
        # pprint(population)
        print(f"{iteration}{best}")

    best_population = sorted(population, key=lambda x: x.values[0])
    # pprint(best_population)
    return best_population[0]


def main():
    main_config.clock.start()
    best_individual = run_genetic()
    main_config.clock.stop()
    file_name = f"{main_config.net_name}_Genetic_I{main_config.intensity}_PS{config.POP_SIZE}_CPB{config.GSPB}_MPB{config.CPPB}_N{config.GA_ITERATIONS}"
    main_config.save_result(best_individual, file_name)
    return best_individual


if __name__ == '__main__':
    main()
