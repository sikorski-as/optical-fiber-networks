import copy
import numpy as np
import sortedcontainers


class Ant:
    def __init__(self, world, assessment_fun):
        self.solution = []
        self.used_edges = []
        self.current_node = None
        self.world = world
        self.visited_nodes = set()
        self.assessment_fun = assessment_fun

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

    @property
    def total_distance(self):
        return sum((self.world.get_edge_distance(edge) for edge in self.solution))

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

    def __hash__(self):
        return hash(sum([self.world.get_edge_distance(edge) for edge in self.solution]))

    def __eq__(self, other):
        return self.solution == other.solution

    def __lt__(self, other):
        return self.assessment_fun(self.solution) < self.assessment_fun(other.solution)

    def __str__(self):
        return f"Ant:{self.total_distance} {self.solution}"


def find_best_ant(ants, assessment_fun):
    ants_with_solutions = [ant for ant in ants if ant.solution is not None]
    if len(ants_with_solutions) == 0:
        return None
    return min(ants_with_solutions, key=lambda ant: assessment_fun(ant.solution))


class Colony:
    def __init__(self, n, k, world, select_fun, assessment_fun, goals, iterations):
        self.select_fun = select_fun
        self.assessment_fun = assessment_fun
        self.n = n
        self.k = k
        self.world = world
        self.ants = [Ant(world, assessment_fun) for _ in range(n)]
        self.best_ants = sortedcontainers.SortedSet(key=lambda el: self.assessment_fun(el.solution))
        self.goals = goals
        self.iterations = iterations

    def find_best_solution(self, goal, n=1):
        self.use_ants(goal, n)
        best_ants = copy.deepcopy(self.best_ants)
        self.best_ants.clear()
        return best_ants

    def use_ants(self, goal, n=1):
        for _ in range(n):
            for ant in self.ants:
                ant.find_solution(goal[0], goal[1])
                if ant.solution:
                    self.update_best_ants(ant)
                self.update_path()
                self.reset()

    def reset(self):
        for ant in self.ants:
            ant.reset()

    def update_path(self):
        for ant in self.ants:
            ant.update_path(self.assessment_fun)

    def find_solutions(self, goal):
        return [ant.find_solution(goal[0], goal[1]) for ant in self.ants]

    def update_best_ants(self, ant):
        # print(ant)
        if len(self.best_ants) == self.k and ant not in self.best_ants:
            if self.assessment_fun(self.best_ants[self.k - 1].solution) > self.assessment_fun(ant.solution):
                self.best_ants.pop()
                self.best_ants.add(copy.copy(ant))
        elif len(self.best_ants) < self.k:
            self.best_ants.add(copy.copy(ant))
