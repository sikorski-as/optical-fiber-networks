from structure import create_individual
from structure import fitness
from main_config import chromosome_type, SolutionTracer
from bees import config
from structure import random_neighbour_ksize
from random import randrange
from utils import Timer
import main_config


def bee_colony(nscouts=64, m_best=10, e_best=2, n1=20, n2=3, flower_patch_size=5, iterations=100):
    tools = main_config.tools
    filename = "{}_Bees_I{}_NSCOUTS{}_M{}_E{}_N1{}_N2{}_PATCHSIZE{}_N{}".format(main_config.net_name, main_config.intensity, nscouts, m_best, e_best, n1, n2, flower_patch_size, iterations)

    with Timer() as timer, SolutionTracer(filename) as solution_tracer:
        scouts = [create_individual(ChromosomeType=chromosome_type) for _ in range(nscouts)]
        tools.calculate_fitness_values(scouts, list_of_funcs=[fitness])

        for i in range(1, iterations + 1):
            m_bees = tools.select_best(scouts, m_best)
            elite_bees = m_bees[:e_best]
            not_elite_bees = m_bees[e_best:]

            all_bees = []
            for elite_bee in elite_bees:
                for _ in range(n1):
                    all_bees.append(random_neighbour_ksize(elite_bee, k=randrange(flower_patch_size)))
            for not_elite_bee in not_elite_bees:
                for _ in range(n2):
                    all_bees.append(random_neighbour_ksize(not_elite_bee, k=randrange(flower_patch_size)))

            tools.calculate_fitness_values(all_bees, list_of_funcs=[fitness])
            all_bees.extend(m_bees)
            scouts = tools.select_best(all_bees, m_best)
            new_scouts = [create_individual(ChromosomeType=chromosome_type) for _ in range(nscouts - m_best)]
            tools.calculate_fitness_values(new_scouts, list_of_funcs=[fitness])

            solution_tracer.update(scouts[0], timer.elapsed)
            print('Iteration {} ended\n'.format(i) + str(solution_tracer))

            scouts.extend(new_scouts)
            if solution_tracer.repetitions_exceeded:
                break

    return solution_tracer.best


def main():
    best_individual = bee_colony(
        nscouts=config.BEES_NSCOUTS,
        m_best=config.BEES_M_BEST,
        e_best=config.BEES_E_BEST,
        n1=config.BEES_N1,
        n2=config.BEES_N2,
        flower_patch_size=config.BEES_FLOWER_PATCH_SIZE,
        iterations=config.BEES_ITERATIONS
    )
    return best_individual


if __name__ == '__main__':
    main()
