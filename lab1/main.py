from itertools import tee

import matplotlib.pyplot as plt
import numpy as np

from scipy.stats import expon, chisquare, chi2


def main():
    n_numbers = 10000
    random_numbers = gen_random_numbers(n_numbers)
    generated_numbers = rng(random_numbers, 0.4)
    mean_value = generated_numbers.mean()
    std_div = generated_numbers.std()
    lambda_obs = 1/mean_value
    print(f'Avgerage: {mean_value}')
    print(f'Variance: {generated_numbers.var()}')
    print(f'Standard deviation: {std_div}\n')
    build_graph(generated_numbers)

    hist, bin_edges = get_hist(generated_numbers)
    h_obs = hist/10000

    print(f'h observed sum: {h_obs.sum()}')
    print(f'intervals count: {len(h_obs)}\n')
    edges = pairwise(bin_edges)

    h_exp = np.array([
        cdf_expon(limits[0], lambda_obs) - cdf_expon(limits[1], lambda_obs)
        for limits in edges
    ])

    print(f'h expected sum: {h_exp.sum()}\n')

    # Scipy chisquare
    # chisquare_value = chisquare(h_obs, h_exp)
    # print(chisquare_value)

    print(f'chisquare value: {chisqure_stat(h_obs, h_exp)}')
    print(f'chisquare table value: {chi2.ppf(0.95, len(h_obs))}')


def rng(ksi, l):
    return -np.log(ksi)*1/l


def gen_random_numbers(n):
    return np.random.uniform(size=n)


def build_graph(x):
    plt.hist(x, bins=100, density=True)
    plt.savefig('graph.png')


def get_hist(arr, m=100):
    delta_x = (arr.max() - arr.min())/(m-1)
    xj_s = [0.0]
    for j in range(1, m):
        x = arr.min() - delta_x/2 + j*delta_x
        if len(xj_s) >= 2:
            counter = 0
            for el in arr:
                if el > xj_s[-1] and el < x:
                    counter += 1
            if counter < 5:
                continue
        xj_s.append(x)
    xj_s.append(arr.min() - delta_x/2 + (m)*delta_x)

    return np.histogram(arr, bins=xj_s)


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def group(arr, edges):
    for i, el in enumerate(arr):
        if el < 5:
            arr[i-1] += el
            arr, edges = group(np.delete(arr, i), np.delete(edges, i))
    return arr, edges


def cdf_expon(x, l):
    return np.e**(-l*x)


def chisqure_stat(h_obs, h_exp):
    chisquare_value = 0
    for obs, exp in zip(h_obs, h_exp):
        chisquare_value += ((obs-exp)**2)/exp
    return chisquare_value


if __name__ == '__main__':
    main()
