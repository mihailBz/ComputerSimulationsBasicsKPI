import numpy as np
import simpy
import pandas as pd

from lab3.main import setup, measurements
np.set_printoptions(suppress=True)


def run_experiment(intensity, mu_1):
    simulation_time = 30

    t_1 = 1 / mu_1
    env = simpy.Environment()
    env.process(setup(env, intensity, t_1, 5, 10))
    env.run(until=simulation_time)

    return pd.DataFrame(measurements)[["q1_waiting_time"]].mean().round(3)

def y(x1, x2):
    return 1.52 + 6.68*x1 + 6.58*x2 + 27.03*x1*x2

def norm_x(x, xmin, xmax):
    return (x - (xmin+xmax)/2)/((xmin-xmax)/2)

def main():
    lmbd = (0.1, 10)
    mu = (0.1, 10)

    matrix = np.array([
        [1, 1, 1, 1],
        [lmbd[0], lmbd[1], lmbd[0], lmbd[1],],
        [mu[0], mu[0], mu[1], mu[1]],
        [lmbd[0]*mu[0], lmbd[1]*mu[0], lmbd[0]*mu[1], lmbd[1]*mu[1]],
        [
            run_experiment(lmbd[0], mu[0])[0],
            run_experiment(lmbd[1], mu[0])[0],
            run_experiment(lmbd[0], mu[1])[0],
            run_experiment(lmbd[1], mu[1])[0],
        ]
    ])
    print()
    # print(matrix.T)
    # print(np.sum(matrix.T, axis=0))

    # print(run_experiment(0.22, 0.23)[0])
    print()
    i = 1
    for column in matrix[1:-1]:
        print()
        # print(column)
        # print('+')
        # print(matrix[-1])
        # print('=')
        # print(column+matrix[-1])
        # print()
        print(f'b{i} = {(column+matrix[-1]).sum()/4}')
        i+=1


    print()
    print('Experiment: ')
    print(matrix[-1])
    print("Regression: ")
    print([
            y(lmbd[0], mu[0]),
            y(lmbd[1], mu[0]),
            y(lmbd[0], mu[1]),
            y(lmbd[1], mu[1]),
        ])





if __name__ == '__main__':
    main()
