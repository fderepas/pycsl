"""PyCSL mock for Python's linecache module — Provides random access to individual lines from text files."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def getline(filename: int, lineno: int, module_globals: int) -> int:
    """Mock: Get line *lineno* from file named *filename*. This function will never raise an exception --- it will return ``''`` on e..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def clearcache() -> int:
    """Mock: Clear the cache.  Use this function if you no longer need lines from files previously read using :func:`getline`."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def checkcache(filename: int) -> int:
    """Mock: Check the cache for validity.  Use this function if files in the cache  may have changed on disk, and you require the up..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def lazycache(filename: int, module_globals: int) -> int:
    """Mock: Capture enough detail about a non-file-based module to permit getting its lines later via :func:`getline` even if *modul..."""
    return 0
