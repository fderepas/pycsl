"""PyCSL mock for Python's random module — Generate pseudo-random numbers with various common distributions."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def seed(a: int, version: int) -> int:
    """Mock: Initialize the random number generator. If *a* is omitted or ``None``, the current system time is used.  If randomness s..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getstate() -> int:
    """Mock: Return an object capturing the current internal state of the generator.  This object can be passed to :func:`setstate` t..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def setstate(state: int) -> int:
    """Mock: *state* should have been obtained from a previous call to :func:`getstate`, and :func:`setstate` restores the internal s..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def randbytes(n: int) -> int:
    """Mock: Generate *n* random bytes. This method should not be used for generating security tokens. Use :func:`secrets.token_bytes..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def randrange(stop: int) -> int:
    """Mock: Return a randomly selected element from ``range(start, stop, step)``. This is roughly equivalent to ``choice(range(start..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def randint(a: int, b: int) -> int:
    """Mock: Return a random integer *N* such that ``a <= N <= b``.  Alias for ``randrange(a, b+1)``."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getrandbits(k: int) -> int:
    """Mock: Returns a non-negative Python integer with *k* random bits. This method is supplied with the Mersenne Twister generator ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def choice(seq: int) -> int:
    """Mock: Return a random element from the non-empty sequence *seq*. If *seq* is empty, raises :exc:`IndexError`."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def choices(population: int, weights: int, cum_weights: int, k: int) -> int:
    """Mock: Return a *k* sized list of elements chosen from the *population* with replacement. If the *population* is empty, raises ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def shuffle(x: int) -> int:
    """Mock: Shuffle the sequence *x* in place. To shuffle an immutable sequence and return a new shuffled list, use ``sample(x, k=le..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sample(population: int, k: int, counts: int) -> int:
    """Mock: Return a *k* length list of unique elements chosen from the population sequence.  Used for random sampling without repla..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def binomialvariate(n: int, p: int) -> int:
    """Mock: `Binomial distribution <https://mathworld.wolfram.com/BinomialDistribution.html>`_. Return the number of successes for *..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def random() -> int:
    """Mock: Return the next random floating-point number in the range ``0.0 <= X < 1.0``"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def uniform(a: int, b: int) -> int:
    """Mock: Return a random floating-point number *N* such that ``a <= N <= b`` for ``a <= b`` and ``b <= N <= a`` for ``b < a``. Th..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def triangular(low: int, high: int, mode: int) -> int:
    """Mock: Return a random floating-point number *N* such that ``low <= N <= high`` and with the specified *mode* between those bou..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def betavariate(alpha: int, beta: int) -> int:
    """Mock: Beta distribution.  Conditions on the parameters are ``alpha > 0`` and ``beta > 0``. Returned values range between 0 and..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def expovariate(lambd: int) -> int:
    """Mock: Exponential distribution.  *lambd* is 1.0 divided by the desired mean.  It should be nonzero.  (The parameter would be c..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def gammavariate(alpha: int, beta: int) -> int:
    """Mock: Gamma distribution.  (*Not* the gamma function!)  The shape and scale parameters, *alpha* and *beta*, must have positive..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def gauss(mu: int, sigma: int) -> int:
    """Mock: Normal distribution, also called the Gaussian distribution. *mu* is the mean, and *sigma* is the standard deviation.  Th..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def lognormvariate(mu: int, sigma: int) -> int:
    """Mock: Log normal distribution.  If you take the natural logarithm of this distribution, you'll get a normal distribution with ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def normalvariate(mu: int, sigma: int) -> int:
    """Mock: Normal distribution.  *mu* is the mean, and *sigma* is the standard deviation. .. versionchanged:: 3.11 *mu* and *sigma*..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def vonmisesvariate(mu: int, kappa: int) -> int:
    """Mock: *mu* is the mean angle, expressed in radians between 0 and 2\*\ *pi*, and *kappa* is the concentration parameter, which ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def paretovariate(alpha: int) -> int:
    """Mock: Pareto distribution.  *alpha* is the shape parameter."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def weibullvariate(alpha: int, beta: int) -> int:
    """Mock: Weibull distribution.  *alpha* is the scale parameter and *beta* is the shape parameter."""
    return 0
