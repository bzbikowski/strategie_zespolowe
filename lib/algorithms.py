import random

import matplotlib.pyplot as plt
import numpy as np

from lib.individual import BeeScout, BeeWorker


class BeesAlgorithm(object):
    """
    begin
    Generuj losowo początkową populację rozwiązań
    Oceń jakość rozwiązań
    repreat
    Wybierz miejsca do przeszukiwania sąsiedztwa
    Wybierz rekrutów dla wybranych miejsc (większa liczba
    pszczół dla najlepszych
    e miejsc) i oceń ich
    Wybierz najlepszą pszczołę z każdego obszaru
    Przypisz pozostałym pszczołom przemieszczenia losowe i ocen je
    until kryterium końca BA niespełnione
    end
    """

    def __init__(self, fun, canvas):
        self.index = 0
        self.stage = 0
        self.scouts = []
        # self.problem = fun
        self.function = fun.calculate
        self.best_value_vector = []
        self.init_data = list(fun.param_range)
        self.canvas = canvas
        # self.number_of_scouts = 10  # liczba pszczół zwiadowców (n)
        # self.number_of_chosen_places = 3  # Liczba miejsc wybranych n z odwiedzonych(m)
        # self.number_of_best_places = 1  # Liczba najlepszych obszarów dla m odwiedzanych miejsc (e)
        # self.number_of_recruits_for_best = 4  # Liczba rekrutów dla najlepszych e obszarów (nep)
        # self.number_of_recruits_for_other = 2  # Liczba rekrutów dla innych (m-e) wybranych obszarów (nsp)
        # self.init_size_of_area = 0.2  # początkowy rozmiar obszarów (ngh)
        # self.init_size_of_neighbourhood = 0.5
        # self.bee_search_prob = 0.2
        # self.stop_criteria = 1e-4

        self.best_result = 0
        self.best_value = 0

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

    def start_algorithm(self, max_generation=500, number_of_scouts=10, number_of_chosen_places=3,
                        number_of_best_places=1,
                        number_of_recruits_for_best=4, number_of_recruits_for_other=2, init_size_of_area=0.2,
                        init_size_of_neighbourhood=0.5,
                        bee_search_prob=0.5, stop_criteria=1e-2):
        self.neigh_size = init_size_of_neighbourhood
        self.chosen_places = number_of_chosen_places
        self.best_places = number_of_best_places
        self.initiate_population(self.function, self.init_data, number_of_scouts)
        generation = 0
        while generation < max_generation:
            for scout in self.scouts:
                scout.calculate_fitness()
            self.scouts.sort(reverse=True)
            self.final_data["scouts_per_gen"].append([(s.f_value, s.param) for s in self.scouts])
            if self.scouts[0].f_value > self.best_value:
                self.final_data["best_value"] = self.scouts[0].f_value
                self.final_data["best_result"] = self.scouts[0].param
                self.final_data["best_value_vector"].append(self.best_value)
            if 50 - self.final_data["best_value"] < stop_criteria:
                break
            data_workers = []
            best_places_workers = []
            for i in range(number_of_best_places):
                local_workers = []
                for j in range(number_of_recruits_for_best):
                    worker = BeeWorker(self.scouts[0])
                    worker.search_neighbourhood(init_size_of_neighbourhood)
                    local_workers.append(worker)
                local_workers.sort(reverse=True)
                data_workers.append(local_workers)
                self.scouts.pop(0)
                best_places_workers.append(local_workers[0])

            for i in range(number_of_best_places, number_of_chosen_places):
                local_workers = []
                for j in range(number_of_recruits_for_other):
                    worker = BeeWorker(self.scouts[0])
                    worker.search_neighbourhood(init_size_of_neighbourhood)
                    local_workers.append(worker)
                local_workers.sort(reverse=True)
                data_workers.append(local_workers)
                self.scouts.pop(0)
                best_places_workers.append(local_workers[0])
            self.final_data["workers_per_gen"].append(data_workers)
            for bee in self.scouts:
                if random.random() < bee_search_prob:
                    bee.search_local(init_size_of_area)
            for bee in best_places_workers:
                scout = bee.promote()
                self.scouts.append(scout)
            generation += 1
        return

    def plot_stage(self, dir=None):
        """
        for now, just 2 parameters
        """
        if dir is None:
            self.index = 0
        elif dir:
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
            ax.plot(par[0], par[1], 'bo')
            index += 1

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
