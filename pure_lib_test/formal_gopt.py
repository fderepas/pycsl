# Formal test for getopt (gopt) module
#
# Based on library_reference/getopt.rst:
#   "Parses command line options and parameter list."
#   "Returns (opts, args) pair."
#
# Tests verify contract postconditions:
#   - getopt_count: 0 <= result <= argc
#   - remaining_args: 0 <= result <= argc

from pure_lib.gopt import getopt_count, gnu_getopt_count, remaining_args


#@ ensures \result >= 0 and \result <= 10
def test_getopt_bounded() -> int:
    """getopt result bounded by argc."""
    return getopt_count(10, 5)


#@ ensures \result >= 0 and \result <= 10
def test_gnu_getopt_bounded() -> int:
    """gnu_getopt result bounded by argc."""
    return gnu_getopt_count(10, 5)


#@ ensures \result >= 0 and \result <= 10
def test_remaining_bounded() -> int:
    """remaining_args bounded by argc."""
    return remaining_args(10, 3)
