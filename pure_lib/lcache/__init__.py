# pure_lib/lcache — pure-Python linecache module model
# Named 'lcache' to avoid stdlib name clash.
#
# Models linecache.getline and getlines for source reading.
# Contract-only: file I/O is modelled abstractly.


#@ requires lineno >= 1
#@ ensures \result >= 0
def getline(filename: int, lineno: int) -> int:
    """Get a line from a file by line number.
    Model: returns line length (>= 0). Returns 0 for missing lines."""
    return 0


#@ requires filename >= 0
#@ ensures \result >= 0
def getlines(filename: int) -> int:
    """Get all lines from a file. Returns total line count."""
    return 0


def clearcache() -> None:
    """Clear the linecache. No contracts needed — pure side effect on cache."""
    pass


#@ requires filename >= 0
#@ ensures \result >= 0
def checkcache(filename: int) -> int:
    """Check validity of cache entries. Returns number invalidated."""
    return 0


#@ requires filename >= 0
#@ ensures \result >= 0
def lazycache(filename: int, module_globals: int) -> int:
    """Seed the cache for a filename without reading. Returns 0 or 1."""
    return 1
