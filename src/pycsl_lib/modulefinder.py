"""PyCSL mock for Python's modulefinder module — Find modules used by a script."""
_ = 0  # anchor

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/modulefinder.py
#@ requires True
#@ ensures True
def AddPackagePath(pkg_name: int, path: int) -> int:
    """Mock: Record that the package named *pkg_name* can be found in the specified *path*."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/modulefinder.html#modulefinder.ReplacePackage
#@ requires True
#@ ensures True
def ReplacePackage(oldname: int, newname: int) -> int:
    """Mock: Allows specifying that the module named *oldname* is in fact the package named *newname*."""
    return 0
