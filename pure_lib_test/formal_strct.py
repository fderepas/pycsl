# Formal test for struct (strct) module — universally quantified
#
# Based on library_reference/struct.rst:
#   "Return the size of the struct... described by the format string."
#   "Pack the values... according to the format string."
#   "Unpack from the buffer... according to the format string."

from pure_lib.strct import calcsize, pack, unpack


#@ requires fmt >= 0 and fmt < 2147483647
#@ ensures \result >= 0
#@ ensures \result == fmt
def test_calcsize_nonneg(fmt: int) -> int:
    """calcsize(fmt) == fmt for all fmt. Exact model identity."""
    return calcsize(fmt)


#@ requires fmt >= 0 and fmt < 2147483647
#@ requires val >= 0 and val < 2147483647
#@ ensures \result >= 0
#@ ensures \result == fmt
def test_pack_nonneg(fmt: int, val: int) -> int:
    """pack(fmt, val) == fmt for all inputs. Exact model identity."""
    return pack(fmt, val)


#@ requires fmt >= 0 and fmt < 2147483647
#@ requires data >= 0 and data < 2147483647
#@ ensures \result >= 0
#@ ensures \result == fmt
def test_unpack_nonneg(fmt: int, data: int) -> int:
    """unpack(fmt, data) == fmt for all inputs. Exact model identity."""
    return unpack(fmt, data)
