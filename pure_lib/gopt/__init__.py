# pure_lib/gopt — pure-Python getopt module model
# Named 'gopt' to avoid stdlib name clash.
#
# Contracts derived from library_reference/getopt.rst.
# RST: "Parses command line options and parameter list."
# RST: "returns (opts, args) pair"


#@ requires argc >= 0
#@ requires shortopts >= 0
#@ ensures \result >= 0
#@ ensures \result <= argc
def getopt_count(argc: int, shortopts: int) -> int:
    """RST: 'Parses command line options and parameter list.
    After a non-option argument, all further arguments are non-options.'
    Recognized option count <= total argument count."""
    return argc


#@ requires argc >= 0
#@ requires shortopts >= 0
#@ ensures \result >= 0
#@ ensures \result <= argc
def gnu_getopt_count(argc: int, shortopts: int) -> int:
    """RST: 'GNU style scanning mode — option and non-option arguments
    may be intermixed.' Recognized count still <= argc."""
    return argc


#@ requires argc >= 0
#@ requires parsed >= 0
#@ ensures \result >= 0
#@ ensures \result <= argc
#@ ensures parsed >= argc ==> \result == 0
def remaining_args(argc: int, parsed: int) -> int:
    """Remaining non-option arguments = argc - parsed.
    When all args are parsed, remaining is 0."""
    if parsed > argc:
        return 0
    return argc - parsed
