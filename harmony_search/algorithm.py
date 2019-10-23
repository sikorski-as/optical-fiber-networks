import itertools
import random

from sortedcontainers import sortedlist

from genetic import config, fitness
from genetic.algorithm import change_path, save_result
from genetic.structure import create_individual


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
    harmonies = [create_individual() for _ in range(memory_size)]
    config.tools.calculate_fitness_values(harmonies, list_of_funcs=[fitness])
    harmony_memory = sortedlist.SortedList(harmonies, key=lambda x: x.values[0])
    print(harmony_memory)

    iteration = itertools.count()
    while next(iteration) < n:
        new_harmony = create_individual()
        new_harmony.chromosome.clear_structure()
        harmony_structure = {}
        for key in config.demands:
            if random.random() < accept_rate:
                harmony_structure[key] = choose_gene_from_hm(harmony_memory, key)
                if random.random() < pa_rate:
                    mutate_gene(harmony_structure[key], new_harmony.chromosome.predefined_paths[key])
            else:
                harmony_structure[key] = new_harmony.chromosome._create_gene(key)
        new_harmony.chromosome.set_structure(harmony_structure)
        config.tools.calculate_fitness_values([new_harmony], list_of_funcs=[fitness])
        print(new_harmony)
        if harmony_memory[-1].values[0] > new_harmony.values[0]:
            harmony_memory.pop()
            harmony_memory.add(new_harmony)
    print(harmony_memory[0])
    return harmony_memory[0]


def choose_gene_from_hm(hm: sortedlist.SortedList, key):
    genes = [harmony.chromosome.genes[key] for harmony in hm]
    return random.choice(genes)


def mutate_gene(gene, predefined_paths):
    for i, subgene in enumerate(gene):
        gene[i] = change_path(subgene, predefined_paths)


if __name__ == "__main__":
    config.clock.start()
    best_result = run(accept_rate=0.9, pa_rate=0.1, memory_size=30, n=2000)
    config.clock.stop()
    save_result(best_result.chromosome)
    print(config.clock.time_elapsed())
