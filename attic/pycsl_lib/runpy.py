"""PyCSL mock for Python's runpy module — Locate and run Python modules without importing them first."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def run_module(mod_name: int, init_globals: int, run_name: int, alter_sys: int) -> int:
    """Mock: .. index:: pair: module; __main__ Execute the code of the specified module and return the resulting module's globals dic..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def run_path(path_name: int, init_globals: int, run_name: int) -> int:
    """Mock: .. index:: pair: module; __main__ Execute the code at the named filesystem location and return the resulting module's gl..."""
    return 0
