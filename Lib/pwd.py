"""PyCSL mock for Python's pwd module — The password database (getpwnam() and friends)."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def getpwuid(uid: int) -> int:
    """Mock: Return the password database entry for the given numeric user ID."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getpwnam(name: int) -> int:
    """Mock: Return the password database entry for the given user name."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getpwall() -> int:
    """Mock: Return a list of all available password database entries, in arbitrary order."""
    return 0
