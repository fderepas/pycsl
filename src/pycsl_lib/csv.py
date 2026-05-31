"""PyCSL mock for Python's csv module.

Provides trusted stubs for CSV reading and writing.
DictReader and DictWriter modelled as classes.
"""
_ = 0  # anchor

# ── Constants ──

QUOTE_ALL = 0
QUOTE_MINIMAL = 0
QUOTE_NONNUMERIC = 0
QUOTE_NONE = 0
QUOTE_NOTNULL = 0
QUOTE_STRINGS = 0

# ── DictReaderObj class ─────────────────────────────────────────────

""  # pycsl
#@ class invariant self._line_num >= 0
class DictReaderObj:
    def __init__(self):
        self._line_num = 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/csv.html#csv.reader
#@ requires True
#@ ensures True
#@ assigns self._line_num
    def next_row(self) -> int:
        self._line_num += 1
        return self._line_num

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._line_num
    #@ assigns \nothing
    def line_num(self) -> int:
        return self._line_num

#@ \trusted reviewer: python-stdlib
# cite: cpython/Lib/csv.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def fieldnames(self) -> int:
        return 0

# ── DictWriterObj class ─────────────────────────────────────────────

#@ class invariant self._rows_written >= 0
class DictWriterObj:
    def __init__(self):
        self._rows_written = 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures self._rows_written == \old(self._rows_written) + 1
    #@ assigns self._rows_written
    def writerow(self, row: int) -> int:
        self._rows_written += 1
        return self._rows_written

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/csv.html#csv.writer.writerows
#@ requires True
#@ ensures True
#@ assigns self._rows_written
    def writerows(self, rows: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/csv.html#csv.DictWriter.writeheader
#@ ensures True
#@ assigns self._rows_written
    def writeheader(self) -> int:
        return 0

# ── SnifferObj class ────────────────────────────────────────────────

#@ class invariant self._ready >= 0
class SnifferObj:
    def __init__(self):
        self._ready = 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/csv.html#csv.Sniffer.sniff
#@ ensures True
#@ assigns \nothing
    def sniff(self, sample: int, delimiters: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/csv.html#csv.Sniffer.has_header
#@ requires True
#@ ensures True
#@ assigns \nothing
    def has_header(self, sample: int) -> int:
        return 0

# ── Module-level functions ──────────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/csv.html#csv.reader
#@ requires csvfile >= 0
#@ ensures \result >= 0
def reader(csvfile: int, dialect: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/csv.html#csv.writer
#@ requires csvfile >= 0
#@ ensures \result >= 0
def writer(csvfile: int, dialect: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/csv.html#csv.register_dialect
#@ requires name != ""
#@ ensures True
def register_dialect(name: int, dialect: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/csv.html#csv.unregister_dialect
#@ ensures True
def unregister_dialect(name: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/csv.html#csv.get_dialect
#@ ensures True
def get_dialect(name: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/csv.html#csv.list_dialects
#@ ensures True
#@ assigns \nothing
def list_dialects() -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/csv.html#csv.field_size_limit
#@ requires new_limit >= 0
#@ ensures \result >= 0
def field_size_limit(new_limit: int) -> int:
    return 0
