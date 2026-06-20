# Formal tests for pycsl_lib/strct — struct module model
from pycsl_lib.strct import calcsize, pack, unpack, unpack_from, iter_unpack


#@ requires fmt >= 0
#@ ensures \result >= 0
#@ ensures \result == fmt
def test_calcsize_identity(fmt: int) -> int:
    """calcsize returns the format size itself."""
    return calcsize(fmt)


#@ requires fmt >= 0
#@ requires \length(buf) >= fmt
#@ ensures \result == fmt
def test_pack_returns_size(fmt: int, buf: list, val: int) -> int:
    """pack returns number of bytes = calcsize."""
    return pack(fmt, buf, val)


#@ requires fmt >= 0
#@ requires \length(buf) >= fmt
#@ ensures \result == fmt
def test_unpack_returns_size(fmt: int, buf: list) -> int:
    """unpack returns number of values = calcsize."""
    return unpack(fmt, buf)


#@ requires fmt >= 0
#@ requires offset >= 0
#@ requires \length(buf) >= offset + fmt
#@ ensures \result == fmt
def test_unpack_from_returns_size(fmt: int, buf: list, offset: int) -> int:
    """unpack_from returns number of values = calcsize."""
    return unpack_from(fmt, buf, offset)


#@ requires fmt > 0
#@ requires \length(buf) >= fmt
#@ ensures \result >= 0
def test_iter_unpack_nonneg(fmt: int, buf: list) -> int:
    """iter_unpack returns non-negative iteration count."""
    return iter_unpack(fmt, buf)
