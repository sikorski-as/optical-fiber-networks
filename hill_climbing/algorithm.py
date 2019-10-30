from pprint import pprint
import main_config
import hill_climbinglib as hc
import structure
from hill_climbing import config
from hill_climbinglib import vns


def run_vns():
    individual = structure.create_individual()
    main_config.tools.calculate_fitness_values([individual], [structure.fitness])
    best = vns.run(individual, random_neighbour_function=structure.random_neighbour_ksize, compare_function=compare,
                   n=config.HILL_ITERATIONS,
                   m=config.HILL_M, K=config.HILL_K)
    pprint(best)


def run_hill():
    n = config.HILL_ITERATIONS
    size = config.HILL_SIZE
    individuals = [structure.create_individual() for _ in range(size)]
    main_config.tools.calculate_fitness_values(individuals, [structure.fitness])
    main_config.clock.start()
    best = hc.run(individuals, random_neighbour_function=structure.random_neighbour, compare_function=structure.compare, n=n)
    main_config.clock.stop()
    file_name = f"{main_config.net_name}_Hill_I{main_config.intensity}_SIZE{size}_N{n}"
    main_config.save_result(best, file_name)
    pprint(best)


if __name__ == "__main__":
    run_hill()
    # run_vns()
