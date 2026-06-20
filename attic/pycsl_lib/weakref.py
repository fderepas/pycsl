"""PyCSL mock for Python's weakref module — Support for weak references and weak dictionaries."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def proxy(object: int, callback: int) -> int:
    """Mock: Return a proxy to *object* which uses a weak reference.  This supports use of the proxy in most contexts instead of requ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getweakrefcount(object: int) -> int:
    """Mock: Return the number of weak references and proxies which refer to *object*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getweakrefs(object: int) -> int:
    """Mock: Return a list of all weak reference and proxy objects which refer to *object*."""
    return 0
