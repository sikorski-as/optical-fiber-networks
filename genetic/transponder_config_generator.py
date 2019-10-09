import json
from collections import namedtuple

import mip

Transponder = namedtuple('Transponder', 'transfer width cost')
tdata = [
    Transponder(transfer=40, width=4, cost=2),
    Transponder(transfer=100, width=4, cost=5),
    Transponder(transfer=200, width=8, cost=7),
    Transponder(transfer=400, width=12, cost=9),
]


def optimize_for_demand(demanded_value, tdata, max_seconds=3600, debug=False):
    model = mip.Model()  # type: mip.Model
    nvars = len(tdata)
    T = [model.add_var(f'T{i}', var_type=mip.INTEGER, lb=0) for i in range(nvars)]
    model += mip.xsum(tvar * tdata[i].transfer for i, tvar in enumerate(T)) >= demanded_value
    model.objective = mip.minimize(
        mip.xsum(
            tvar * tdata[i].width + tvar * tdata[i].cost / 2
            for i, tvar in enumerate(T)
        )
    )

    status = model.optimize(max_seconds=max_seconds)

    if debug:
        if status == mip.OptimizationStatus.OPTIMAL:
            print('optimal solution cost {} found'.format(model.objective_value))
        elif status == mip.OptimizationStatus.FEASIBLE:
            print('sol.cost {} found, best possible: {}'.format(model.objective_value, model.objective_bound))
        elif status == mip.OptimizationStatus.NO_SOLUTION_FOUND:
            print('no feasible solution found, lower bound is: {}'.format(model.objective_bound))
        if status == mip.OptimizationStatus.OPTIMAL or status == mip.OptimizationStatus.FEASIBLE:
            print('solution:')
            vars = (f'{v.name}={v.x}' for v in model.vars)
            print(*vars, sep=', ')

    return tuple(v.x for v in model.vars)


def read_config(filename: str):
    with open(filename) as f:
        d = json.load(f)
        return {int(demand_value): config for demand_value, config in d.items()}
