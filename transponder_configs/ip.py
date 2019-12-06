from collections import namedtuple

import mip


def create_config(demanded_value, tdata, n, width_weight=1, cost_weight=0, max_seconds=3600, debug=False):
    model = mip.Model()  # type: mip.Model
    model.verbose = 0
    nvars = len(tdata)
    tvars = [model.add_var('T{}'.format(i), var_type=mip.INTEGER, lb=0) for i in range(nvars)]
    model += mip.xsum(tvar * tdata[i].transfer for i, tvar in enumerate(tvars)) >= demanded_value
    model.objective = mip.minimize(
        mip.xsum(
            tvar * tdata[i].width * width_weight + tvar * tdata[i].cost * cost_weight
            for i, tvar in enumerate(tvars)
        )
    )

    model.cuts = 0
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
            vars = ('{}={}'.format(v.name, v.x) for v in model.vars)
            print(*vars, sep=', ')

    n = min(n, model.num_solutions)

    solutions = []
    for i in range(n):
        solution = [int(v.xi(i)) for v in model.vars]
        solutions.append(solution)

    return solutions
