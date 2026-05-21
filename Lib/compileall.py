"""PyCSL mock for Python's compileall module — Tools for byte-compiling all Python source files in a directory tree."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def compile_dir(dir: int, maxlevels: int, ddir: int, force: int, rx: int, quiet: int, legacy: int) -> int:
    """Mock: Recursively descend the directory tree named by *dir*, compiling all :file:`.py` files along the way. Return a true valu..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def compile_file(fullname: int, ddir: int, force: int, rx: int, quiet: int, legacy: int, optimize: int) -> int:
    """Mock: Compile the file with path *fullname*. Return a true value if the file compiled successfully, and a false value otherwis..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def compile_path(skip_curdir: int, maxlevels: int, force: int, quiet: int, legacy: int, optimize: int, invalidation_mode: int) -> int:
    """Mock: Byte-compile all the :file:`.py` files found along ``sys.path``. Return a true value if all the files compiled successfu..."""
    return 0
