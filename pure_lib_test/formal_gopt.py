# Formal test for getopt (gopt) module — universally quantified
#
# Based on library_reference/getopt.rst:
#   "Parses command line options and parameter list."
#   "After a non-option argument, all further arguments are non-options."
#   → option count <= total argc.
#   When all args parsed, remaining == 0.

from pure_lib.gopt import getopt_count, gnu_getopt_count, remaining_args


#@ requires argc >= 0 and argc < 2147483647
#@ requires shortopts >= 0 and shortopts < 2147483647
#@ ensures \result >= 0 and \result <= argc
def test_getopt_bounded(argc: int, shortopts: int) -> int:
    """getopt_count(argc, shortopts) <= argc for all inputs."""
    return getopt_count(argc, shortopts)


#@ requires argc >= 0 and argc < 2147483647
#@ requires shortopts >= 0 and shortopts < 2147483647
#@ ensures \result >= 0 and \result <= argc
def test_gnu_getopt_bounded(argc: int, shortopts: int) -> int:
    """gnu_getopt_count(argc, shortopts) <= argc for all inputs."""
    return gnu_getopt_count(argc, shortopts)


#@ requires argc >= 0 and argc < 2147483647
#@ requires parsed >= 0 and parsed < 2147483647
#@ ensures \result >= 0 and \result <= argc
def test_remaining_bounded(argc: int, parsed: int) -> int:
    """remaining_args(argc, parsed) <= argc for all inputs."""
    return remaining_args(argc, parsed)


#@ requires argc >= 0 and argc < 2147483647
#@ requires parsed >= argc
#@ ensures \result == 0
def test_remaining_excess(argc: int, parsed: int) -> int:
    """When parsed >= argc, remaining is 0 for all such inputs."""
    return remaining_args(argc, parsed)


#@ requires argc >= 0 and argc < 2147483647
#@ requires parsed >= 0 and parsed <= argc
#@ ensures \result == argc - parsed
def test_remaining_exact(argc: int, parsed: int) -> int:
    """When parsed <= argc, remaining == argc - parsed. Exact."""
    return remaining_args(argc, parsed)
