from algorithm import BeesAlgorithm


def main():
    alg = BeesAlgorithm(fun1, 2,  [(-5.00, 5.00)])
    res, val = alg.start_algorithm(500)
    print(res, val)


def fun1(*args):
    return 50 - args[0] ** 2 - args[1] ** 2


if __name__ == "__main__":
    main()
