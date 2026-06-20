# pycsl_lib/rng — pure-Python random module model
# Named 'rng' to avoid stdlib name clash.
#
# Contracts derived from library_reference/random.rst.
# RST: "This module implements pseudo-random number generators."
# RST: "randint(), randrange(), choice(), shuffle(), sample()"
#
# Model: random functions specify output RANGE (not distribution).
# All random state is in the Random class.


#@ requires a >= 0
#@ requires b >= a
#@ ensures \result >= a
#@ ensures \result <= b
#@ assigns \nothing
def randint(a: int, b: int) -> int:
    """RST: 'Return a random integer N such that a <= N <= b.'"""
    return a


#@ requires start >= 0
#@ requires stop > start
#@ ensures \result >= start
#@ ensures \result < stop
#@ assigns \nothing
def randrange(start: int, stop: int) -> int:
    """RST: 'Return a randomly selected element from range(start, stop).'"""
    return start


#@ requires \length(seq) > 0
#@ requires \forall i; (0 <= i and i < \length(seq)) ==> seq[i] >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def choice(seq: list) -> int:
    """RST: 'Return a random element from the non-empty sequence seq.'
    Returns an element (non-negative from non-negative array)."""
    return seq[0]


#@ requires \length(seq) > 0
#@ requires k >= 0
#@ requires k <= \length(seq)
#@ ensures \result == k
#@ assigns \nothing
def sample_len(seq: list, k: int) -> int:
    """RST: 'Return a k length list of unique elements chosen from seq.'
    Returns exactly k elements."""
    return k


#@ requires \length(seq) > 0
#@ ensures \result == \length(seq)
#@ assigns seq[0 .. \length(seq)]
def shuffle_len(seq: list) -> int:
    """RST: 'Shuffle the sequence x in place.' Length unchanged."""
    return len(seq)


""  # pycsl
#@ class invariant self._state >= 0
class Random:
    """RST: 'Class that implements the default pseudo-random number generator.'"""

    def __init__(self):
        self._state = 0

    #@ requires seed >= 0
    #@ ensures self._state == seed
    #@ assigns self._state
    def seed(self, seed: int) -> None:
        """RST: 'Initialize the random number generator.'"""
        self._state = seed

    #@ ensures \result == self._state
    #@ assigns \nothing
    def getstate(self) -> int:
        """RST: 'Return an object capturing the current internal state.'"""
        return self._state

    #@ requires state >= 0
    #@ ensures self._state == state
    #@ assigns self._state
    def setstate(self, state: int) -> None:
        """RST: 'state should have been obtained from getstate().'"""
        self._state = state

    #@ requires a >= 0
    #@ requires b >= a
    #@ ensures \result >= a
    #@ ensures \result <= b
    #@ assigns \nothing
    def randint(self, a: int, b: int) -> int:
        """RST: 'Return a random integer N such that a <= N <= b.'"""
        return a
