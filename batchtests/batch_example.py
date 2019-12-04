import bees.algorithm
import genetic.algorithm
import hybrid.algorithm
import hill_climbing.algorithm
import harmony_search.algorithm
import main_config


def main():
    nets = {
        ('germany50', 'germany'): [10],
        ('janos-us', 'janos-us'): [1, 2],
        ('polska', 'pol'): [1, 2, 5],
    }

    algorithms = [
        hybrid.algorithm.main,
        hill_climbing.algorithm.main,
        harmony_search.algorithm.main,
        bees.algorithm.main,
        genetic.algorithm.main,
    ]

    for (netfile, datfile), intensities in nets.items():
        for intensity in intensities:
            main_config.init(netfile, datfile, intensity)
            for algorithm in algorithms:
                algorithm()


if __name__ == '__main__':
    main()
