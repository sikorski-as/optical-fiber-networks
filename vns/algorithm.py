from pprint import pprint

import main_config
import structure
from hill_climbinglib import vns
from vns import config


def run_vns():
    size = config.VNS_SIZE
    individuals = [structure.create_individual() for _ in range(size)]
    main_config.tools.calculate_fitness_values(individuals, [structure.fitness])
    main_config.clock.start()
    best = vns.run(individuals, random_neighbour_function=structure.random_neighbour_ksize,
                   compare_function=structure.compare, n=config.VNS_ITERATIONS, m=config.VNS_M, K=config.VNS_K)
    file_name = "{}_VNS_I{}_SIZE{}_N{}".format(main_config.net_name, main_config.intensity, size, config.VNS_ITERATIONS)
    main_config.clock.stop()
    main_config.save_result(best, file_name)
    pprint(best)


if __name__ == '__main__':
    run_vns()
