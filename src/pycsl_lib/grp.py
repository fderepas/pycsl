"""PyCSL mock for Python's grp module — The group database (getgrnam() and friends)."""
_ = 0  # anchor

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/grp.html#grp.getgrgid
#@ requires id >= 0
#@ ensures True
def getgrgid(id: int) -> int:
    """Mock: Return the group database entry for the given numeric group ID. :exc:`KeyError` is raised if the entry asked for cannot ..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/grp.html#grp.getgrnam
#@ requires name != ""
#@ ensures \result >= 0
def getgrnam(name: int) -> int:
    """Mock: Return the group database entry for the given group name. :exc:`KeyError` is raised if the entry asked for cannot be fou..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/grp.html#grp.getgrall
#@ ensures True
def getgrall() -> int:
    """Mock: Return a list of all available group entries, in arbitrary order."""
    return 0
