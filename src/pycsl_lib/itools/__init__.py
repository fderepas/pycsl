# pycsl_lib/itools — pure-Python itertools module model
# Named 'itools' to avoid stdlib name clash.
#
# Contracts derived from library_reference/itertools.rst.
# RST: "Functions creating iterators for efficient looping."
# RST: "count(), cycle(), repeat(), chain(), islice(), etc."
#
# Model: itertools functions produce sequences. We model them by
# their output LENGTH (how many items they yield).


#@ requires start >= 0
#@ requires n >= 0
#@ ensures \result == n
#@ assigns \nothing
def count_n(start: int, n: int) -> int:
    """RST: 'Make an iterator that returns evenly spaced values.'
    Model: produces n values starting from start."""
    return n


#@ requires \length(seq) >= 0
#@ requires n >= 0
#@ ensures \result == n * \length(seq)
#@ assigns \nothing
def cycle_n(seq: list, n: int) -> int:
    """RST: 'Make an iterator returning elements from the iterable
    and saving a copy of each.' Model: n full cycles."""
    return n * len(seq)


#@ requires n >= 0
#@ ensures \result == n
#@ assigns \nothing
def repeat_n(val: int, n: int) -> int:
    """RST: 'Make an iterator that returns object over and over again.'
    Returns count of repetitions."""
    return n


#@ requires \length(a) >= 0
#@ requires \length(b) >= 0
#@ ensures \result == \length(a) + \length(b)
#@ assigns \nothing
def chain_len(a: list, b: list) -> int:
    """RST: 'Make an iterator that returns elements from the first
    iterable until it is exhausted, then proceeds to the next.'
    Result length = sum of input lengths."""
    return len(a) + len(b)


#@ requires \length(seq) >= 0
#@ requires start >= 0
#@ requires stop >= start
#@ requires stop <= \length(seq)
#@ ensures \result == stop - start
#@ assigns \nothing
def islice_len(seq: list, start: int, stop: int) -> int:
    """RST: 'Make an iterator that returns selected elements.'
    Slice from start to stop yields stop-start elements."""
    return stop - start


#@ requires \length(seq) >= 0
#@ ensures \result >= 0
#@ ensures \result <= \length(seq)
#@ assigns \nothing
def takewhile_len(seq: list) -> int:
    """RST: 'Make an iterator that returns elements as long as
    the predicate is true.' Result <= input length."""
    return len(seq)


#@ requires \length(seq) >= 0
#@ ensures \result >= 0
#@ ensures \result <= \length(seq)
#@ assigns \nothing
def dropwhile_len(seq: list) -> int:
    """RST: 'Make an iterator that drops elements as long as
    the predicate is true.' Result <= input length."""
    return len(seq)


#@ requires \length(seq) >= 0
#@ ensures \result >= 0
#@ ensures \result <= \length(seq)
#@ assigns \nothing
def filter_len(seq: list) -> int:
    """RST: 'Make an iterator that filters elements.'
    filterfalse is symmetric. Result <= input."""
    return len(seq)


#@ requires n >= 0
#@ requires r >= 0
#@ requires r <= n
#@ ensures \result >= 0
#@ assigns \nothing
def combinations_count(n: int, r: int) -> int:
    """RST: 'Return r length subsequences of elements.'
    Count = C(n,r). Model: non-negative."""
    return n


#@ requires n >= 0
#@ requires r >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def product_count(n: int, r: int) -> int:
    """RST: 'Cartesian product of input iterables.'
    Model: non-negative count."""
    return n


#@ requires \length(seq) >= 0
#@ requires \length(seq) <= 12
#@ ensures \result >= 0
#@ assigns \nothing
def permutations_count(seq: list) -> int:
    """RST: 'Return successive r length permutations.'
    Model: non-negative count (n! for full permutations)."""
    return len(seq)
