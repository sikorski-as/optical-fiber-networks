from genetic.structure import create_individual
from genetic import fitness
from bees import config
from hill_climbing.algorithm import random_neighbour_ksize
from random import randrange
import main_config


def bee_colony(nscouts=64, m_best=10, e_best=2, n1=20, n2=3, flower_patch_size=5, iterations=100):
    tools = main_config.tools
    scouts = [create_individual() for _ in range(nscouts)]
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
        top3_string = "\n    ".join(str(s) for s in scouts[:3])
        print(f'After iteration {i} top 3: \n    {top3_string}')
        new_scouts = [create_individual() for _ in range(nscouts - m_best)]
        tools.calculate_fitness_values(new_scouts, list_of_funcs=[fitness])
        scouts.extend(new_scouts)

    return sorted(scouts, key=lambda x: x.values[0])[0]


def main():
    adapted_predefined_paths = {key: [value[1] for value in values] for key, values in config.predefined_paths.items()}
    main_config.clock.start()
    best_individual = bee_colony(
        nscouts=config.BEES_NSCOUTS,
        m_best=config.BEES_M_BEST,
        e_best=config.BEES_E_BEST,
        n1=config.BEES_N1,
        n2=config.BEES_N2,
        flower_patch_size=config.BEES_FLOWER_PATCH_SIZE,
        iterations=config.BEES_ITERATIONS
    )
    main_config.clock.stop()
    file_name = f"{main_config.net_name}_Bees_I{main_config.intensity}_NSCOUTS{config.BEES_NSCOUTS}" \
        f"_M{config.BEES_M_BEST}_E{config.BEES_E_BEST}_N1{config.BEES_N1}_N2{config.BEES_N2}" \
        f"_PATCHSIZE{config.BEES_FLOWER_PATCH_SIZE}_N{config.BEES_ITERATIONS}"
    main_config.save_result(best_individual, file_name)
    return best_individual


if __name__ == '__main__':
    main()
