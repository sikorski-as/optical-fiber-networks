import heapq
import itertools
from operator import attrgetter
from dataclasses import dataclass, field
from collections import deque


class Queue:
    def __init__(self, values=None, max_length=None):
        self.values = deque(values, maxlen=max_length) if values is not None else deque(maxlen=max_length)

    def put(self, item):
        for i, another_item in enumerate(self.values):
            if item < another_item:
                if self.values.maxlen == len(self.values):
                    self.values.pop()
                self.values.insert(i, item)
                return

        if len(self.values) < self.values.maxlen:
            self.values.append(item)

    def as_list(self):
        return list(self.values)

    def __len__(self):
        return len(self.values)


def config_factory(tdata):
    class Config:
        __slots__ = ['value', 'demand']
        transponder_costs = [t.cost for t in tdata]
        transponder_transfer = [t.transfer for t in tdata]
        transponder_width = [t.width for t in tdata]

        def __init__(self, value, demand):
            self.value = value
            self.demand = demand

        def __lt__(self, another):
            if self.demand != another.demand:
                raise ValueError('Comparing configs for two different demand values!')

            transfer = sum(tu * tc for tu, tc in zip(self.value, self.transponder_transfer))
            another_transfer = sum(tu * tc for tu, tc in zip(another.value, self.transponder_transfer))

            satisfies = transfer >= self.demand
            another_satisfies = another_transfer >= self.demand

            width_cost = sum(tu * tc for tu, tc in zip(self.value, self.transponder_width))
            another_width_cost = sum(tu * tc for tu, tc in zip(another.value, self.transponder_width))

            if satisfies == another_satisfies:
                return width_cost < another_width_cost
            else:
                return satisfies

        def __repr__(self):
            return str(self.value)

    return Config


def create_config(demanded_value, tdata, n, debug=False):
    solutions = []
    return solutions


def find_configs(demands, tdata, n):
    print(demands, tdata, n)

    queues = {demand: Queue(max_length=n) for demand in demands}
    min_d, max_d = min(demands), max(demands)
    min_t, max_t = min(tdata, key=attrgetter('transfer')), max(tdata, key=attrgetter('transfer'))
    upper_bound = int(max_d / min_t.transfer) + 1
    lower_bound = 0

    # print(upper_bound, lower_bound)
    # print(max_d, min_d)

    possibilities = list(range(lower_bound, upper_bound))
    ranges = (possibilities for _ in range(len(tdata)))
    # print(possibilities)
    configs = itertools.product(*ranges)
    Config = config_factory(tdata)

    for conf in configs:
        for demand, queue in queues.items():
            queue.put(item=Config(conf, demand))
            # print('len', demand, len(queue), conf)

    return {demand: [c.value for c in q.values] for demand, q in queues.items()}
