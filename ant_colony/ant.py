import copy
import numpy as np


class Ant:
    def __init__(self, world):
        self.solution = []
        self.used_edges = []
        self.current_node = None
        self.world = world
        self.visited_nodes = set()

    @property
    def remaining_nodes(self):
        return set(self.world.net.nodes) - self.visited_nodes

    # working for digraph
    @property
    def edges_available(self):
        edges = [
            (self.current_node, node, self.world.net[self.current_node][node]) for node in
            self.world.net[self.current_node] if node not in self.visited_nodes
        ]
        return [edge for edge in edges]

    # @property
    # def solution_without_cycles(self):
    #     if self.solution is None:
    #         return None
    #     solution = self.solution
    #     pos = len(solution) - 1
    #     while pos != 0:
    #         el = solution[pos]
    #         another_pos = solution.index(el)
    #         if another_pos != pos:
    #             solution = solution[:another_pos] + solution[pos:]
    #             self.used_edges = self.used_edges[:another_pos] + self.used_edges[pos:]
    #             pos = another_pos
    #         pos = pos - 1
    #     return solution

    def reset(self):
        self.solution = []
        self.used_edges = []
        self.current_node = None
        self.visited_nodes = set()

    def choose_edge(self):
        total_pheromones = sum(self.world.calculate_edge_weight(edge) for edge in self.edges_available)
        probability = [self.world.calculate_edge_weight(edge) / total_pheromones for edge in self.edges_available]
        # np.random.seed(13)
        return self.edges_available[np.random.choice(len(self.edges_available), 1, p=probability)[0]]

    def move(self, edge):
        if self.current_node != edge[0]:
            raise ValueError(f"Wrong edge used - current edge begin {edge[0]}, current node {self.current_node}")
        self.visited_nodes.add(self.current_node)
        self.solution.append(edge)
        self.used_edges.append(edge)
        self.current_node = edge[1]

    def find_solution(self, start_node, destination):
        self.current_node = start_node
        while self.current_node != destination:
            if self.edges_available:
                edge = self.choose_edge()
                self.move(edge)
            else:
                self.solution = None
                break
        return self.solution

    def update_path(self, assessment_fun):
        if self.solution is not None:
            self.world.update_pheromone(self.used_edges, assessment_fun(self.solution))


def find_best_ant(ants, assessment_fun):
    ants_with_solutions = [ant for ant in ants if ant.solution is not None]
    if len(ants_with_solutions) == 0:
        return None
    return min(ants_with_solutions, key=lambda ant: assessment_fun(ant.solution))


class Colony:
    def __init__(self, n, world, select_fun, assessment_fun):
        self.select_fun = select_fun
        self.assessment_fun = assessment_fun
        self.n = n
        self.world = world
        self.ants = [Ant(world) for _ in range(n)]

    def find_best_solution(self, goal, n=1):
        best_ant = self.find_best_ant(goal, n)
        return best_ant.solution if best_ant else None

    def find_best_ant(self, goal, n=1):
        global_best_ant = None
        for _ in range(n):
            for ant in self.ants:
                ant.find_solution(goal[0], goal[1])
            try:
                local_best_ant = self.select_fun((ant for ant in self.ants if ant.solution is not None), key=lambda a: self.assessment_fun(a.solution))
                if global_best_ant is None:
                    global_best_ant = copy.copy(local_best_ant)
                else:
                    best_out_of_two = self.select_fun((global_best_ant, local_best_ant),
                                                           key=lambda a: self.assessment_fun(a.solution))
                    global_best_ant = global_best_ant if global_best_ant is best_out_of_two else copy.copy(local_best_ant)
                self.update_path()
                self.reset()
            except ValueError:
                continue
        return copy.copy(global_best_ant)

    def reset(self):
        for ant in self.ants:
            ant.reset()

    def update_path(self):
        for ant in self.ants:
            ant.update_path(self.assessment_fun)

    def find_solutions(self, goal):
        return [ant.find_solution(goal[0], goal[1]) for ant in self.ants]
