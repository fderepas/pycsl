"""PyCSL mock for Python's gzip module — Interfaces for gzip compression and decompression using file objects."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def open(filename: int, mode: int, compresslevel: int, encoding: int, errors: int, newline: int) -> int:
    """Mock: Open a gzip-compressed file in binary or text mode, returning a :term:`file object`. The *filename* argument can be an a..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def compress(data: int, compresslevel: int, mtime: int) -> int:
    """Mock: Compress the *data*, returning a :class:`bytes` object containing the compressed data.  *compresslevel* and *mtime* have..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def decompress(data: int) -> int:
    """Mock: Decompress the *data*, returning a :class:`bytes` object containing the uncompressed data. This function is capable of d..."""
    return 0
