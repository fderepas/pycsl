"""G29 route #143 helper — the callee's module IMPORTS LIM from a constants module."""
from multi_file_lib.r143_consts import LIM


#@ raises ValueError when LIM < 0
#@ assigns \nothing
def f4(k: int) -> int:
    if LIM < 0:
        raise ValueError
    return k


#@ requires k >= LIM
#@ ensures \result == k
#@ assigns \nothing
def g5(k: int) -> int:
    return k
