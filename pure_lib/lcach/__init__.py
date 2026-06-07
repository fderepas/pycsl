# Pure model for linecache — random access to text lines
# Models as line-count based access.


#@ requires lineno >= 1
#@ ensures \result >= 0
def getline(lineno: int) -> int:
    """Get line from file/cache. Returns line length."""
    return 0


#@ requires lineno >= 1
#@ ensures \result >= 0
def checkcache(lineno: int) -> int:
    """Check and update cache. Returns 0 on success."""
    return 0


#@ ensures \result >= 0
def clearcache() -> int:
    """Clear the cache. Returns 0."""
    return 0


#@ requires size >= 0
#@ ensures \result >= 0
#@ ensures \result <= size
def getlines(size: int) -> int:
    """Get all lines (up to size). Returns count."""
    return size
