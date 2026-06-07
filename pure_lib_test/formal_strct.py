# Formal test for struct (strct) module — universally quantified
#
# Based on library_reference/struct.rst:
#   "Return the size of the struct... described by the format string."
#   "Pack the values... according to the format string."
#   "Unpack from the buffer... according to the format string."

from pure_lib.strct import calcsize, pack, unpack


#@ requires fmt >= 0 and fmt < 2147483647
#@ ensures \result >= 0
def test_calcsize_nonneg(fmt: int) -> int:
    """calcsize(fmt) >= 0 for all format sizes. Always non-negative."""
    return calcsize(fmt)


#@ requires fmt >= 0 and fmt < 2147483647
#@ requires val >= 0 and val < 2147483647
#@ ensures \result >= 0
def test_pack_nonneg(fmt: int, val: int) -> int:
    """pack(fmt, val) >= 0 for all inputs. Bytes length non-negative."""
    return pack(fmt, val)


#@ requires fmt >= 0 and fmt < 2147483647
#@ requires data >= 0 and data < 2147483647
#@ ensures \result >= 0
def test_unpack_nonneg(fmt: int, data: int) -> int:
    """unpack(fmt, data) >= 0 for all inputs. Tuple length non-negative."""
    return unpack(fmt, data)
