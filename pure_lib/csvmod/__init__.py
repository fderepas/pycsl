# pure_lib/csvmod — pure-Python csv module model
# Named 'csvmod' to avoid stdlib name clash.
#
# Models csv reader/writer as producers/consumers of field counts.
# Contract-only: real parsing is in C (_csv).


#@ requires line >= 0
#@ ensures \result >= 0
def count_fields(line: int) -> int:
    """Count fields in a CSV line (delimiter-separated).
    Model: at least 1 field per non-empty line."""
    if line == 0:
        return 0
    return 1


#@ requires num_fields >= 0
#@ ensures \result >= 0
#@ ensures \result >= num_fields
def write_row(num_fields: int) -> int:
    """Write a row with num_fields. Returns bytes written (>= field count)."""
    return num_fields


#@ requires data >= 0
#@ ensures \result >= 0
def reader_count(data: int) -> int:
    """Number of rows from parsing data of length data.
    Model: at least 0 rows."""
    return data


#@ requires dialect >= 0
#@ ensures \result >= 0
def get_dialect(dialect: int) -> int:
    """Get a dialect by name. Returns dialect id."""
    return dialect


#@ requires rows >= 0
#@ requires fields_per_row >= 0
#@ ensures \result >= 0
def writerows(rows: int, fields_per_row: int) -> int:
    """Write multiple rows. Returns total bytes written."""
    return rows * fields_per_row
