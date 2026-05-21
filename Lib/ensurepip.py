"""PyCSL mock for Python's ensurepip module — Bootstrapping the "pip" installer into an existing Python."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def version() -> int:
    """Mock: Returns a string specifying the available version of pip that will be installed when bootstrapping an environment."""
    return 0

#@ \trusted
#@ ensures \result == 0
def bootstrap(root: int, upgrade: int, user: int, __altinstall: int, default_pip: int, __verbosity: int) -> int:
    """Mock: Bootstraps ``pip`` into the current or designated environment. *root* specifies an alternative root directory to install..."""
    return 0
