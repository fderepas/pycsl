# Formal test for csv (csvmod) module — universally quantified
#
# Based on library_reference/csv.rst:
#   "Return a reader object that will process lines."
#   → empty line has 0 fields; non-empty line has >= 1 field.
#   "Return a writer object responsible for converting data."
#   → writing N fields produces >= N bytes.

from pure_lib.csvmod import count_fields, write_row, writerows


#@ ensures \result == 0
def test_count_fields_empty() -> int:
    """count_fields(0) == 0. Empty line → 0 fields. (Only one input: 0.)"""
    return count_fields(0)


#@ requires line > 0 and line < 2147483647
#@ ensures \result >= 1
def test_count_fields_nonempty(line: int) -> int:
    """count_fields(line) >= 1 for all line > 0. Non-empty → at least 1 field."""
    return count_fields(line)


#@ requires num_fields >= 0 and num_fields < 2147483647
#@ ensures \result >= num_fields
def test_write_row_bounded(num_fields: int) -> int:
    """write_row(num_fields) >= num_fields for all inputs."""
    return write_row(num_fields)


#@ requires rows >= 0 and rows < 2147483647
#@ requires fields_per_row >= 0 and fields_per_row < 2147483647
#@ ensures \result >= 0
def test_writerows_nonneg(rows: int, fields_per_row: int) -> int:
    """writerows(rows, fields_per_row) >= 0 for all inputs."""
    return writerows(rows, fields_per_row)
