from itertools import tee

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
        start_node, end_node = key
        current_node = start_node
        organised_path = [start_node]
        while path:
            for edge in path:
                if edge[0] == current_node:
                    organised_path.append(edge[1])
                    path.remove(edge)
                    current_node = edge[1]
                elif edge[1] == current_node:
                    organised_path.append(edge[0])
                    path.remove(edge)
                    current_node = edge[0]
        return organised_path

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
