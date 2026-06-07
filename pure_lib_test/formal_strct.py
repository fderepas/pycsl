# Formal test for struct (strct) module
#
# Based on library_reference/struct.rst:
#   "Return the size of the struct... described by the format string."
#   "Pack the values... according to the format string."
#   "Unpack from the buffer... according to the format string."
#
# Tests:
#   1. calcsize is non-negative
#   2. pack result is non-negative
#   3. unpack result is non-negative

from pure_lib.strct import calcsize, pack, unpack


#@ ensures \result >= 0
def test_calcsize_nonneg() -> int:
    """calcsize always returns non-negative."""
    return calcsize(8)


#@ ensures \result >= 0
def test_pack_nonneg() -> int:
    """pack result (bytes length) is non-negative."""
    return pack(4, 255)


#@ ensures \result >= 0
def test_unpack_nonneg() -> int:
    """unpack result (tuple length) is non-negative."""
    return unpack(2, 8)
