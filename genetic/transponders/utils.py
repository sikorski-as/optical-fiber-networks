import json
from collections import Counter, namedtuple
from . import ip, ea

Transponder = namedtuple('Transponder', 'transfer width cost')


def load_config(filename: str):
    with open(filename) as f:
        d = json.load(f)
        return {int(demand_value): config for demand_value, config in d.items()}


def save_config(filename: str, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def find_configs_for_range(a, b, n, tdata, method, stats=False):
    configs = {}
    for demand in range(a, b):
        configs[demand] = method(demand, tdata, n)

    if stats:
        total = 0
        for s in configs.values():
            total += len(s)

        stats = Counter({i: 0 for i in range(n + 1)})
        stats.update(len(s) for s in configs.values())
        print('average:', total / len(configs))
        for occurrences, value in stats.most_common(3):
            print(value, 'solutions', occurrences, 'times')

    return configs
