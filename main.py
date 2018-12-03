from algorithm import BeesAlgorithm


def main():
    alg = BeesAlgorithm(fun1, 2,  [(-5.00, 5.00)])
    alg.start_algorithm(2000)


def fun1(*args):
    return 50 - args[0] ** 2 - args[1] ** 2


if __name__ == "__main__":
    main()
