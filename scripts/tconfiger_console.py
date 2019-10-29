import datetime
import json
from itertools import chain
from pprint import pprint
import genetic.transponders as tconfiger
from genetic.transponders.utils import Transponder
from genetic.transponders import heapforce
import time
from functools import partial
import os


class Timer:
    def __init__(self, message=False):
        self.message = message

    def __enter__(self):
        self.start = time.clock()
        return self

    def __exit__(self, *args):
        self.end = time.clock()
        self.interval = self.end - self.start
        if self.message:
            print(f'It took {self.interval:.3f}s')


def load_json(filename):
    with open(filename) as f:
        return json.load(f)


def save_json(filename, data, **kwargs):
    with open(filename, 'w') as f:
        json.dump(data, f, **kwargs)
        # print(os.path.realpath(f.name))


def get_demands(data):
    demands = {demand['demand_value'] for demand in data['demands']}
    return demands


def merge_cofigs(x, y):
    merged = {demand: [] for demand in x}
    for demand in x:
        merged[demand].extend(x[demand])
        merged[demand].extend(y[demand])
    return merged


def generate_metric(filename, multipliers, transponders_data, method='unknown', description=''):
    metric = {
        'filename': [filename] if isinstance(filename, str) else filename,
        'multipliers': multipliers,
        'tranposnders_data': [
            {
                'transfer': t.transfer,
                'width': t.width,
                'cost': t.cost
            }
            for t in transponders_data
        ],
        'method': method,
        'description': description,
        'date': str(datetime.datetime.now())
    }
    return metric


def simple_configs():
    filenames = [
        'data/sndlib/json/polska/polska.json',
        'data/sndlib/json/nobel-germany/nobel-germany.json',
        'data/sndlib/json/germany50/germany50.json',
        'data/sndlib/json/janos-us/janos-us.json',
    ]
    multipliers = [0.25, 1.0, 5.0, 10.0, 20.0, 30.0, 40.0, 50.0]

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
            configs_data['configs'][demand] = tconfiger.utils.find_configs_for_demand(
                demand=demand,
                n=3,
                tdata=tdata,
                method=tconfiger.mixed.create_config
            )
            print(f'{i / len(demands_multiplied) * 100:.2f}% done')
    print(f'It took {t.interval:.3f}s')

    save_json('data/tconfigs_mixed_bez_400.json', configs_data, indent=4)


def multiple_objectives_configs():
    filenames = [
        'data/sndlib/json/abilene/abilene.json',
        'data/sndlib/json/polska/polska.json',
        'data/sndlib/json/nobel-germany/nobel-germany.json',
        'data/sndlib/json/germany50/germany50.json',
        'data/sndlib/json/janos-us/janos-us.json',
    ]
    # multipliers = [1.0]
    multipliers = [0.01, 0.02, 0.05, 0.1, 0.25, 1.0, 2.0, 5.0, 10.0, 20.0, 30.0, 40.0, 50.0]

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

    minimizing_width = partial(tconfiger.ip.create_config, width_weight=1.0, cost_weight=0.0)
    minimizing_cost = partial(tconfiger.ip.create_config, width_weight=0.0, cost_weight=1.0)

    with Timer(message=True) as t:
        best_width_configs = {}
        for i, demand in enumerate(sorted(demands_multiplied), start=1):
            best_width_configs[demand] = tconfiger.utils.find_configs_for_demand(
                demand=demand, n=1, tdata=transponders, method=minimizing_width)
            print(f'{i / len(demands_multiplied) * 100:.2f}% done')
    # input('Press <return> to start calculations')

    with Timer(message=True) as t:
        best_cost_configs = {}
        for i, demand in enumerate(sorted(demands_multiplied), start=1):
            best_cost_configs[demand] = tconfiger.utils.find_configs_for_demand(
                demand=demand, n=1, tdata=transponders, method=minimizing_cost)
            print(f'{i / len(demands_multiplied) * 100:.2f}% done')
    # input('Press <return> to start calculations')

    all_configs = merge_cofigs(best_cost_configs, best_width_configs)

    with Timer(message=True) as t:
        best_width_low_power_configs = {}
        for i, demand in enumerate(sorted(demands_multiplied), start=1):
            best_width_low_power_configs[demand] = tconfiger.utils.find_configs_for_demand(
                demand=demand, n=1, tdata=low_power_transponders, method=minimizing_width)
            print(f'{i / len(demands_multiplied) * 100:.2f}% done')
    # input('Press <return> to start calculations')

    with Timer(message=True) as t:
        best_cost_low_power_configs = {}
        for i, demand in enumerate(sorted(demands_multiplied), start=1):
            best_cost_low_power_configs[demand] = tconfiger.utils.find_configs_for_demand(
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
    save_json(f'data/transponder_configs_ip_5.json', configs_data, indent=4)


def heap_configs():
    filenames = [
        'data/sndlib/json/polska/polska.json',
        # 'data/sndlib/json/nobel-germany/nobel-germany.json',
        # 'data/sndlib/json/germany50/germany50.json',
        # 'data/sndlib/json/janos-us/janos-us.json',
    ]
    multipliers = [0.25, 1.0, 5.0, 10.0, 20.0, 30.0, 40.0, 50.0]

    demands = set()
    for filename in filenames:
        data = load_json(filename)
        demands = demands | get_demands(data)
        print('new demands:', len(demands), demands)

    demands_multiplied = {demand * m for demand in demands for m in multipliers}
    print('demands:', len(demands_multiplied), demands_multiplied)

    tdata = [
        Transponder(transfer=40, width=4, cost=2),
        Transponder(transfer=100, width=4, cost=5),
        Transponder(transfer=200, width=8, cost=7),
        Transponder(transfer=400, width=12, cost=9),
    ]

    configs_data = {
        'metric': generate_metric(filenames, multipliers, tdata),
        'configs': {}
    }

    input('Press <return> to start calculations')

    with Timer() as t:
        configs = heapforce.find_configs(demands_multiplied, tdata, 3)

    new_configs = {}
    for demand, demands_configs in configs:
        new_configs[demand] = []
        for config in demands_configs:
            new_configs[demand].append()

    configs_data['configs'] = configs
    print(f'It took {t.interval:.3f}s')

    save_json('data/tconfigs_heapforce.json', configs_data, indent=4)


if __name__ == '__main__':
    multiple_objectives_configs()
