import itertools
import random
from sortedcontainers import sortedlist
import main_config
from harmony_search import config
import structure
from utils import Timer


def run(accept_rate, pa_rate, memory_size, n, separate_genes=True):
    """
    rpa best (0.1-0.5)
    r_accept (0.7-0.95)
    :param accept_rate:
    :param pa_rate:
    :param memory_size:
    :param n: number of iterations
    :param separate_genes: determining if random choosing each gene or whole structure
    :return: best harmony
    """
    file_name = "{}_Harmony_I{}_AR{}_PR{}_MS{}_N{}".format(main_config.net_name, main_config.intensity, config.HS_ACCEPT_RATE, config.HS_PA_RATE, config.HS_MEMORY_SIZE, config.HS_ITERATIONS)

    harmonies = [structure.create_individual(main_config.chromosome_type) for _ in range(memory_size)]
    main_config.tools.calculate_fitness_values(harmonies, list_of_funcs=[structure.fitness])
    harmony_memory = sortedlist.SortedList(harmonies, key=lambda x: x.values[0])

    print("Start harmony search: \n")
    with Timer() as timer, main_config.SolutionTracer(file_name) as solution_tracer:

        iteration = itertools.count()
        while next(iteration) < n:
            # print(iteration)
            new_harmony = structure.create_individual(main_config.chromosome_type)
            new_harmony.chromosome.clear_structure()
            harmony_structure = {}
            if separate_genes:  # choose for each gene if random or from memory
                for key in main_config.net.demands:
                    if random.random() < accept_rate:
                        harmony_structure[key] = choose_gene_from_hm(harmony_memory, key)
                        if random.random() < pa_rate:
                            harmony_structure[key] = change_gene(key, change_fun=new_harmony.chromosome._create_gene)
                    else:
                        harmony_structure[key] = new_harmony.chromosome._create_gene(key)
            else:  # draw all genes from memory or random
                if random.random() < accept_rate:
                    for key in main_config.net.demands:
                        harmony_structure[key] = choose_gene_from_hm(harmony_memory, key)
                        if random.random() < pa_rate:
                            harmony_structure[key] = change_gene(key, change_fun=new_harmony.chromosome._create_gene) \
                                if random.random() < 0.5 else \
                                mutate_gene(harmony_structure[key], new_harmony.chromosome.predefined_paths[key])
                else:
                    harmony_structure = new_harmony.chromosome._create_structure()
            new_harmony.chromosome.set_structure(harmony_structure)
            main_config.tools.calculate_fitness_values([new_harmony], list_of_funcs=[structure.fitness])
            # print(new_harmony)
            if harmony_memory[-1].values[0] > new_harmony.values[0]:
                harmony_memory.pop()
                harmony_memory.add(new_harmony)
            solution_tracer.update(harmony_memory[0], timer.elapsed)
            print('Iteration {} ended\n'.format(iteration) + str(solution_tracer))

        return solution_tracer.best


def change_gene(key, change_fun):
    return change_fun(key)


def mutate_gene(gene, predefined_paths):
    mutated_gene = structure.create_gene_with_random_path(gene, predefined_paths)
    return mutated_gene


def choose_gene_from_hm(hm: sortedlist.SortedList, key):
    genes = [harmony.chromosome.genes[key] for harmony in hm]
    return random.choice(genes)


def main():
    return run(accept_rate=config.HS_ACCEPT_RATE, pa_rate=config.HS_PA_RATE, memory_size=config.HS_MEMORY_SIZE,
                      n=config.HS_ITERATIONS, separate_genes=True)


if __name__ == "__main__":
    main()
