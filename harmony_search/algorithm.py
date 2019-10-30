import itertools
import random
from sortedcontainers import sortedlist
import main_config
from harmony_search import config
import structure


def run(accept_rate, pa_rate, memory_size, n):
    """
    rpa best (0.1-0.5)
    r_accept (0.7-0.95)
    :param accept_rate:
    :param pa_rate:
    :param memory_size:
    :param n: number of iterations
    :return: best harmony
    """
    harmonies = [structure.create_individual() for _ in range(memory_size)]
    main_config.tools.calculate_fitness_values(harmonies, list_of_funcs=[structure.fitness])
    harmony_memory = sortedlist.SortedList(harmonies, key=lambda x: x.values[0])

    iteration = itertools.count()
    while next(iteration) < n:
        print(iteration)
        new_harmony = structure.create_individual()
        new_harmony.chromosome.clear_structure()
        harmony_structure = {}
        for key in main_config.net.demands:
            if random.random() < accept_rate:
                harmony_structure[key] = choose_gene_from_hm(harmony_memory, key)
                if random.random() < pa_rate:
                    structure.mutate_gene(harmony_structure[key], new_harmony.chromosome.predefined_paths[key])
            else:
                harmony_structure[key] = new_harmony.chromosome._create_gene(key)
        new_harmony.chromosome.set_structure(harmony_structure)
        main_config.tools.calculate_fitness_values([new_harmony], list_of_funcs=[structure.fitness])
        print(new_harmony)
        if harmony_memory[-1].values[0] > new_harmony.values[0]:
            harmony_memory.pop()
            harmony_memory.add(new_harmony)
    print(harmony_memory[0])
    return harmony_memory[0]


def choose_gene_from_hm(hm: sortedlist.SortedList, key):
    genes = [harmony.chromosome.genes[key] for harmony in hm]
    return random.choice(genes)


def main():
    main_config.clock.start()
    best_result = run(accept_rate=config.HS_ACCEPT_RATE, pa_rate=config.HS_PA_RATE, memory_size=config.HS_MEMORY_SIZE,
                      n=config.HS_ITERATIONS)
    file_name = f"{main_config.net_name}_Harmony_I{main_config.intensity}_AR{config.HS_ACCEPT_RATE}_PR{config.HS_PA_RATE}_MS{config.HS_MEMORY_SIZE}_N{config.HS_ITERATIONS}"
    main_config.clock.stop()
    main_config.save_result(best_result, file_name)
    print(best_result)


if __name__ == "__main__":
    main()
