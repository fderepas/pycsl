# Formal tests for pycsl_lib/csvmod — CSV module model
from pycsl_lib.csvmod import count_fields, write_row, writerows


#@ requires line >= 0
#@ ensures line == 0 ==> \result == 0
#@ ensures line > 0 ==> \result >= 1
def test_count_fields_spec(line: int) -> int:
    """Empty line -> 0 fields, non-empty -> at least 1."""
    return count_fields(line)


# (#49) gen #30: RENAMED from `test_write_row_identity`, which PROVED `\result == n` for
# the field count of a written row — a claim CPython contradicts (`writerow` returns the
# CHARACTER count, 7 for 3 fields). This driver is the downstream half of that defect: the
# false contract was not merely written in the model, it was PROVED here.
#@ requires n >= 0
#@ ensures \result >= n
def test_write_row_at_least_fields(n: int) -> int:
    """write_row returns the byte count, which is at least the field count."""
    return write_row(n)


# (#49) gen #30: was `ensures \result == rows * fpr`. Real `writerows` returns None, so
# the exact product was wrong in both quantity and value.
#@ requires rows >= 0
#@ requires fpr >= 0
#@ ensures \result >= rows * fpr
def test_writerows_at_least_product(rows: int, fpr: int) -> int:
    """writerows returns the byte count, at least one per field."""
    return writerows(rows, fpr)
