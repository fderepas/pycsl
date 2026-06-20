# pycsl_lib/lcache — pure-Python linecache module model
# Named 'lcache' to avoid stdlib name clash.
#
# Contracts derived from library_reference/linecache.rst.
# RST: "Get line lineno from file. This function will never raise an
#  exception — it will return '' on errors."


#@ requires lineno >= 1
#@ ensures \result >= 0
def getline(filename: int, lineno: int) -> int:
    """RST: 'Get line lineno from file named filename. This function will
    never raise an exception — it will return empty string on errors.'
    Returns line length (0 for not-found/error)."""
    return 0


#@ requires filename >= 0
#@ ensures \result >= 0
def getlines(filename: int) -> int:
    """RST: 'Return a list of lines... for the named file.'
    Returns total line count (0 for missing file)."""
    return 0


def clearcache() -> None:
    """RST: 'Clear the cache. Use this function if you no longer need
    lines from files previously read.' No return value."""
    pass


#@ requires filename >= 0
#@ ensures \result >= 0
def checkcache(filename: int) -> int:
    """RST: 'Check the cache for validity. Use if files may have changed
    on disk.' Returns number of entries invalidated."""
    return 0


#@ requires filename >= 0
#@ ensures \result >= 0 and \result <= 1
def lazycache(filename: int, module_globals: int) -> int:
    """RST: 'Capture enough detail about a non-file-based module to permit
    getting its lines later via getline.' Returns 0 (failure) or 1 (success)."""
    return 1
