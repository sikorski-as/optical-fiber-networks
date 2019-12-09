import bees.algorithm
import genetic.algorithm
import hybrid.algorithm
import hill_climbing.algorithm
import harmony_search.algorithm
import main_config


def main():

    algorithms = [
        harmony_search.algorithm.main,
        hybrid.algorithm.main,
        hill_climbing.algorithm.main,
        genetic.algorithm.main,
        bees.algorithm.main,
    ]
    nets = {
        ('polska', 'pol'): [0.25, 1, 2, 5, 10, 20, 30],
        ('abilene', 'abilene'): [0.01, 0.02],
        ('germany50', 'germany'): [10, 20, 30],
        ('janos-us', 'janos-us'): [1, 2],
    }

    max_repetitions = {
        'hybrid.algorithm': 500,
        'hill_climbing.algorithm': 500,
        'harmony_search.algorithm': 500,
        'genetic.algorithm': 200,
        'bees.algorithm': 500,
    }

    for (netfile, datfile), intensities in nets.items():
        for intensity in intensities:
            for algorithm in algorithms:
                main_config.init(netfile, datfile, intensity, max_repetitions[algorithm.__module__])
                algorithm()
                print("\n\n\n")


if __name__ == '__main__':
    main()
