import copy
import unittest
import sndlib
import yen
import networkx as nx


class YenTests(unittest.TestCase):

    def setUp(self):
        network_name = 'polska'
        self.net = sndlib.create_undirected_net(network_name, calculate_distance=True)
        self.DISTANCE_KEY = 'distance'

    def test_if_graph_not_changed(self):
        net_before = copy.deepcopy(self.net)
        for node in net_before:
            for neighbour in self.net[node]:
                yen.ksp(self.net, node, neighbour, nx.single_source_dijkstra, k=3, weight=self.DISTANCE_KEY)
        self.assertEqual(net_before.nodes, self.net.nodes)
        self.assertEqual(net_before.edges, self.net.edges)

    def test_if_graph_restored(self):
        net_before = copy.deepcopy(self.net)
        skipped_nodes = {node: yen.algorithm._find_all_edges(self.net, node, directed_graph=isinstance(self.net, sndlib.DirectedNetwork)) for i, node in enumerate(self.net.nodes) if i % 2 == 0}
        self.net.remove_nodes_from(skipped_nodes)
        yen.algorithm._restore_graph(self.net, skipped_nodes)
        self.assertEqual(net_before.nodes, self.net.nodes)
        self.assertEqual(net_before.edges, self.net.edges)

    def test_if_all_paths_created(self):
        k = 3
        paths = yen.ksp_all_nodes(self.net, nx.single_source_dijkstra, k=k, weight=self.DISTANCE_KEY)
        for node in self.net.nodes:
            for neighbour in self.net[node]:
                self.assertEqual(k, len(paths[node][neighbour]))
