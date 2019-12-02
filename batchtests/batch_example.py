import bees.algorithm
import genetic.algorithm
import main_config


def main():
    intensities = [1, 2, 5]
    nets = [
        ('janos-us', 'janos-us'),
        ('polska', 'pol'),
    ]
    algorithms = [
        bees.algorithm.main,
        genetic.algorithm.main,
    ]

    for intensity in intensities:
        for netfile, datfile in nets:
            main_config.init(netfile, datfile, intensity)
            for algorithm in algorithms:
                algorithm()


if __name__ == '__main__':
    main()
