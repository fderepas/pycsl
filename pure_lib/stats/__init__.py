# pure_lib/stats — pure-Python statistics module model
# Named 'stats' to avoid stdlib name clash.
#
# Contracts derived from library_reference/statistics.rst.
# RST: "This module provides functions for calculating mathematical
#  statistics of numeric (Real-valued) data."
# RST: "mean(), median(), mode(), stdev(), variance()"
#
# Model: functions take list of non-negative integers.


#@ requires \length(data) > 0
#@ requires \forall i; (0 <= i and i < \length(data)) ==> data[i] >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def mean(data: list) -> int:
    """RST: 'Return the sample arithmetic mean of data.'
    Mean of non-negative values is non-negative."""
    s = 0
    i = 0
    n = len(data)
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop invariant s >= 0
    #@ loop variant n - i
    while i < n:
        s = s + data[i]
        i = i + 1
    return s // n


#@ requires \length(data) > 0
#@ requires \forall i; (0 <= i and i < \length(data)) ==> data[i] >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def median(data: list) -> int:
    """RST: 'Return the median (middle value) of numeric data.'
    For sorted data: data[n//2]. Returns non-negative element."""
    n = len(data)
    return data[n // 2]


#@ requires \length(data) > 0
#@ requires \forall i; (0 <= i and i < \length(data)) ==> data[i] >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def mode(data: list) -> int:
    """RST: 'Return the single most common data point.'
    Returns first element as model (mode requires counting)."""
    return data[0]


#@ requires \length(data) > 0
#@ requires \forall i; (0 <= i and i < \length(data)) ==> data[i] >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def fmean(data: list) -> int:
    """RST: 'Convert data to floats and compute the arithmetic mean.'
    Same as mean for integer model."""
    return mean(data)


#@ requires \length(data) > 0
#@ requires \forall i; (0 <= i and i < \length(data)) ==> data[i] >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def median_low(data: list) -> int:
    """RST: 'Return the low median of numeric data.'
    When n is even, returns lower of two middle values."""
    n = len(data)
    if n % 2 == 1:
        return data[n // 2]
    idx = n // 2 - 1
    return data[idx]


#@ requires \length(data) > 0
#@ requires \forall i; (0 <= i and i < \length(data)) ==> data[i] >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def median_high(data: list) -> int:
    """RST: 'Return the high median of numeric data.'
    When n is even, returns higher of two middle values."""
    n = len(data)
    return data[n // 2]
