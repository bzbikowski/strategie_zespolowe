import random

import matplotlib.pyplot as plt
import numpy as np
from PySide2.QtCore import QThread

from lib.individual import BeeScout, BeeWorker


class BaseAlg(QThread):
    def __init__(self):
        super(BaseAlg, self).__init__()

    def setup_algorithm(self, *args, **kwargs):
        """
        Sequence of parameters must match the order from schema.
        Must be reimplemented in parent class.
        """
        pass

    def plot_stage(self, direction=None):
        """
        Here, render learning example based on current stage.
        Checks for reaching boundaries must be written manually.
        Must be reimplemented in parent class.
        :param direction: If True/False, move current stage up/down. If None, initialize stage as zero index.
        :type direction: bool
        """
        pass

    def run(self):
        """
        Here, write all algorithm logic.
        Must be reimplemented in parent class.
        """
        pass


class BeesAlgorithm(BaseAlg):
    def __init__(self, fun, canvas, panel):
        # todo doc init function too
        super(BeesAlgorithm, self).__init__()
        self.index = 0
        self.stage = 0
        self.scouts = []
        self.function = fun.calculate
        self.best_value_vector = []
        self.init_data = list(fun.param_range)
        self.canvas = canvas
        self.panel = panel

        self.best_result = 0
        self.best_value = 0

        self.max_generation = None
        self.number_of_scouts = None
        self.number_of_chosen_places = None
        self.number_of_best_places = None
        self.number_of_recruits_for_best = None
        self.number_of_recruits_for_other = None
        self.area_size = None
        self.bee_search_prob = None
        self.stop_criteria = None
        self.neigh_size = None
        self.chosen_places = None
        self.best_places = None

        self.final_data = {"best_result": 0,
                           "best_value": 0,
                           "no_of_gens": 0,
                           "best_value_vector": [],
                           "scouts_per_gen": [],
                           "workers_per_gen": []}

    def initiate_population(self, fun, init_data, number_of_scouts):
        self.scouts = [BeeScout(fun) for _ in range(number_of_scouts)]
        init_data = list(init_data)
        for bee in self.scouts:
            bee.randomize_position(init_data)

    def setup_algorithm(self, max_generation=500, number_of_scouts=10, number_of_chosen_places=3,
                        number_of_best_places=1,
                        number_of_recruits_for_best=4, number_of_recruits_for_other=2, init_size_of_area=0.2,
                        init_size_of_neighbourhood=0.5,
                        bee_search_prob=0.5, stop_criteria=1e-3):
        self.max_generation = max_generation
        self.number_of_scouts = number_of_scouts
        self.number_of_chosen_places = number_of_chosen_places
        self.number_of_best_places = number_of_best_places
        self.number_of_recruits_for_best = number_of_recruits_for_best
        self.number_of_recruits_for_other = number_of_recruits_for_other
        self.area_size = init_size_of_area
        self.bee_search_prob = bee_search_prob
        self.stop_criteria = stop_criteria
        self.neigh_size = init_size_of_neighbourhood
        self.chosen_places = number_of_chosen_places
        self.best_places = number_of_best_places
        self.initiate_population(self.function, self.init_data, number_of_scouts)

    def run(self):
        generation = 0
        while generation < self.max_generation:
            for scout in self.scouts:
                scout.calculate_fitness()
            self.scouts.sort(reverse=True)
            self.final_data["scouts_per_gen"].append([(s.f_value, s.param) for s in self.scouts])
            if self.scouts[0].f_value > self.best_value:
                self.final_data["best_value"] = self.scouts[0].f_value
                self.final_data["best_result"] = self.scouts[0].param
                self.final_data["best_value_vector"].append(self.best_value)
            if 50 - self.final_data["best_value"] < self.stop_criteria:
                break
            data_workers = []
            best_places_workers = []
            for i in range(self.number_of_best_places):
                local_workers = []
                for j in range(self.number_of_recruits_for_best):
                    worker = BeeWorker(self.scouts[0])
                    worker.search_neighbourhood(self.neigh_size)
                    local_workers.append(worker)
                local_workers.sort(reverse=True)
                data_workers.append(local_workers)
                self.scouts.pop(0)
                best_places_workers.append(local_workers[0])

            for i in range(self.number_of_best_places, self.number_of_chosen_places):
                local_workers = []
                for j in range(self.number_of_recruits_for_other):
                    worker = BeeWorker(self.scouts[0])
                    worker.search_neighbourhood(self.neigh_size)
                    local_workers.append(worker)
                local_workers.sort(reverse=True)
                data_workers.append(local_workers)
                self.scouts.pop(0)
                best_places_workers.append(local_workers[0])
            self.final_data["workers_per_gen"].append(data_workers)
            for bee in self.scouts:
                if random.random() < self.bee_search_prob:
                    bee.search_local(self.area_size)
            for bee in best_places_workers:
                scout = bee.promote()
                self.scouts.append(scout)
            generation += 1

    def plot_stage(self, direction=None):
        # todo work on scale
        if direction is None:
            self.index = 0
        elif direction:
            if self.index == len(self.final_data['scouts_per_gen']) - 1:
                return 1
            self.index += 1
        else:
            if self.index == 0:
                return
            self.index -= 1
        self.canvas.fig.clf()
        ax = self.canvas.fig.add_subplot(111)
        self.plot_base(ax)

        stage = int(self.index / 3)
        mode = self.index % 3
        if mode == 0:
            self.plot_scouts(ax, stage)
        elif mode == 1:
            self.plot_areas_with_best(ax, stage)
        elif mode == 2:
            self.plot_workers(ax, stage)

        self.canvas.draw()

    def plot_base(self, ax):
        res = 500

        x = np.linspace(self.init_data[0][0], self.init_data[0][1], res)
        y = np.linspace(self.init_data[1][0], self.init_data[1][1], res)

        X, Y = np.meshgrid(x, y)

        Z = np.zeros((res, res))
        for i in range(len(Z)):
            for j in range(len(Z[0])):
                Z[i][j] = self.function(x[j], y[i])
        cs = ax.contourf(X, Y, Z, cmap=plt.get_cmap('plasma'))
        cbar = self.canvas.fig.colorbar(cs)

    def plot_scouts(self, ax, gen):
        for val, par in self.final_data['scouts_per_gen'][gen]:
            ax.plot(par[0], par[1], 'bo')
            # todo procentowo (2%) przesun lekko w prawo
            ax.text(par[0], par[1], f"{val:.2f}")
        self.panel.setText(f"At first step, create {self.number_of_scouts} bees scouts and randomize their position."
                           f" The current value of each bee is displayed above their position. If you want to check ..")

    def plot_areas_with_best(self, ax, gen):
        index = 0
        for val, par in self.final_data['scouts_per_gen'][gen]:
            if index < self.best_places:
                color = 'r'
            elif self.best_places <= index < self.chosen_places:
                color = 'b'
            else:
                break
            c1 = plt.Circle((par[0], par[1]), self.neigh_size, color=color, alpha=0.5)
            ax.add_artist(c1)
            ax.plot(par[0], par[1], f'{color}o')
            ax.text(par[0], par[1], f"{val:.2f}")
            index += 1
        self.panel.setText(f"...")

    def plot_workers(self, ax, gen):
        index = 0
        for val, par in self.final_data['scouts_per_gen'][gen]:
            if index < self.best_places:
                color = 'r'
            elif self.best_places <= index < self.chosen_places:
                color = 'b'
            else:
                break
            c1 = plt.Circle((par[0], par[1]), self.neigh_size, color=color, alpha=0.5)
            ax.add_artist(c1)
            first = True
            for worker in self.final_data["workers_per_gen"][gen][index]:
                if first:
                    ax.plot(worker.param[0], worker.param[1], f'{color}o')
                    first = False
                else:
                    ax.plot(worker.param[0], worker.param[1], f'{color}x')
            index += 1
