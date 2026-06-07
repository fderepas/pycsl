# pure_lib/gopt — pure-Python getopt module
# Named 'gopt' to avoid stdlib name clash.
#
# Contracts derived from library_reference/getopt.rst.
# RST: "Parses command line options and parameter list."
# RST: "The return value consists of two elements: the first is a list of
#       (option, value) pairs; the second is the list of program arguments
#       left after the option list was stripped."
#
# Model: args as list of int (token IDs), n = len(args).
# Options are negative values; non-options are non-negative.
# Returns (parsed_count, remaining_count) as tuple.


#@ requires n >= 0
#@ requires \length(args) == n
#@ ensures \result[0] >= 0
#@ ensures \result[1] >= 0
#@ ensures \result[0] + \result[1] == n
#@ ensures \result[0] <= n
#@ assigns \nothing
def getopt(args: list, n: int, shortopts: int) -> tuple:
    """RST: 'Parses command line options and parameter list.'
    After a non-option argument, all further arguments are non-options.
    Returns (parsed_option_count, remaining_arg_count).
    Scans the longest prefix of options (negative values)."""
    parsed = 0
    j = 0
    #@ loop invariant 0 <= j and j <= n
    #@ loop invariant parsed == j
    #@ loop variant n - j
    while j < n and args[j] < 0:
        parsed = parsed + 1
        j = j + 1
    return (parsed, n - parsed)


#@ requires n >= 0
#@ requires \length(args) == n
#@ ensures \result[0] >= 0
#@ ensures \result[1] >= 0
#@ ensures \result[0] + \result[1] == n
#@ ensures \result[0] <= n
#@ assigns \nothing
def gnu_getopt(args: list, n: int, shortopts: int) -> tuple:
    """RST: 'GNU style scanning mode — option and non-option arguments
    may be intermixed.' Returns (parsed_option_count, remaining_arg_count)."""
    parsed = 0
    j = 0
    #@ loop invariant 0 <= j and j <= n
    #@ loop invariant 0 <= parsed and parsed <= j
    #@ loop variant n - j
    while j < n:
        if args[j] < 0:
            parsed = parsed + 1
        j = j + 1
    return (parsed, n - parsed)
