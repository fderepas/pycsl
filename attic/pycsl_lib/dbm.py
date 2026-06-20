"""PyCSL mock for Python's dbm module — Interfaces to various Unix "database" formats."""
_ = 0  # anchor

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/dbm.html#dbm.whichdb
#@ ensures True
#@ assigns \nothing
def whichdb(filename: int) -> int:
    """Mock: This function attempts to guess which of the several simple database modules available --- :mod:`dbm.sqlite3`, :mod:`dbm..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/dbm.html#dbm.open
#@ requires mode >= 0
#@ ensures True
def open(file: int, flag: int, mode: int) -> int:
    """Mock: Open a database and return the corresponding database object. :param file: The database file to open. If the database fi..."""
    return 0
