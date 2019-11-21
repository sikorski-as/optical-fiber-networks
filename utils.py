from copy import copy
from itertools import tee
import time
import sndlib


def pairwise(iterable):
    a, b = tee(iterable)
    next(b)
    return zip(a, b)


def get_predefined_paths(network_filename, dat_filename, npaths):
    """
    Load predefined paths from kozdro *.dat file.

    :param network_filename: sndlib *.json file
    :param dat_filename: kozdro's *.dat file
    :param npaths: number of predefined paths in *.dat file
    """
    nodes, edges = sndlib.UndirectedNetwork.get_nodes_and_edges(network_filename)
    paths_dict = {(n1, n2): [list() for _ in range(npaths)] for n1 in nodes for n2 in nodes if n1 != n2}
    nnodes, nedges = len(nodes), len(edges)

    def upload_path_row():
        vertex, path, edge, *row = datfile.readline().split()
        vertex1, path, edge = int(vertex) - 1, int(path) - 1, int(edge) - 1
        for vertex2, result in enumerate(row):
            if int(result):
                node1 = nodes[vertex1]
                node2 = nodes[vertex2]
                paths_dict[(node1, node2)][path].append(edges[edge])

    def organise_paths():
        for key, values in paths_dict.items():
            new_values = []
            for value in values:
                organised_path = organise_path(key, value)
                new_values.append((len(organised_path), organised_path))
            paths_dict[key] = new_values

    def organise_path(key, path: list):
        remove_redundant_edges(path)
        start_node, end_node = key
        current_node = start_node
        organised_path = [start_node]
        starting_path = copy(path)
        while path:
            l = len(path)
            for edge in path:
                if edge[0] == current_node:
                    organised_path.append(edge[1])
                    path.remove(edge)
                    current_node = edge[1]
                elif edge[1] == current_node:
                    organised_path.append(edge[0])
                    path.remove(edge)
                    current_node = edge[0]
            if l == len(path):
                print(starting_path)
                raise Exception("No coś nie tak")
        return organised_path

    def remove_redundant_edges(path):
        p = copy(path)
        used = set()
        for (n1, n2) in p:
            if (n1, n2) not in used:
                try:
                    path.remove((n2, n1))
                    used.add((n1, n2))
                    used.add((n2, n1))
                except ValueError:
                    continue
    with open(dat_filename) as datfile:
        datfile.readline()
        for _ in range(nedges):
            for _ in range(npaths):
                for _ in range(nnodes):
                    upload_path_row()
                datfile.readline()
            datfile.readline()
        organise_paths()

    return paths_dict




class Timer:
    DEFAULT_PRINT = False
    DEFAULT_ACCURACY = 3

    def __init__(self, name='It', accuracy: int = DEFAULT_ACCURACY, print_on_exit: bool = DEFAULT_PRINT):
        self._name = name
        self.print_on_exit = print_on_exit
        self._start = None
        if not isinstance(accuracy, int) or accuracy < 0:
            raise ValueError('Accuracy must be a natural number')
        self._accuracy = accuracy

    def __enter__(self):
        self._start = time.time()
        return self

    def __exit__(self, *args):
        if self.print_on_exit:
            print(f'{self._name} took {self.elapsed:.{self._accuracy}f}s')

    @property
    def elapsed(self):
        if self._start is None:
            raise RuntimeError('Timer has to be started first, use with-statement')
        return time.time() - self._start

    def print_elapsed(self):
        print(f'{self._name} so far: {self.elapsed:.{self._accuracy}f}s')
