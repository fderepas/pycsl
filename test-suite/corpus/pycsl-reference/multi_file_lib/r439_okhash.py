"""Helper for corpus 6642 (route #439 control): a CLAIMED hashing function and one that hashes nothing."""


#@ no_exception \all
#@ ensures \result == n + 1
def hs(k: str, n: int) -> int:
    s = {k}
    return n + 1


#@ ensures \result == n + 1
def inc(n: int) -> int:
    return n + 1
