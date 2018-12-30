import collections


class Problem(object):
    def __init__(self, data_dict):
        self.title = data_dict["title"]
        self.fun = data_dict["fun"]
        self.number_of_params = data_dict["x_param"]
        self.low = data_dict["x_min"]
        self.high = data_dict["x_max"]
        self.rpn_list = []
        self.convert_to_rpn()
        self.param_range = zip(self.low, self.high)

    def convert_to_rpn(self):
        fun_s = ['s', 'c', 't', 'g', 'e', 'm', 'n']
        opp_s = ['+', '-', '*', '/', '^', '%']
        temp = []
        var = False
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
                    continue
            if not var:
                if ch == "x":
                    var = True
                if str.isdigit(ch) or ch == '.':
                    temp.append(ch)
                if ch == ',':
                    self.rpn_list.append("".join(temp))
                    temp = []
                if ch in fun_s:
                    if not len(temp) == 0:
                        self.rpn_list.append("".join(temp))
                        temp = []
                    stack.appendleft(ch)
                if ch in opp_s:
                    if not len(temp) == 0:
                        self.rpn_list.append("".join(temp))
                        temp = []
                    while True:
                        if len(stack) == 0:
                            stack.append(ch)
                            break
                        if stack[0] in fun_s:
                            self.rpn_list.append(stack.popleft())
                            continue
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
                        stack.appendleft(ch)
                    if ch == ')':
                        while not stack[0] == '(':
                            self.rpn_list.append(stack.popleft())
                        stack.popleft()
        if not len(temp) == 0:
            self.rpn_list.append("".join(temp))
        while not len(stack) == 0:
            self.rpn_list.append(stack.popleft())
        return

    def change_symbols_rpn(self):
        pairs = [(" ", ""), ("sin", "s"), ("cos", "c"), ("tg", "t"), ("ctg", "g"),
                 ("exp", "e"), ("max", "m"), ("min", "n"), ("pi", "p")]
        for pair in pairs:
            self.fun = self.fun.replace(pair[0], pair[1])

    def calculate(self, *params):
        # todo calculate rpn
        return 0

    def __str__(self):
        return self.title
