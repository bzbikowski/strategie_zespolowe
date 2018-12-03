import random


class BeeScout(object):
    def __init__(self, problem, init_range):
        self.param = [random.random()*(prm[1] - prm[0]) + prm[0] for prm in init_range]
        self.fitness = problem
        self.f_value = 0

    def calculate_fitness(self):
        self.f_value = self.fitness(*self.param)

    def __lt__(self, other):
        return self.f_value < other.f_value

