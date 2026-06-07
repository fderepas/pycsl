# pure_lib/csvmod — pure-Python csv module model
# Named 'csvmod' to avoid stdlib name clash.
#
# Contracts derived from library_reference/csv.rst.
# RST: "Return a reader object that will process lines from the given csvfile."
# RST: "Return a writer object responsible for converting data into
#  delimited strings."
# RST: "DictReader maps rows to dicts, DictWriter writes dicts to rows."


#@ requires line >= 0
#@ ensures \result >= 0
#@ ensures line == 0 ==> \result == 0
#@ ensures line > 0 ==> \result >= 1
def count_fields(line: int) -> int:
    """RST: 'reader will process lines.' Empty line -> 0 fields.
    Non-empty line has at least 1 field (even if no delimiter)."""
    if line == 0:
        return 0
    return 1


#@ requires num_fields >= 0
#@ ensures \result >= 0
#@ ensures \result == num_fields
def write_row(num_fields: int) -> int:
    """RST: 'writer... converting data into delimited strings.'
    Written bytes >= field count."""
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


# --- CSVReader class ---

""  # pycsl
#@ class invariant self._field_count >= 0
#@ class invariant self._rows_read >= 0
class CSVReader:
    """RST: 'Return a reader object that will process lines from csvfile.'"""

    def __init__(self):
        self._field_count = 0
        self._rows_read = 0

    #@ requires fields >= 0
    #@ ensures self._field_count == fields
    #@ assigns self._field_count
    def set_field_count(self, fields: int) -> None:
        """Configure number of fields per row."""
        self._field_count = fields

    #@ ensures \result == self._field_count
    #@ ensures self._rows_read == \old(self._rows_read) + 1
    #@ assigns self._rows_read
    def next_row(self) -> int:
        """RST: 'Return the next row of the reader's iterable object as a list.'
        Returns number of fields read."""
        self._rows_read = self._rows_read + 1
        return self._field_count

    #@ ensures \result == self._rows_read
    #@ assigns \nothing
    def line_num(self) -> int:
        """RST: 'The number of lines read from the source iterator.'"""
        return self._rows_read


# --- CSVWriter class ---

""  # pycsl
#@ class invariant self._rows_written >= 0
#@ class invariant self._field_count >= 0
class CSVWriter:
    """RST: 'Return a writer object responsible for converting data.'"""

    def __init__(self):
        self._rows_written = 0
        self._field_count = 0

    #@ requires fields >= 0
    #@ ensures self._field_count == fields
    #@ assigns self._field_count
    def set_field_count(self, fields: int) -> None:
        """Configure expected fields per row."""
        self._field_count = fields

    #@ ensures self._rows_written == \old(self._rows_written) + 1
    #@ ensures \result == self._field_count
    #@ assigns self._rows_written
    def writerow(self) -> int:
        """RST: 'Write the row parameter to the writer's file object.'
        Returns number of fields written."""
        self._rows_written = self._rows_written + 1
        return self._field_count

    #@ ensures \result == self._rows_written
    #@ assigns \nothing
    def rows_written(self) -> int:
        """Total rows written so far."""
        return self._rows_written
