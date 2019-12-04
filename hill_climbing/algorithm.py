from pprint import pprint
import main_config
import hill_climbinglib as hc
import structure
from hill_climbing import config


def main():
    n = config.HILL_ITERATIONS
    size = config.HILL_SIZE
    print("Start hill climbing:\n")
    individuals = [structure.create_individual(main_config.chromosome_type) for _ in range(size)]
    main_config.tools.calculate_fitness_values(individuals, [structure.fitness])
    return hc.run(individuals, random_neighbour_function=structure.random_neighbour, compare_function=structure.compare,
           n=n)


if __name__ == "__main__":
    main()
