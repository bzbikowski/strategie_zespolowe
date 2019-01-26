import copy
import math
import os
import random
import sys

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from PySide2.QtCore import QThread, Signal

from lib.individual import BeeScout, BeeWorker


class BaseAlg(QThread):
    """
    stageChanged - signal, which as first param takes current scene and as second param
     takes max number of scene in presentation.
    """
    stageChanged = Signal(int, int)

    def __init__(self, parent, fun, canvas, panel):
        """
        :param parent: main widget from which this class is called
        :param fun: class representing problem to solve
        :type fun: Problem
        :param canvas: display all 2D graphs and maps
        :type canvas: PlotWidget
        :param panel: widget on which all user information will be displayed
        :type panel: QTextEdit
        """
        super(BaseAlg, self).__init__()
        self.parent = parent
        self.canvas = canvas
        self.panel = panel

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
    def __init__(self, parent, fun, canvas, panel):
        super(BeesAlgorithm, self).__init__(parent, fun, canvas, panel)
        self.index = 0
        self.stage = 0
        self.scouts = []
        self.function = fun.calculate
        self.target = fun.target
        self.best_value_vector = []
        self.init_data = list(fun.param_range)

        self.best_result = 0
        self.best_current_value = 999999
        self.max_global_value = self.target
        self.finish = None

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

        self.X = None
        self.Y = None
        self.Z = None

        self.final_data = {"best_result": 0,
                           "best_value": 0,
                           "no_of_gens": 0,
                           "best_value_per_gen": [],
                           "scouts_per_gen": [],
                           "workers_per_gen": [],
                           "other_scouts_per_gen": []}

    def initiate_population(self, fun, init_data, number_of_scouts):
        self.scouts = [BeeScout(fun) for _ in range(number_of_scouts)]
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
            self.scouts.sort(reverse=False)
            self.final_data["scouts_per_gen"].append(
                [(copy.deepcopy(s.f_value), copy.deepcopy(s.param)) for s in self.scouts])
            if self.scouts[0].f_value < self.best_current_value:
                self.best_current_value = self.scouts[0].f_value
                self.final_data["best_value"] = self.scouts[0].f_value
                self.final_data["best_result"] = self.scouts[0].param
            self.final_data["best_value_per_gen"].append(self.best_current_value)
            if self.final_data["best_value"] - self.target < self.stop_criteria:
                self.finish = 'stop'
                break
            data_workers = []
            best_places_workers = []
            for i in range(self.number_of_best_places):
                local_workers = []
                for j in range(self.number_of_recruits_for_best):
                    worker = BeeWorker(self.scouts[0])
                    worker.search_neighbourhood(self.neigh_size)
                    local_workers.append(worker)
                local_workers.sort(reverse=False)
                data_workers.append(local_workers)
                self.scouts.pop(0)
                best_places_workers.append(local_workers[0])

            for i in range(self.number_of_best_places, self.number_of_chosen_places):
                local_workers = []
                for j in range(self.number_of_recruits_for_other):
                    worker = BeeWorker(self.scouts[0])
                    worker.search_neighbourhood(self.neigh_size)
                    local_workers.append(worker)
                local_workers.sort(reverse=False)
                data_workers.append(local_workers)
                self.scouts.pop(0)
                best_places_workers.append(local_workers[0])
            self.final_data["workers_per_gen"].append(data_workers)
            self.final_data["other_scouts_per_gen"].append([])
            for bee in self.scouts:
                if random.random() < self.bee_search_prob:
                    bee.search_local(self.area_size, self.init_data)
                    self.final_data["other_scouts_per_gen"][generation].append(
                        (copy.deepcopy(bee.f_value), copy.deepcopy(bee.param)))
                else:
                    self.final_data["other_scouts_per_gen"][generation].append(None)
            for bee in best_places_workers:
                scout = bee.promote()
                self.scouts.append(scout)
            generation += 1
        if self.finish is None:
            self.finish = 'gen'

    def plot_stage(self, direction=None):
        max_index = 10
        if direction is None:
            self.index = 0
        elif direction:
            if self.index == max_index:
                return
            self.index += 1
        else:
            if self.index == 0:
                return
            self.index -= 1

        self.stageChanged.emit(self.index + 1, max_index + 1)
        self.canvas.fig.clf()
        ax = self.canvas.fig.add_subplot(111)

        stage = 0  # placeholder
        if self.index == 0:
            self.plot_base(ax)
            self.plot_scouts(ax, stage)
        elif self.index == 1:
            self.plot_base(ax)
            self.plot_areas_with_best(ax, stage)
        elif self.index == 2:
            self.plot_base(ax)
            self.plot_workers(ax, stage)
        elif self.index == 3:
            self.plot_base(ax)
            self.plot_best_workers(ax, stage)
        elif self.index == 4:
            self.plot_base(ax)
            self.plot_chosen_workers(ax, stage)
        elif self.index == 5:
            self.plot_base(ax)
            self.plot_others_scouts(ax, stage)
        elif self.index == 6:
            self.plot_base(ax)
            self.plot_diff_others_scouts(ax, stage)
        elif self.index == 7:
            self.plot_base(ax)
            self.plot_scouts_second(ax)
        elif self.index == 8:
            self.plot_base(ax)
            self.plot_scouts_last(ax)
        elif self.index == 9:
            self.plot_best_values(ax)
        elif self.index == 10:
            path = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), "resources/images/placeholder.png"))
            im = Image.open(path)
            self.panel.setText("This is the last slide of the presentation."
                               " In 'Options' menu you can take a look on another algorithm.")
            ax.imshow(im)
        self.canvas.draw()

    def buffor_base_map(self):
        res = 500

        x = np.linspace(self.init_data[0][0], self.init_data[0][1], res)
        y = np.linspace(self.init_data[1][0], self.init_data[1][1], res)

        self.X, self.Y = np.meshgrid(x, y)

        self.Z = np.zeros((res, res))
        for i in range(len(self.Z)):
            for j in range(len(self.Z[0])):
                v = self.function(x[j], y[i])
                self.Z[i][j] = v
                if v > self.max_global_value:
                    self.max_global_value = v

    def plot_base(self, ax):
        if self.X is None:
            self.buffor_base_map()
        levels = np.linspace(self.target, self.max_global_value, 50)
        cs = ax.contourf(self.X, self.Y, self.Z, levels, cmap=plt.get_cmap('summer'))
        cbar = self.canvas.fig.colorbar(cs)

    def plot_scouts(self, ax, gen):
        # Wyświetl skautów z wartościami
        for val, par in self.final_data['scouts_per_gen'][gen]:
            x_offset = (self.init_data[0][1] - self.init_data[0][0]) * 0.015
            ax.plot(par[0], par[1], 'bo')
            ax.text(par[0] + x_offset, par[1], f"{val:.2f}")
        self.panel.setText(f"At first step, create {self.number_of_scouts} bees scouts and randomize their position."
                           f" The current fitness of each bee is displayed above their position.")

    def plot_areas_with_best(self, ax, gen):
        # Wyszczególnij wybranych skautów i narysuj dla nich okrąg
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
            x_offset = (self.init_data[0][1] - self.init_data[0][0]) * 0.015
            ax.plot(par[0], par[1], f'{color}o')
            ax.text(par[0] + x_offset, par[1], f"{val:.2f}")
            index += 1
        self.panel.setText(f"Next, we choose {self.number_of_chosen_places} bees with the best fitness. "
                           f"{self.number_of_best_places} of these bees is selected as the best (red circle),"
                           f" the rest is marked with blue circle.")

    def plot_workers(self, ax, gen):
        # Dla każdego wyszczególnionego skauta, narysuj ich pracowników
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
            for worker in self.final_data["workers_per_gen"][gen][index]:
                ax.plot(worker.param[0], worker.param[1], f'{color}x')
            index += 1
        self.panel.setText(f"For the best bees (red circle), algorithm"
                           f" sends {self.number_of_recruits_for_best} bees workers (X marker) for neighbourhood "
                           f"searching of this area. Radius of this area is {self.neigh_size}. "
                           f"The same situation happens for other bees, but we send only"
                           f" {self.number_of_recruits_for_other} workers.")

    def plot_best_workers(self, ax, gen):
        # Pracownicy dla pierwszego najlepszego skauta
        val, par = self.final_data['scouts_per_gen'][gen][0]
        color = 'r'
        c1 = plt.Circle((par[0], par[1]), self.neigh_size, color=color, alpha=0.5)
        ax.add_artist(c1)
        ax.set_xlim(par[0] - self.neigh_size, par[0] + self.neigh_size)
        ax.set_ylim(par[1] - self.neigh_size, par[1] + self.neigh_size)
        first = True
        for worker in self.final_data["workers_per_gen"][gen][0]:
            if first:
                x_offset = (self.init_data[0][1] - self.init_data[0][0]) * 0.005
                ax.plot(worker.param[0], worker.param[1], f'{color}o', markersize=10.0)
                ax.text(worker.param[0] + x_offset, worker.param[1], f"{worker.f_value:.2f}")
                first = False
            else:
                x_offset = (self.init_data[0][1] - self.init_data[0][0]) * 0.005
                ax.plot(worker.param[0], worker.param[1], f'{color}x', markersize=10.0)
                ax.text(worker.param[0] + x_offset, worker.param[1], f"{worker.f_value:.2f}")
        self.panel.setText(f"From among these bees, for each area, we select the best individual (full circle marker)."
                           f" This worker will replace scout, which found this area, in next generation. ")

    def plot_chosen_workers(self, ax, gen):
        # pracownicy dla pierwszego wybranego skauta
        val, par = self.final_data['scouts_per_gen'][gen][self.best_places]
        color = 'b'
        c1 = plt.Circle((par[0], par[1]), self.neigh_size, color=color, alpha=0.5)
        ax.add_artist(c1)
        ax.set_xlim(par[0] - self.neigh_size, par[0] + self.neigh_size)
        ax.set_ylim(par[1] - self.neigh_size, par[1] + self.neigh_size)
        first = True
        for worker in self.final_data["workers_per_gen"][gen][self.best_places]:
            if first:
                x_offset = (self.init_data[0][1] - self.init_data[0][0]) * 0.0001
                ax.plot(worker.param[0], worker.param[1], f'{color}o', markersize=10.0)
                ax.text(worker.param[0] + x_offset, worker.param[1], f"{worker.f_value:.2f}")
                first = False
            else:
                x_offset = (self.init_data[0][1] - self.init_data[0][0]) * 0.0001
                ax.plot(worker.param[0], worker.param[1], f'{color}x', markersize=10.0)
                ax.text(worker.param[0] + x_offset, worker.param[1], f"{worker.f_value:.2f}")
        self.panel.setText(f"From among these bees, for each area, we select the best individual (full circle marker)."
                           f" This worker will replace scout, which found this area, in next generation. ")

    def plot_others_scouts(self, ax, gen):
        index = 0
        for val, par in self.final_data['scouts_per_gen'][gen]:
            if index >= self.chosen_places:
                c1 = plt.Circle((par[0], par[1]), self.area_size, color='k', alpha=0.5)
                ax.add_artist(c1)
                x_offset = (self.init_data[0][1] - self.init_data[0][0]) * 0.015
                ax.plot(par[0], par[1], 'bo')
                ax.text(par[0] + x_offset, par[1], f"{val:.2f}")
            index += 1
        ax.set_xlim(*self.init_data[0])
        ax.set_ylim(*self.init_data[1])
        self.panel.setText(f"The other scouts, which hadn't been chosen as best, they can search randomly area"
                           f" of radius {self.area_size} with probability of {self.bee_search_prob}.")

    def plot_diff_others_scouts(self, ax, gen):
        for pair_s, pair_o in zip(self.final_data['scouts_per_gen'][gen][self.chosen_places:],
                                  self.final_data['other_scouts_per_gen'][gen]):
            ax.plot(pair_s[1][0], pair_s[1][1], 'bo')
            if pair_o is not None:
                x_offset = (self.init_data[0][1] - self.init_data[0][0]) * 0.015
                ax.plot(pair_o[1][0], pair_o[1][1], 'ro')
                ax.text(pair_o[1][0] + x_offset, pair_o[1][1], f"{pair_o[0]:.2f}")
                head_width = 0.025
                head_length = 0.05
                kat = math.atan2(pair_o[1][1] - pair_s[1][1], pair_o[1][0] - pair_s[1][0])
                ax.arrow(pair_s[1][0], pair_s[1][1], pair_o[1][0] - pair_s[1][0] - math.cos(kat) * head_length,
                         pair_o[1][1] - pair_s[1][1] - math.sin(kat) * head_length,
                         head_width=head_width, head_length=head_length, fc='k', ec='k')
        ax.set_xlim(*self.init_data[0])
        ax.set_ylim(*self.init_data[1])
        self.panel.setText(f"For these bees, which changed its position, have been drawn their new positions"
                           f" (red circle) and corresponding vectors")

    def plot_scouts_second(self, ax):
        # Wyświetl skautów z wartościami
        for val, par in self.final_data['scouts_per_gen'][1]:
            x_offset = (self.init_data[0][1] - self.init_data[0][0]) * 0.015
            ax.plot(par[0], par[1], 'bo')
            ax.text(par[0] + x_offset, par[1], f"{val:.2f}")
        self.panel.setText(f"These steps are repeated, until number of generation reaches {self.max_generation} or "
                           f"the difference between the minimum value of the function"
                           f" and fitness of any scout will not exceed {self.stop_criteria:.0e}.")

    def plot_scouts_last(self, ax):
        # Wyświetl skautów z wartościami
        for val, par in self.final_data['scouts_per_gen'][len(self.final_data['scouts_per_gen']) - 1]:
            x_offset = (self.init_data[0][1] - self.init_data[0][0]) * 0.015
            ax.plot(par[0], par[1], 'bo')
            ax.text(par[0] + x_offset, par[1], f"{val:.2f}")
        if self.finish == 'stop':
            self.panel.setText(f"This is the last iteration of the algorithm."
                               f" Here, the best bee reached value {self.final_data['best_value']:.4f},"
                               f" which was enough to trigger stop criteria.")
        elif self.finish == 'gen':
            self.panel.setText(f"This is the last iteration of the algorithm."
                               f" Minimum error was not reached, so an algorithm stopped "
                               f"working afrer {self.max_generation} generations.")
        else:
            self.panel.setText("Weird bug!")

    def plot_best_values(self, ax):
        time = range(len(self.final_data['best_value_per_gen']))
        error = list(map(lambda x: x - self.target, self.final_data['best_value_per_gen']))
        ax.plot(time, error)
        ax.set_title("Absolute error between generations")
        ax.set_xlabel("Generation")
        ax.set_ylabel("Value of error")
        self.panel.setText(f"On the left, you can see ...")
