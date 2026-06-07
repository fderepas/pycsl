# Formal test for csv (csvmod) module
#
# Based on library_reference/csv.rst:
#   "Return a reader object that will process lines."
#   → empty line has 0 fields; non-empty line has >= 1 field.
#   "Return a writer object responsible for converting data."
#   → writing N fields produces >= N bytes.

from pure_lib.csvmod import count_fields, write_row, writerows


#@ ensures \result == 0
def test_count_fields_empty() -> int:
    """Empty line → 0 fields. Direct from data format semantics."""
    return count_fields(0)


#@ ensures \result >= 1
def test_count_fields_nonempty() -> int:
    """Non-empty line → at least 1 field (even without delimiter)."""
    return count_fields(10)


#@ ensures \result >= 5
def test_write_row_bounded() -> int:
    """Writing 5 fields produces >= 5 bytes."""
    return write_row(5)


#@ ensures \result >= 0
def test_writerows_nonneg() -> int:
    """writerows result is non-negative."""
    return writerows(3, 4)
