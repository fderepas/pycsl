"""PyCSL mock for Python's getopt module — Portable parser for command line options; support both short and."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def getopt(args: int, shortopts: int, longopts: int) -> int:
    """Mock: Parses command line options and parameter list.  *args* is the argument list to be parsed, without the leading reference..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def gnu_getopt(args: int, shortopts: int, longopts: int) -> int:
    """Mock: This function works like :func:`getopt`, except that GNU style scanning mode is used by default. This means that option ..."""
    return 0
