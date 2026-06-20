"""PyCSL mock for Python's tarfile module — Read and write tar-format archive files."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def open(name: int, mode: int, fileobj: int, bufsize: int) -> int:
    """Mock: Return a :class:`TarFile` object for the pathname *name*. For detailed information on :class:`TarFile` objects and the k..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def is_tarfile(name: int) -> int:
    """Mock: Return :const:`True` if *name* is a tar archive file, that the :mod:`!tarfile` module can read. *name* may be a :class:`..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fully_trusted_filter(member: int, path: int) -> int:
    """Mock: Return *member* unchanged. This implements the ``'fully_trusted'`` filter."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def tar_filter(member: int, path: int) -> int:
    """Mock: Mock: tar_filter"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def data_filter(member: int, path: int) -> int:
    """Mock: Mock: data_filter"""
    return 0
