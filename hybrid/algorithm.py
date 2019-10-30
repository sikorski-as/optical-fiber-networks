from genetic import run_genetic
from hybrid import config
import hill_climbinglib as hc
from hill_climbing.algorithm import random_neighbour, compare
import main_config


def run_genetic_with_hill():
    adapted_predefined_paths = {key: [value[1] for value in values] for key, values in main_config.predefined_paths.items()}
    main_config.clock.start()
    best_individual = run_genetic(config.POP_SIZE, main_config.net, adapted_predefined_paths, main_config.transponders_config,
                                  main_config.bands, main_config.slices_usage, main_config.transponders_cost)
    best_result = hc.run(best_individual, random_neighbour_function=random_neighbour, compare_function=compare,
                         n=config.HILL_ITERATIONS)
    main_config.clock.stop()
    file_name = f"{main_config.net_name}_Genetic+Hill_I{main_config.intensity}_GI{config.GA_ITERATIONS}_HI{config.HILL_ITERATIONS}"
    main_config.save_result(best_result, file_name)


if __name__ == "__main__":
    run_genetic_with_hill()
