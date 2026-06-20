"""PyCSL mock for Python's site module — Module responsible for site-specific configuration."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def main() -> int:
    """Mock: Adds all the standard site-specific directories to the module search path.  This function is called automatically when t..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def addsitedir(sitedir: int, known_paths: int, defer_processing_start_files: int) -> int:
    """Mock: Add a directory to sys.path and parse the :file:`.pth` and :file:`.start` files found in that directory.  Typically used..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getsitepackages() -> int:
    """Mock: Return a list containing all global site-packages directories. .. versionadded:: 3.2"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getuserbase() -> int:
    """Mock: Return the path of the user base directory, :data:`USER_BASE`.  If it is not initialized yet, this function will also se..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getusersitepackages() -> int:
    """Mock: Return the path of the user-specific site-packages directory, :data:`USER_SITE`.  If it is not initialized yet, this fun..."""
    return 0
