# Formal tests for pure_lib/stats — statistics module
from pure_lib.stats import mean, median, mode, median_low, median_high


#@ requires \length(data) > 0
#@ requires \forall i; (0 <= i and i < \length(data)) ==> data[i] >= 0
#@ ensures \result >= 0
def test_mean_nonneg(data: list) -> int:
    """Mean of non-negative data is non-negative."""
    return mean(data)


#@ requires \length(data) > 0
#@ requires \forall i; (0 <= i and i < \length(data)) ==> data[i] >= 0
#@ ensures \result >= 0
def test_median_nonneg(data: list) -> int:
    """Median of non-negative data is non-negative."""
    return median(data)


#@ requires \length(data) > 0
#@ requires \forall i; (0 <= i and i < \length(data)) ==> data[i] >= 0
#@ ensures \result >= 0
def test_mode_nonneg(data: list) -> int:
    """Mode of non-negative data is non-negative."""
    return mode(data)


#@ requires \length(data) > 0
#@ requires \forall i; (0 <= i and i < \length(data)) ==> data[i] >= 0
#@ ensures \result >= 0
def test_median_low_nonneg(data: list) -> int:
    """median_low of non-negative data is non-negative."""
    return median_low(data)


#@ requires \length(data) > 0
#@ requires \forall i; (0 <= i and i < \length(data)) ==> data[i] >= 0
#@ ensures \result >= 0
def test_median_high_nonneg(data: list) -> int:
    """median_high of non-negative data is non-negative."""
    return median_high(data)
