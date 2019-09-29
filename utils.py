from itertools import tee


def pairwise(iterable):
    a, b = tee(iterable)
    next(b)
    return zip(a, b)




