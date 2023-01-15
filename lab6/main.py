import numpy as np
from scipy.linalg import solve
import itertools
from operator import itemgetter

import matplotlib.pyplot as plt


def get_x_powers(x, n):
    xs = []
    for i in range(n):
        xs.append(1 / x**i)
    return np.array(xs)


def calc_wi(xs, ys):
    a = np.array([get_x_powers(x, len(xs)) for x in xs])
    b = ys
    return solve(a, b)


def eval_model(xs, wi):
    a = np.array([get_x_powers(x, len(xs)) for x in xs])
    return np.array([sum(x * wi) for x in a])


def get_all_combinations_with_len_more_than_2(x):
    res = []
    for L in range(2, len(x) + 1):
        for subset in itertools.combinations(x, L):
            res.append(subset)
    return res


def find_sub_list_indices(sl, lst):
    ind = []
    for elem in sl:
        ind.append(lst.index(elem))
    return ind


def f(x, b):
    return sum(get_x_powers(x, len(b)) * b)


def main():
    data_x = np.arange(1.0, 8.6, 0.5)

    data_y = np.array(
        [
            14,
            18.222,
            18,
            17.216,
            16.444,
            15.778,
            15.219,
            14.749,
            14.352,
            14.014,
            13.722,
            13.469,
            13.248,
            13.052,
            12.879,
            12.724,
        ],
        dtype="float",
    )

    xs = get_all_combinations_with_len_more_than_2(data_x)
    models_coefs = []
    for x in xs:
        indices = find_sub_list_indices(list(x), list(data_x))
        y = itemgetter(*indices)(data_y)
        models_coefs.append(calc_wi(x, y))

    models_res = []
    for x, w in zip(xs, models_coefs):
        models_res.append(eval_model(x, w))

    mse_stat = []
    for w in models_coefs:
        y_obs = []
        for x in data_x:
            y_obs.append(f(x, w))
        mse_stat.append(np.square(np.subtract(np.array(y_obs), data_y)).mean())

    mse_stat = np.array(mse_stat)
    print(f"Error value {np.min(mse_stat)}")
    best_res_index = np.argmin(mse_stat)
    print(f"Best model id: {best_res_index}")

    final_y = []
    for x in data_x:
        final_y.append(f(x, models_coefs[best_res_index]))

    with plt.style.context("ggplot"):
        plt.plot(data_x, data_y, "--", label="Train")
        plt.plot(data_x, final_y, ":", label="Test", color='black')
        plt.legend()
        plt.plot()
        plt.show()


if __name__ == "__main__":
    main()
