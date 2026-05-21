"""PyCSL mock for Python's lzma module — A Python wrapper for the liblzma compression library."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def open(filename: int, mode: int, format: int, check_: int, preset: int, filters: int, encoding: int) -> int:
    """Mock: Open an LZMA-compressed file in binary or text mode, returning a :term:`file object`. The *filename* argument can be eit..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def compress(data: int, format: int, check_: int, preset: int, filters: int) -> int:
    """Mock: Compress *data* (a :class:`bytes` object), returning the compressed data as a :class:`bytes` object. See :class:`LZMACom..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def decompress(data: int, format: int, memlimit: int, filters: int) -> int:
    """Mock: Decompress *data* (a :class:`bytes` object), returning the uncompressed data as a :class:`bytes` object. If *data* is th..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def is_check_supported(check_: int) -> int:
    """Mock: Return ``True`` if the given integrity check is supported on this system. :const:`CHECK_NONE` and :const:`CHECK_CRC32` a..."""
    return 0
