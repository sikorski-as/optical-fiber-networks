from genetic import config, run_genetic
import hill_climbinglib as hc
from genetic.algorithm import save_result
from hill_climbing.algorithm import random_neighbour, compare


def run_genetic_with_hill():
    adapted_predefined_paths = {key: [value[1] for value in values] for key, values in config.predefined_paths.items()}
    best_individual = run_genetic(config.POP_SIZE, config.net, adapted_predefined_paths, config.transponders_config,
                                  config.demands, config.bands,
                                  config.slices_usage, config.transponders_cost)
    best_result = hc.run(best_individual, random_neighbour_function=random_neighbour, compare_function=compare,
                         n=config.HILL_ITERATIONS)
    save_result(best_result.chromosome)


if __name__ == "__main__":
    run_genetic_with_hill()
