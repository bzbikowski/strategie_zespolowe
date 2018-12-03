from individual import BeeScout


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
        self.number_of_scouts = 100  # liczba pszczół zwiadowców (n)
        self.number_of_chosen_places = 10  # Liczba miejsc wybranych n z odwiedzonych(m)
        self.number_of_best_places = 5  # Liczba najlepszych obszarów dla m odwiedzanych miejsc (e)
        self.number_of_recruits_for_best = 10  # Liczba rekrutów dla najlepszych e obszarów (nep)
        self.number_of_recruits_for_other = 5  # Liczba rekrutów dla innych (m-e) wybranych obszarów (nsp)
        self.init_size_of_area = 0  # początkowy rozmiar obszarów (ngh)
        self.init_size_of_neighbourhood = 0
        self.stop_criteria = 1e-4

    def initiate_population(self, fun, init_data):
        self.scouts = [BeeScout(fun, init_data) for _ in range(self.number_of_scouts)]

    def start_algorithm(self, max_generation):
        self.initiate_population(self.function, self.init_data)
        generation = 0
        while generation < max_generation:
            for scout in self.scouts:
                scout.calculate_fitness()
            self.scouts.sort(reverse=True)
            for i in range(self.number_of_best_places):
                print(i)
            for i in range(self.number_of_best_places, self.number_of_chosen_places):
                print(i)
            pass



