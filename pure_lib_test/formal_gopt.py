# Formal test for getopt (gopt) module
#
# Based on library_reference/getopt.rst:
#   "Parses command line options and parameter list."
#   "After a non-option argument, all further arguments are non-options."
#   → option count <= total argc.
#   When all args parsed, remaining == 0.

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


#@ ensures \result == 0
def test_remaining_excess() -> int:
    """When parsed >= argc, remaining is 0."""
    return remaining_args(3, 5)
