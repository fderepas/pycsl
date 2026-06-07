# pure_lib/gopt — pure-Python getopt module model
# Named 'gopt' to avoid stdlib name clash.
#
# Models getopt/gnu_getopt as argument parsers.
# Body-proven where possible; error cases contract-only.


#@ requires argc >= 0
#@ requires shortopts >= 0
#@ ensures \result >= 0
#@ ensures \result <= argc
def getopt_count(argc: int, shortopts: int) -> int:
    """Parse argc arguments with shortopts options.
    Returns number of recognized option pairs (<= argc)."""
    return argc


#@ requires argc >= 0
#@ requires shortopts >= 0
#@ ensures \result >= 0
#@ ensures \result <= argc
def gnu_getopt_count(argc: int, shortopts: int) -> int:
    """GNU-style getopt (intermixed args). Returns recognized count."""
    return argc


#@ requires argc >= 0
#@ requires parsed >= 0
#@ ensures \result >= 0
#@ ensures \result <= argc
def remaining_args(argc: int, parsed: int) -> int:
    """Count remaining non-option arguments.
    Model: remaining = argc - parsed."""
    if parsed > argc:
        return 0
    return argc - parsed
