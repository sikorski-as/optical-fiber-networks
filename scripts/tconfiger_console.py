import datetime
import json
from itertools import chain
from pprint import pprint
import genetic.transponders as tconfiger
from genetic.transponders.utils import Transponder
from genetic.transponders import heapforce
import time
import os


class Timer:
    def __enter__(self):
        self.start = time.clock()
        return self

    def __exit__(self, *args):
        self.end = time.clock()
        self.interval = self.end - self.start


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
    return {demand: x.get(demand, []) + y.get(demand, []) for demand in chain(x, y)}


def generate_metric(filename, multipliers, transponders_data):
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
        'date': str(datetime.datetime.now())
    }
    return metric


def main():
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
            print(f'{i/len(demands_multiplied)*100:.2f}% done')
    print(f'It took {t.interval:.3f}s')

    save_json('data/tconfigs_mixed_bez_400.json', configs_data, indent=4)


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
    main()
