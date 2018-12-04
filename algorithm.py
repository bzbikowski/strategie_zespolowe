from individual import BeeScout, BeeWorker
import random


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
    def __init__(self, fun, no_of_param, param_range):
        self.scouts = []
        self.function = fun
        self.init_data = []
        if len(param_range) == no_of_param:
            self.init_data = param_range
        elif not len(param_range) == no_of_param and len(param_range) == 1:
            self.init_data = [param_range[0] for _ in range(no_of_param)]
        else:
            raise Exception("Błąd")
        self.number_of_scouts = 10  # liczba pszczół zwiadowców (n)
        self.number_of_chosen_places = 3  # Liczba miejsc wybranych n z odwiedzonych(m)
        self.number_of_best_places = 1  # Liczba najlepszych obszarów dla m odwiedzanych miejsc (e)
        self.number_of_recruits_for_best = 5  # Liczba rekrutów dla najlepszych e obszarów (nep)
        self.number_of_recruits_for_other = 3  # Liczba rekrutów dla innych (m-e) wybranych obszarów (nsp)
        self.init_size_of_area = 0  # początkowy rozmiar obszarów (ngh)
        self.init_size_of_neighbourhood = 0
        self.stop_criteria = 1e-4

        self.best_result = 0
        self.best_value = 0

    def initiate_population(self, fun, init_data):
        self.scouts = [BeeScout(fun) for _ in range(self.number_of_scouts)]
        for bee in self.scouts:
            bee.randomize_position(init_data)

    def start_algorithm(self, max_generation):
        self.initiate_population(self.function, self.init_data)
        generation = 0
        while generation < max_generation:
            print(generation)
            for scout in self.scouts:
                scout.calculate_fitness()
            self.scouts.sort(reverse=True)
            if self.scouts[0].f_value > self.best_value:
                self.best_value = self.scouts[0].f_value
                self.best_result = self.scouts[0].param
            if 50 - self.best_value < self.stop_criteria:
                break
            best_places_workers = []
            for i in range(self.number_of_best_places):
                local_workers = []
                for j in range(self.number_of_recruits_for_best):
                    worker = BeeWorker(self.scouts[0])
                    worker.search_neighbourhood(0.5)
                    local_workers.append(worker)
                self.scouts.pop(0)
                local_workers.sort(reverse=True)
                best_places_workers.append(local_workers[0])

            for i in range(self.number_of_best_places, self.number_of_chosen_places):
                local_workers = []
                for j in range(self.number_of_recruits_for_other):
                    worker = BeeWorker(self.scouts[0])
                    worker.search_neighbourhood(0.5)
                    local_workers.append(worker)
                    local_workers.sort(reverse=True)
                self.scouts.pop(0)
                best_places_workers.append(local_workers[0])
            for bee in self.scouts:
                if random.random() < 0.2:
                    bee.search_local(0.2)
            for bee in best_places_workers:
                scout = bee.promote()
                self.scouts.append(scout)
            generation += 1
        return self.best_result, self.best_value




