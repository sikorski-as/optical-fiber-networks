from genetic import run_genetic
from hybrid import config
import hill_climbinglib as hc
from hill_climbing.algorithm import random_neighbour, compare


def run_genetic_with_hill():
    adapted_predefined_paths = {key: [value[1] for value in values] for key, values in config.predefined_paths.items()}
    config.clock.start()
    best_individual = run_genetic(config.POP_SIZE, config.net, adapted_predefined_paths, config.transponders_config,
                                  config.demands, config.bands,
                                  config.slices_usage, config.transponders_cost)
    best_result = hc.run(best_individual, random_neighbour_function=random_neighbour, compare_function=compare,
                         n=config.HILL_ITERATIONS)
    config.clock.stop()
    file_name = f"{config.net_name}_Genetic+Hill_I{config.intensity}_GI{config.GA_ITERATIONS}_HI{config.HILL_ITERATIONS}"
    config.save_result(best_result, file_name)


if __name__ == "__main__":
    run_genetic_with_hill()
