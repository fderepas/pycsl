# pure_lib/csvmod — pure-Python csv module model
# Named 'csvmod' to avoid stdlib name clash.
#
# Contracts derived from library_reference/csv.rst.
# RST: "Return a reader object that will process lines from the given csvfile."
# RST: "Return a writer object responsible for converting data into
#  delimited strings."


#@ requires line >= 0
#@ ensures \result >= 0
#@ ensures line == 0 ==> \result == 0
#@ ensures line > 0 ==> \result >= 1
def count_fields(line: int) -> int:
    """RST: 'reader will process lines.' Empty line → 0 fields.
    Non-empty line has at least 1 field (even if no delimiter)."""
    if line == 0:
        return 0
    return 1


#@ requires num_fields >= 0
#@ ensures \result >= 0
#@ ensures \result >= num_fields
#@ ensures \result == num_fields
def write_row(num_fields: int) -> int:
    """RST: 'writer... converting data into delimited strings.'
    Written bytes >= field count (each field is at least 1 byte + delimiters)."""
    return num_fields


#@ requires data >= 0
#@ ensures \result >= 0
def reader_count(data: int) -> int:
    """Number of rows from parsing data. At least 0 rows."""
    return data


#@ requires dialect >= 0
#@ ensures \result >= 0
def get_dialect(dialect: int) -> int:
    """RST: 'Return the dialect associated with name.' Returns dialect id."""
    return dialect


#@ requires rows >= 0
#@ requires fields_per_row >= 0
#@ ensures \result >= 0
#@ ensures \result == rows * fields_per_row
def writerows(rows: int, fields_per_row: int) -> int:
    """RST: 'Write all elements in rows to the writer's file object.'
    Total bytes written is non-negative."""
    return rows * fields_per_row
