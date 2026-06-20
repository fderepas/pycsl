# Formal tests for pycsl_lib/csvmod — CSV module model
from pycsl_lib.csvmod import count_fields, write_row, writerows


#@ requires line >= 0
#@ ensures line == 0 ==> \result == 0
#@ ensures line > 0 ==> \result >= 1
def test_count_fields_spec(line: int) -> int:
    """Empty line -> 0 fields, non-empty -> at least 1."""
    return count_fields(line)


#@ requires n >= 0
#@ ensures \result == n
def test_write_row_identity(n: int) -> int:
    """write_row returns field count."""
    return write_row(n)


#@ requires rows >= 0
#@ requires fpr >= 0
#@ ensures \result == rows * fpr
def test_writerows_product(rows: int, fpr: int) -> int:
    """writerows returns rows * fields_per_row."""
    return writerows(rows, fpr)
