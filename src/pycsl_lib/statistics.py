"""PyCSL mock for Python's statistics module — Mathematical statistics functions."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def mean(data: int) -> int:
    """Mock: Return the sample arithmetic mean of *data* which can be a sequence or iterable. The arithmetic mean is the sum of the d..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fmean(data: int, weights: int) -> int:
    """Mock: Convert *data* to floats and compute the arithmetic mean. This runs faster than the :func:`mean` function and it always ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def geometric_mean(data: int) -> int:
    """Mock: Convert *data* to floats and compute the geometric mean. The geometric mean indicates the central tendency or typical va..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def harmonic_mean(data: int, weights: int) -> int:
    """Mock: Return the harmonic mean of *data*, a sequence or iterable of real-valued numbers.  If *weights* is omitted or ``None``,..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def kde(data: int, h: int, kernel: int, cumulative: int) -> int:
    """Mock: `Kernel Density Estimation (KDE) <https://www.itm-conferences.org/articles/itmconf/pdf/2018/08/itmconf_sam2018_00037.pdf..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def kde_random(data: int, h: int, kernel: int, seed: int) -> int:
    """Mock: Return a function that makes a random selection from the estimated probability density function produced by ``kde(data, ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def median(data: int) -> int:
    """Mock: Return the median (middle value) of numeric data, using the common 'mean of middle two' method.  If *data* is empty, :ex..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def median_low(data: int) -> int:
    """Mock: Return the low median of numeric data.  If *data* is empty, :exc:`StatisticsError` is raised.  *data* can be a sequence ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def median_high(data: int) -> int:
    """Mock: Return the high median of data.  If *data* is empty, :exc:`StatisticsError` is raised.  *data* can be a sequence or iter..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def median_grouped(data: int, interval: int) -> int:
    """Mock: Estimates the median for numeric data that has been `grouped or binned <https://en.wikipedia.org/wiki/Data_binning>`_ ar..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def mode(data: int) -> int:
    """Mock: Return the single most common data point from discrete or nominal *data*. The mode (when it exists) is the most typical ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def multimode(data: int) -> int:
    """Mock: Return a list of the most frequently occurring values in the order they were first encountered in the *data*.  Will retu..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pstdev(data: int, mu: int) -> int:
    """Mock: Return the population standard deviation (the square root of the population variance).  See :func:`pvariance` for argume..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pvariance(data: int, mu: int) -> int:
    """Mock: Return the population variance of *data*, a non-empty sequence or iterable of real-valued numbers.  Variance, or second ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def stdev(data: int, xbar: int) -> int:
    """Mock: Return the sample standard deviation (the square root of the sample variance).  See :func:`variance` for arguments and o..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def variance(data: int, xbar: int) -> int:
    """Mock: Return the sample variance of *data*, an iterable of at least two real-valued numbers.  Variance, or second moment about..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def quantiles(data: int, n: int, method: int) -> int:
    """Mock: Divide *data* into *n* continuous intervals with equal probability. Returns a list of ``n - 1`` cut points separating th..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def covariance(x: int, y: int) -> int:
    """Mock: Return the sample covariance of two sequence inputs *x* and *y*. Covariance is a measure of the joint variability of two..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def correlation(x: int, y: int, method: int) -> int:
    """Mock: Return the `Pearson's correlation coefficient <https://en.wikipedia.org/wiki/Pearson_correlation_coefficient>`_ for two ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def linear_regression(x: int, y: int, proportional: int) -> int:
    """Mock: Return the slope and intercept of `simple linear regression <https://en.wikipedia.org/wiki/Simple_linear_regression>`_ p..."""
    return 0
