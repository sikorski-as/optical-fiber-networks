import copy
import random
import geneticlib
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


def run_genetic(pop_size, net, adapted_predefined_paths, transponders_config, bands, slices_usage,
                transponders_cost):
    crt = geneticlib.Creator(structure.Chromosome)
    initial_population = crt.create(pop_size, net, adapted_predefined_paths, transponders_config, bands,
                                    slices_usage, transponders_cost)
    population = tools.create_individuals(initial_population)
    tools.calculate_fitness_values(population, list_of_funcs=[structure.fitness])
    best = tools.select_best(population, 1)
    print(best)
    iteration = 0
    while iteration < config.GA_ITERATIONS:
        iteration += 1
        couples = tools.create_couples(population, 2, int(pop_size / 2))
        offspring = tools.cross(couples, crossover_fun=crossing, CPB=config.CPB)
        tools.mutate(offspring, mutation_fun=mutating, MPB=config.MPB)
        tools.calculate_fitness_values(offspring, [structure.fitness])
        # new_population = tools.select_best(population + offspring, pop_size - config.NEW_POP_SIZE)
        # new_population = tools.select_tournament(population + offspring, pop_size - config.NEW_POP_SIZE, n=5)
        new_population = tools.select_linear(population + offspring, pop_size - config.NEW_POP_SIZE)
        additional_population = crt.create(config.NEW_POP_SIZE, net, adapted_predefined_paths, transponders_config,
                                           bands, slices_usage, transponders_cost)
        additional_population = tools.create_individuals(additional_population)
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
    adapted_predefined_paths = {key: [value[1] for value in values] for key, values in main_config.predefined_paths.items()}
    # pprint(adapted_predefined_paths)
    main_config.clock.start()
    best_individual = run_genetic(config.POP_SIZE, main_config.net, adapted_predefined_paths, main_config.transponders_config,
                                  main_config.bands, main_config.slices_usage, main_config.transponders_cost)
    main_config.clock.stop()
    file_name = f"{main_config.net_name}_Genetic_I{main_config.intensity}_PS{config.POP_SIZE}_CPB{config.GSPB}_MPB{config.CPPB}_N{config.GA_ITERATIONS}"
    main_config.save_result(best_individual, file_name)
    return best_individual


if __name__ == '__main__':
    main()
