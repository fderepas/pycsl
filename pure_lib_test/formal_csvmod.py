# Formal test for csv (csvmod) module
#
# Based on library_reference/csv.rst:
#   "Return a reader object which will iterate over lines in the given csvfile."
#   "Return a writer object... for writing... on the given file-like object."
#
# Tests verify contract postconditions:
#   - count_fields: result >= 0
#   - write_row: result >= num_fields
#   - writerows: result >= 0

from pure_lib.csvmod import count_fields, write_row, writerows


#@ ensures \result >= 0
def test_count_fields_nonneg() -> int:
    """count_fields always returns non-negative."""
    return count_fields(10)


#@ ensures \result >= 5
def test_write_row_bounded() -> int:
    """Writing 5 fields produces >= 5 bytes."""
    return write_row(5)


#@ ensures \result >= 0
def test_writerows_nonneg() -> int:
    """writerows result is non-negative."""
    return writerows(3, 4)
