"""PyCSL mock for Python's modulefinder module — Find modules used by a script."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def AddPackagePath(pkg_name: int, path: int) -> int:
    """Mock: Record that the package named *pkg_name* can be found in the specified *path*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ReplacePackage(oldname: int, newname: int) -> int:
    """Mock: Allows specifying that the module named *oldname* is in fact the package named *newname*."""
    return 0
