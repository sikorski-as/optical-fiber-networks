from datetime import datetime
from functools import partial

import transponder_configs.config as tconfigs_config
import transponder_configs.ip as tconfigs_ip
from transponder_configs import Transponder, load_json, save_json, get_demands, merge_cofigs, generate_metric, Timer, \
    find_configs_for_demand


def simple_configs():
    filenames = tconfigs_config.TRANSPONDER_CONFIGS_FILENAMES
    multipliers = tconfigs_config.TRANSPONDER_CONFIGS_MULTIPLIERS

    demands = set()
    for filename in filenames:
        data = load_json(filename)
        new_demands = get_demands(data)
        demands = demands | new_demands
        print('new demands:', len(demands), demands)

    demands_multiplied = {demand * m for demand in demands for m in multipliers}
    print('demands:', len(demands_multiplied), demands_multiplied)

    tdata = [
        Transponder(transfer=40, width=4, cost=2),
        Transponder(transfer=100, width=4, cost=5),
        Transponder(transfer=200, width=8, cost=7),
        # Transponder(transfer=400, width=12, cost=9),
    ]

    configs_data = {
        'metric': generate_metric(filenames, multipliers, tdata),
        'configs': {}
    }

    input('Press <return> to start calculations')

    with Timer() as t:
        for i, demand in enumerate(sorted(demands_multiplied), start=1):
            configs_data['configs'][demand] = transponders.utils.find_configs_for_demand(
                demand=demand,
                n=3,
                tdata=tdata,
                method=transponders.mixed.create_config
            )
            print(f'{i / len(demands_multiplied) * 100:.2f}% done')
    print(f'It took {t.interval:.3f}s')

    save_json('data/tconfigs_mixed_bez_400.json', configs_data, indent=4)


def multiple_objectives_configs():
    filenames = tconfigs_config.TRANSPONDER_CONFIGS_FILENAMES
    multipliers = tconfigs_config.TRANSPONDER_CONFIGS_MULTIPLIERS

    demands = set()
    for filename in filenames:
        data = load_json(filename)
        new_demands = get_demands(data)
        demands = demands | new_demands
        print('new demands:', len(demands), demands)

    demands_multiplied = {demand * m for demand in demands for m in multipliers}
    print('demands:', len(demands_multiplied), demands_multiplied)

    transponders = [
        Transponder(transfer=40, width=4, cost=2),
        Transponder(transfer=100, width=4, cost=5),
        Transponder(transfer=200, width=8, cost=7),
        Transponder(transfer=400, width=12, cost=9),
    ]
    low_power_transponders = transponders[:3]

    # input('Press <return> to start calculations')
    # import webbrowser; webbrowser.open('https://www.youtube.com/watch?v=VBlFHuCzPgY', new=2)

    minimizing_width = partial(tconfigs_ip.create_config, width_weight=1.0, cost_weight=0.0)
    minimizing_cost = partial(tconfigs_ip.create_config, width_weight=0.0, cost_weight=1.0)

    with Timer(print_on_exit=True) as t:
        best_width_configs = {}
        for i, demand in enumerate(sorted(demands_multiplied), start=1):
            best_width_configs[demand] = find_configs_for_demand(
                demand=demand, n=1, tdata=transponders, method=minimizing_width)
            print(f'{i / len(demands_multiplied) * 100:.2f}% done')
    # input('Press <return> to start calculations')

    with Timer(print_on_exit=True) as t:
        best_cost_configs = {}
        for i, demand in enumerate(sorted(demands_multiplied), start=1):
            best_cost_configs[demand] = find_configs_for_demand(
                demand=demand, n=1, tdata=transponders, method=minimizing_cost)
            print(f'{i / len(demands_multiplied) * 100:.2f}% done')
    # input('Press <return> to start calculations')

    all_configs = merge_cofigs(best_cost_configs, best_width_configs)

    with Timer(print_on_exit=True) as t:
        best_width_low_power_configs = {}
        for i, demand in enumerate(sorted(demands_multiplied), start=1):
            best_width_low_power_configs[demand] = find_configs_for_demand(
                demand=demand, n=1, tdata=low_power_transponders, method=minimizing_width)
            print(f'{i / len(demands_multiplied) * 100:.2f}% done')
    # input('Press <return> to start calculations')

    with Timer(print_on_exit=True) as t:
        best_cost_low_power_configs = {}
        for i, demand in enumerate(sorted(demands_multiplied), start=1):
            best_cost_low_power_configs[demand] = find_configs_for_demand(
                demand=demand, n=1, tdata=low_power_transponders, method=minimizing_cost)
            print(f'{i / len(demands_multiplied) * 100:.2f}% done')
    # input('Press <return> to start calculations')

    all_low_power_configs = merge_cofigs(best_width_low_power_configs, best_cost_low_power_configs)

    # fill number of used 400Gb tranposnders with zeroes
    for configs in all_low_power_configs.values():
        for config in configs:
            config.append(0)

    configs_data = {
        'metric': generate_metric(filenames, multipliers, transponders,
                                  method='integer programming',
                                  description='merge of integer programming optimization '
                                              'with different objective functions (width/cost) '
                                              'and with and without 400Gb transponders,'
                                              'possible repetitions of configs for a demand'),
        'configs': merge_cofigs(all_configs, all_low_power_configs)
    }
    date_string = datetime.now().strftime('%Y-%m-%d-%H_%M_%S')
    save_json(f'data/transponder_configs_ip_{date_string}.json', configs_data, indent=4)


if __name__ == '__main__':
    multiple_objectives_configs()
