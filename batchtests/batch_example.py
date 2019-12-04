import bees.algorithm
import genetic.algorithm
import hybrid.algorithm
import hill_climbing.algorithm
import harmony_search.algorithm
import main_config


def main():

    algorithms = [
        hybrid.algorithm.main,
        hill_climbing.algorithm.main,
        harmony_search.algorithm.main,
        genetic.algorithm.main,
        bees.algorithm.main,
    ]
    nets = {
        ('abilene', 'abilene'): [0.01, 0.02],
        ('polska', 'pol'): [0.25, 1, 2, 5, 10, 20, 30],
        ('germany50', 'germany'): [10, 20, 30],
        ('janos-us', 'janos-us'): [1, 2],
    }

    for (netfile, datfile), intensities in nets.items():
        for intensity in intensities:
            main_config.init(netfile, datfile, intensity)
            for algorithm in algorithms:
                algorithm()
                print("\n\n\n")


if __name__ == '__main__':
    main()
