import collections
import math
import operator

import numpy as np


class Problem(object):
    def __init__(self, data_dict):
        self.title = data_dict["title"]
        self.fun = data_dict["fun"]
        self.target = data_dict["target"]
        self.number_of_params = data_dict["x_param"]
        self.low = data_dict["x_min"]
        self.high = data_dict["x_max"]
        self.rpn_list = []
        self.convert_to_rpn()
        self.param_range = zip(self.low, self.high)

    def convert_to_rpn(self):
        fun_s = ['s', 'c', 't', 'b', 'm', 'n']
        opp_s = ['+', '-', '*', '/', '^', '%']
        temp = []
        var = False
        fun = []
        fun_check = []
        prev_ch = None
        stack = collections.deque()
        self.change_symbols_rpn()
        for ch in self.fun:
            if var:
                if str.isdigit(ch):
                    temp.append(ch)
                if ch == ']':
                    index = "".join(temp)
                    self.rpn_list.append(f"x{index}")
                    temp = []
                    var = False
                    prev_ch = None
                    continue
            if not var:
                if ch == "x":
                    var = True
                if str.isdigit(ch) or ch == '.':
                    temp.append(ch)
                if ch == ',':
                    self.rpn_list.append("".join(temp))
                    temp = []
                if ch == 'p':
                    self.rpn_list.append(math.pi)
                if ch == 'e':
                    self.rpn_list.append(math.e)
                if ch in fun_s:
                    fun.append(ch)
                    fun_check.append(0)
                    if not len(temp) == 0:
                        self.rpn_list.append("".join(temp))
                        temp = []
                    stack.appendleft(ch)
                if ch in opp_s:
                    if not len(temp) == 0:
                        self.rpn_list.append("".join(temp))
                        temp = []
                    if ch == '-' and prev_ch is not None:
                        temp.append(ch)
                        continue
                    while True:
                        if len(stack) == 0:
                            stack.append(ch)
                            break
                        if ch in ['+', '-']:
                            if stack[0] in ['/', '*', '%', '^', '-']:
                                self.rpn_list.append(stack.popleft())
                                continue
                            stack.appendleft(ch)
                            break
                        if ch in ['*', '/']:
                            if stack[0] in ['^', '%', '/']:
                                self.rpn_list.append(stack.popleft())
                                continue
                            stack.appendleft(ch)
                            break
                        stack.appendleft(ch)
                        break
                if ch == '(':
                    if len(fun) > 0:
                        for i in range(len(fun_check)):
                            fun_check[i] += 1
                    stack.appendleft(ch)
                    prev_ch = ch
                    continue
                if ch == ')':
                    if not len(temp) == 0:
                        self.rpn_list.append("".join(temp))
                        temp = []
                    while not stack[0] == '(':
                        self.rpn_list.append(stack.popleft())
                    stack.popleft()
                    if len(fun) > 0:
                        for i in range(len(fun_check) - 1, -1, -1):
                            fun_check[i] -= 1
                            if fun_check[i] == 0:
                                fun.pop(i)
                                fun_check.pop(i)
                                self.rpn_list.append(stack.popleft())
                prev_ch = None
        if not len(temp) == 0:
            self.rpn_list.append("".join(temp))
        while not len(stack) == 0:
            self.rpn_list.append(stack.popleft())
        # print(self.rpn_list)
        return

    def change_symbols_rpn(self):
        pairs = [(" ", ""), ("sin", "s"), ("cos", "c"), ("tg", "t"),
                 ("exp", "b"), ("max", "m"), ("min", "n"), ("pi", "p")]
        for pair in pairs:
            self.fun = self.fun.replace(pair[0], pair[1])

    def calculate(self, *params):
        def is_correct(value):
            try:
                float(value)
                return True
            except ValueError:
                return False
        ops = {
            "+": operator.add,
            "-": operator.sub,
            "*": operator.mul,
            "/": operator.truediv,
            "^": operator.pow,
            "%": operator.mod,
            "s": math.sin,
            "c": math.cos,
            "t": math.tan,
            "b": math.exp,
        }
        stack = collections.deque()
        for token in self.rpn_list:
            if is_correct(token):
                stack.appendleft(token)
            elif 'x' in token:
                stack.appendleft(params[int(token[1:])])
            elif token in ['s', 'c', 't', 'b']:
                arg = float(stack.popleft())
                stack.appendleft(ops[token](arg))
            else:
                arg2 = float(stack.popleft())
                arg1 = float(stack.popleft())
                stack.appendleft(ops[token](arg1, arg2))
        return stack[0]

    def __str__(self):
        return self.title


class ProblemTsp(object):
    def __init__(self, data_dict):
        self.title = data_dict["title"]
        self.size = data_dict["size"]
        self.no_of_cities = 131
        # self.no_of_cities = data_dict["cities"]
        self.indicators = data_dict["indicators"]

        self.cities = None
        self.dist_matrix = None

        self.init_problem()

    def random_position(self):
        import random
        return random.random() * (self.size[1] - self.size[0]) + self.size[0]

    def init_problem(self):
        self.cities = np.loadtxt("./resources/maps/map_237points.csv", delimiter=' ')
        # self.cities = [(x, y) for (x, y) in zip((self.random_position() for _ in range(self.no_of_cities)),
        #                                         (self.random_position() for _ in range(self.no_of_cities)))]

        self.dist_matrix = self.create_dist_matrix()

    def create_dist_matrix(self):
        matrix = np.zeros((self.no_of_cities, self.no_of_cities))
        for i in range(self.no_of_cities):
            for j in range(i + 1, self.no_of_cities):
                if not i == j:
                    matrix[i][j] = matrix[j][i] = self.dist(self.cities[i], self.cities[j])
        return matrix

    @staticmethod
    def dist(c1, c2):
        return math.sqrt((c2[0] - c1[0]) ** 2 + (c2[1] - c1[1]) ** 2)

    def calculate(self, seq):
        distance = 0
        city_pop = -1
        starting_point = -1
        first_city = True
        for city in seq:
            if first_city:
                starting_point = city
                first_city = False
            elif not first_city and distance == 0:
                distance += self.dist_matrix[starting_point, city]
            else:
                distance += self.dist_matrix[city_pop, city]
            city_pop = city
        distance += self.dist_matrix[city_pop, starting_point]
        return distance

    def __str__(self):
        return self.title
