from genetic.algorithm import run_genetic
from hybrid import config
import hill_climbinglib as hc
import main_config
from structure import random_neighbour, compare


def run_genetic_with_hill():
    main_config.clock.start()
    best_individual = run_genetic(pop_size=config.POP_SIZE, new_pop_size=config.NEW_POP_SIZE, n=config.GA_ITERATIONS)
    best_result = hc.run([best_individual], random_neighbour_function=random_neighbour, compare_function=compare,
                         n=config.HILL_ITERATIONS)
    main_config.clock.stop()
    file_name = f"{main_config.net_name}_Genetic+Hill_I{main_config.intensity}_GI{config.GA_ITERATIONS}_HI{config.HILL_ITERATIONS}"
    main_config.save_result(best_result, file_name)


if __name__ == "__main__":
    run_genetic_with_hill()


