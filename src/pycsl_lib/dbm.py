"""PyCSL mock for Python's dbm module — Interfaces to various Unix "database" formats."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def whichdb(filename: int) -> int:
    """Mock: This function attempts to guess which of the several simple database modules available --- :mod:`dbm.sqlite3`, :mod:`dbm..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def open(file: int, flag: int, mode: int) -> int:
    """Mock: Open a database and return the corresponding database object. :param file: The database file to open. If the database fi..."""
    return 0
