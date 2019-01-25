import math
import random


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
        # for i, p in enumerate(self.param):
        #     self.param[i] = p + random.random() * 2 * area - area
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
