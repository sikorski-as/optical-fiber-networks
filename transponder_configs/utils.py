import datetime
import json
import time
from collections import Counter, namedtuple
from contextlib import contextmanager

Transponder = namedtuple('Transponder', 'transfer width cost')


class Timer:
    DEFAULT_PRINT = False
    DEFAULT_ACCURACY = 3

    def __init__(self, name='It', accuracy: int = DEFAULT_ACCURACY, print_on_exit: bool = DEFAULT_PRINT):
        self._name = name
        self.print_on_exit = print_on_exit
        self._start = None
        self._accumulator = 0.0
        if not isinstance(accuracy, int) or accuracy < 0:
            raise ValueError('Accuracy must be a natural number')
        self._accuracy = accuracy

    def __enter__(self):
        self._start = time.time()
        return self

    def __exit__(self, *args):
        if self.print_on_exit:
            print(f'{self._name} took {self.elapsed:.{self._accuracy}f}s')

    @contextmanager
    def suspend(self):
        self._accumulator += self.elapsed
        yield
        self._start = time.time()

    @property
    def elapsed(self):
        if self._start is None:
            raise RuntimeError('Timer has to be started first, use with-statement')
        return time.time() - self._start + self._accumulator

    def print_elapsed(self):
        print(f'{self._name} so far: {self.elapsed:.{self._accuracy}f}s')


def load_config(filename: str):
    with open(filename) as f:
        d = json.load(f)
        try:
            # load new format (with metric)
            return {float(demand_value): config for demand_value, config in d['configs'].items()}
        except KeyError:
            # load old format (without metric, just demands and configurations)
            return {int(demand_value): config for demand_value, config in d.items()}


def save_config(filename: str, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def find_configs_for_demand(demand, n, tdata, method):
    configs = method(demand, tdata, n)
    return configs


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
