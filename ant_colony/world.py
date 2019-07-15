import geomanip
import networkx as nx


class World:
    # graph node(1,(lat, long))
    # edge  begin, end, weight, distance

    """
    :param vertices iterable containing all vertices in graph
    :param edges iterable containing 2-element tuple (begin_node, end_node)
    :param edge_dumping [db/km]
    :param node_dumping [db]
    """
    PHEROMONE_KEY = 'pheromone_level'
    DISTANCE_KEY = 'distance'
    DUMPING_KEY = 'dumping'

    def __init__(self, net, edge_dumping: dict, evaporation_level=0.1, basic_pheromone_level=0.1,
                 calculate_distance=False, alpha=1, beta=3, Q=1, node_dumping=1):
        self.net = net
        self.evaporation_level = evaporation_level
        self.basic_pheromone_level = basic_pheromone_level
        self.initialize_edges(calculate_distance, edge_dumping)
        self.initialize_nodes(node_dumping)
        self.alpha = alpha
        self.beta = beta
        self.Q = Q

    def initialize_nodes(self, node_dumping):
        nx.set_node_attributes(self.net, node_dumping, self.DUMPING_KEY)

    def initialize_edges(self, calculate_distance, edge_dumping):
        nx.set_edge_attributes(self.net, self.basic_pheromone_level, self.PHEROMONE_KEY)
        for edge in self.net.edges:
            distance = int(geomanip.haversine(edge[0].long, edge[0].lati, edge[1].long,
                                              edge[1].lati) if calculate_distance else 1)
            self.net.edges[edge][self.DISTANCE_KEY] = distance
            self.net.edges[edge][self.DUMPING_KEY] = edge_dumping[edge]

    def evaporate_pheromone(self):
        for edge in self.net.edges:
            self.net.edges[edge][self.PHEROMONE_KEY] = (1 - self.evaporation_level) * self.net.edges[edge][
                self.PHEROMONE_KEY]

    def update_pheromone(self, edges, solution_score):
        for edge in edges:
            edge[2][self.PHEROMONE_KEY] += self.Q / solution_score

    def reset_edges(self):
        for edge in self.net.edges:
            self.net.edges[edge][self.PHEROMONE_KEY] = self.basic_pheromone_level

    def calculate_edge_weight(self, edge):
        return pow(edge[2][self.PHEROMONE_KEY], self.alpha) * pow(1 / edge[2][self.DISTANCE_KEY], self.beta)

    def get_edge_distance(self, edge):
        return edge[2][self.DISTANCE_KEY]
