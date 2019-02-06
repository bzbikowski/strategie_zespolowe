import math
import random

import numpy as np


class Bee(object):
    def __init__(self, problem):
        self.param = []
        self.fitness = problem
        self.f_value = 0

    def calculate_fitness(self):
        self.f_value = self.fitness(*self.param)

    def __lt__(self, other):
        return self.f_value < other.f_value

    def __gt__(self, other):
        return self.f_value > other.f_value

    def __str__(self):
        return str(self.f_value)


class BeeScout(Bee):
    def __init__(self, problem):
        super(BeeScout, self).__init__(problem)

    def randomize_position(self, init_range):
        self.param = [random.random() * (prm[1] - prm[0]) + prm[0] for prm in init_range]

    def search_local(self, area, bound):
        s = random.random() * 2 * area - area
        k = random.random() * 360
        x1 = self.param[0] + math.sin(k) * s
        x2 = self.param[1] + math.cos(k) * s
        if x1 < bound[0][0]:
            x1 = bound[0][0]
        elif x1 > bound[0][1]:
            x1 = bound[0][1]
        if x2 < bound[1][0]:
            x2 = bound[1][0]
        elif x2 > bound[1][1]:
            x2 = bound[1][1]
        self.param = [x1, x2]
        self.calculate_fitness()

    def assign_param(self, param):
        self.param = param


class BeeWorker(Bee):
    def __init__(self, scout):
        super(BeeWorker, self).__init__(scout.fitness)
        self.scout = scout

    def search_neighbourhood(self, neigh_area):
        s = random.random() * 2 * neigh_area - neigh_area
        k = random.random() * 360
        x1 = self.scout.param[0] + math.sin(k) * s
        x2 = self.scout.param[1] + math.cos(k) * s
        self.param = [x1, x2]
        self.calculate_fitness()

    def promote(self):
        scout = BeeScout(self.scout.fitness)
        scout.assign_param(self.param)
        return scout


class AntWorker(object):
    def __init__(self):
        self.total_cost = 0.0
        self.path = []
        self.local_pheromone = []

    def __lt__(self, other):
        return self.total_cost < other.total_cost

    def __gt__(self, other):
        return self.total_cost > other.total_cost

    def calculate_fitness(self, f):
        self.total_cost = f(self.path)

    def choose_path(self, alg, dist):
        rank = len(dist)
        eta = [[0 if i == j else 1 / dist[i][j] for j in range(rank)] for i in range(rank)]
        possible = list(range(rank))
        visited = []
        start = random.randint(0, rank - 1)
        possible.remove(start)
        visited.append(start)
        last = start
        for _ in range(rank - 1):
            if alg.greediness >= random.random():
                index = np.argmax(np.multiply(np.take(alg.pheromones[last], possible),
                                              np.power(np.take(eta[last], possible), alg.beta)))
                selected = possible[int(index)]
            else:
                denominator = 0
                for j in possible:
                    denominator += alg.pheromones[last][j] ** alg.alpha * eta[last][j] ** alg.beta
                probabilities = [0 for _ in range(rank)]
                for j in range(rank):
                    try:
                        possible.index(j)
                        probabilities[j] = alg.pheromones[last][j] ** alg.alpha * eta[last][j] ** alg.beta / denominator
                    except ValueError:
                        pass
                selected = -1
                rand = random.random()
                for j, probability in enumerate(probabilities):
                    rand -= probability
                    if rand <= 0:
                        selected = j
                        break
            possible.remove(selected)
            visited.append(selected)
            last = selected
        self.path = visited

    def local_update_pheromone(self, alg):
        rank = len(self.path)
        self.local_pheromone = [[0 for _ in range(rank)] for _ in range(rank)]
        for i in range(len(self.path) - 1):
            x = self.path[i]
            y = self.path[i + 1]
            new_value = self.local_pheromone[x][y] * (1 - alg.local_phero_c) + alg.local_phero_c * alg.init_phero_val
            self.local_pheromone[x][y] = new_value
            self.local_pheromone[y][x] = new_value
        x = self.path[len(self.path) - 1]
        y = self.path[0]
        new_value = self.local_pheromone[x][y] * (1 - alg.local_phero_c) + alg.local_phero_c * alg.init_phero_val
        self.local_pheromone[x][y] = new_value
        self.local_pheromone[y][x] = new_value
