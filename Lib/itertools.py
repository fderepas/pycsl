"""PyCSL mock for Python's itertools module — Functions creating iterators for efficient looping."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def accumulate(iterable: int, function_: int, initial: int) -> int:
    """Mock: Make an iterator that returns accumulated sums or accumulated results from other binary functions. The *function* defaul..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def batched(iterable: int, n: int, strict: int) -> int:
    """Mock: Batch data from the *iterable* into tuples of length *n*. The last batch may be shorter than *n*. If *strict* is true, w..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def chain() -> int:
    """Mock: Make an iterator that returns elements from the first iterable until it is exhausted, then proceeds to the next iterable..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def combinations(iterable: int, r: int) -> int:
    """Mock: Return *r* length subsequences of elements from the input *iterable*. The output is a subsequence of :func:`product` kee..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def combinations_with_replacement(iterable: int, r: int) -> int:
    """Mock: Return *r* length subsequences of elements from the input *iterable* allowing individual elements to be repeated more th..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def compress(data: int, selectors: int) -> int:
    """Mock: Make an iterator that returns elements from *data* where the corresponding element in *selectors* is true.  Stops when e..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def count(start: int, step: int) -> int:
    """Mock: Make an iterator that returns evenly spaced values beginning with *start*. Can be used with :func:`map` to generate cons..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def cycle(iterable: int) -> int:
    """Mock: Make an iterator returning elements from the *iterable* and saving a copy of each.  When the iterable is exhausted, retu..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def dropwhile(predicate_: int, iterable: int) -> int:
    """Mock: Make an iterator that drops elements from the *iterable* while the *predicate* is true and afterwards returns every elem..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def filterfalse(predicate_: int, iterable: int) -> int:
    """Mock: Make an iterator that filters elements from the *iterable* returning only those for which the *predicate* returns a fals..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def groupby(iterable: int, key: int) -> int:
    """Mock: Make an iterator that returns consecutive keys and groups from the *iterable*. The *key* is a function computing a key v..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def islice(iterable: int, stop: int) -> int:
    """Mock: Make an iterator that returns selected elements from the iterable. Works like sequence slicing but does not support nega..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pairwise(iterable: int) -> int:
    """Mock: Return successive overlapping pairs taken from the input *iterable*. The number of 2-tuples in the output iterator will ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def permutations(iterable: int, r: int) -> int:
    """Mock: Return successive *r* length `permutations of elements <https://www.britannica.com/science/permutation>`_ from the *iter..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def product(repeat: int) -> int:
    """Mock: `Cartesian product <https://en.wikipedia.org/wiki/Cartesian_product>`_ of the input iterables. Roughly equivalent to nes..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def repeat(object: int, times: int) -> int:
    """Mock: Make an iterator that returns *object* over and over again. Runs indefinitely unless the *times* argument is specified. ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def starmap(function_: int, iterable: int) -> int:
    """Mock: Make an iterator that computes the *function* using arguments obtained from the *iterable*.  Used instead of :func:`map`..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def takewhile(predicate_: int, iterable: int) -> int:
    """Mock: Make an iterator that returns elements from the *iterable* as long as the *predicate* is true.  Roughly equivalent to:: ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def tee(iterable: int, n: int) -> int:
    """Mock: Return *n* independent iterators from a single iterable. Roughly equivalent to:: def tee(iterable, n=2): if n < 0: raise..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def zip_longest(fillvalue: int) -> int:
    """Mock: Make an iterator that aggregates elements from each of the *iterables*. If the iterables are of uneven length, missing v..."""
    return 0
