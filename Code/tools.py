import numpy as np
import matplotlib.pyplot as plt


def uniform(n=1):
    """ This function simulates a uniform distribution on [0, 1] """
    return np.random.uniform(0, 1, n)


def uniform_1(n=1):
    """ This function simulates a uniform distribution on [-1, 1] """
    return uniform(n=n) * 2 - 1


def uniform_pi(n=1):
    """ This function simulates a uniform distribution on [-pi, pi] """
    return uniform(n=n) * 2 * np.pi - np.pi


def wrapped_cauchy(mu=0., kappa=1., n=1):
    """ This function simulates a the optimal wrapped cauchy distribution given kappa"""

    tau = 1 + np.sqrt(1 + 4 * kappa ** 2)
    rho = (tau - np.sqrt(2 * tau)) / (2 * kappa)
    s = (1 + rho**2) / (2 * rho)

    U = uniform(n=n)
    V = np.sign(uniform(n=n) - 0.5)
    sim = V * np.arccos((1 + s * np.cos(np.pi * U)) / (s + np.cos(np.pi * U)))
    return (sim + np.pi + mu) % (2 * np.pi) - np.pi


def normal(mean=0., std=1., n=1):
    """ This function simulates a normal distribution """

    X, Y = uniform_1(n=n), uniform_1(n=n)
    U = X ** 2 + Y ** 2

    X, U = X[(0 < U) & (U < 1)], U[(0 < U) & (U < 1)]
    while len(X) < n:
        x, y = uniform_1(n=n - len(X)), uniform_1(n=n - len(X))
        u = x ** 2 + y ** 2

        X = np.hstack([X, x[(0 < u) & (u < 1)]])
        U = np.hstack([U, u[(0 < u) & (u < 1)]])
    return mean + std * X * np.sqrt(-2 * np.log(U) / U)


def von_mises_unif(mu=0., kappa=1., n=1):
    """ This function simulates a von Mises distribution using the
    rejection sampler based on a uniform distribution on [-pi, pi]
    as proposal distribution.

    :param float mu: mu
    :param float kappa: kappa
    :param int n: output size

    :return array: sample of a rv following a von mises distribution.
    """

    # Compute a uniform on [-pi, pi]
    sample = uniform_pi(n=n)

    # Compute the value for the rejection test
    val = np.exp(kappa * (np.cos(sample - mu) - 1))

    # Acceptance step
    von_mises = sample[uniform(n) <= val]

    # Keep computing until we have a sample on size n
    while len(von_mises) < n:
        sample = uniform_pi(n - len(von_mises))
        val = np.exp(kappa * (np.cos(sample - mu) - 1))

        von_mises = np.hstack([von_mises, sample[uniform(n - len(von_mises)) <= val]])
    return von_mises


def von_mises_cauchy(mu=0., kappa=1., n=1):
    """
    This function simulates a von Mises distribution using the
    rejection sampler based on a wrapped Cauchy distribution :
    https://www.researchgate.net/publication/246035131_Efficient_Simulation_of_the_von_Mises_Distribution

    :param float mu: mu
    :param float kappa: kappa
    :param int n: output size

    :return array: sample of a rv following a von mises distribution.
    """

    if kappa != 0:
        tau = 1 + np.sqrt(1 + 4 * kappa**2)
        rho = (tau - np.sqrt(2 * tau)) / (2 * kappa)
        r = (1 + rho**2) / (2 * rho)

        # Create the sample
        z = np.cos(np.pi * uniform(n=n))
        f = (1 + r * z) / (r + z)
        c = kappa * (r - f)
        sample = np.sign(uniform_1(n=n)) * np.arccos(f)

        # Acceptance step
        von_mises = sample[np.log(c / uniform(n=n)) + 1 - c >= 0]

        # Keep computing until we have a sample on size n
        while len(von_mises) < n:
            z = np.cos(np.pi * uniform(n=n))
            f = (1 + r * z) / (r + z)
            c = kappa * (r - f)
            sample = np.sign(uniform_1(n=n)) * np.arccos(f)

            von_mises = np.hstack([von_mises, sample[np.log(c / uniform(n=n)) + 1 - c >= 0]])
    else:
        von_mises = uniform_pi(n=n)

    return (von_mises + np.pi + mu) % (2 * np.pi) - np.pi


def von_mises_unif_acceptance(kappa=1., n=100_000):
    """ This function estimates the acceptance rate according to a uniform distribution
    as proposal distribution.

    :param float kappa: kappa
    :param int n: number of simulations

    :return float: estimation of the acceptance rate in percentage
    """

    # Compute a uniform on [-pi, pi]
    sample = uniform_pi(n=n)

    # Compute the value for the rejection test
    val = np.exp(kappa * (np.cos(sample) - 1))

    # Acceptance step
    von_mises = sample[uniform(n) <= val]
    return 100 * von_mises.shape[0] / n


def von_mises_cauchy_acceptance(kappa=1., n=100_000):
    """
    This function estimates the acceptance rate according to a wrapped cauchy distribution
    as proposal distribution.
    https://www.researchgate.net/publication/246035131_Efficient_Simulation_of_the_von_Mises_Distribution

    :param float mu: mu
    :param float kappa: kappa
    :param int n: number of simulations

    :return float: estimation of the acceptance rate in percentage
    """

    if kappa != 0:
        tau = 1 + np.sqrt(1 + 4 * kappa**2)
        rho = (tau - np.sqrt(2 * tau)) / (2 * kappa)
        r = (1 + rho**2) / (2 * rho)

        # Create the sample
        z = np.cos(np.pi * uniform(n=n))
        f = (1 + r * z) / (r + z)
        c = kappa * (r - f)
        sample = np.sign(uniform_1(n=n)) * np.arccos(f)

        # Acceptance step
        von_mises = sample[np.log(c / uniform(n=n)) + 1 - c >= 0]

    else:
        von_mises = uniform_pi(n=n)

    return 100 * von_mises.shape[0] / n


def von_mises_density(x, mu=0., kappa=1.):
    """ Computes the density of a Von Mises distribution with parameters mu and kappa.
    Defined up to a constant multiplier.

    :param float x: point to be evaluated
    :param float mu: mu
    :param float kappa: kappa

    :return float: von Mises density evaluated on x (up to a constant multiplier).
    """
    return np.exp(kappa * np.cos(x - mu)) * (-np.pi <= x <= np.pi)


def simulate(array):
    plt.gcf().clear()
    plt.hist(array, bins=200, density=True, color='grey')
    plt.show()
