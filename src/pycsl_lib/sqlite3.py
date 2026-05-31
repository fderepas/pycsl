"""PyCSL mock for Python's sqlite3 module — A DB-API 2.0 implementation using SQLite 3.x."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def connect(database: int, timeout: int, detect_types: int, __isolation_level: int, check_same_thread: int, __factory: int, cached_statements: int) -> int:
    """Mock: Open a connection to an SQLite database. :param database: The path to the database file to be opened. You can pass ``':m..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def complete_statement(statement: int) -> int:
    """Mock: Return ``True`` if the string *statement* appears to contain one or more complete SQL statements. No syntactic verificat..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def enable_callback_tracebacks(flag: int) -> int:
    """Mock: Enable or disable callback tracebacks. By default you will not get any tracebacks in user-defined functions, aggregates,..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def register_adapter(type_: int, adapter: int) -> int:
    """Mock: Register an *adapter* :term:`callable` to adapt the Python type *type* into an SQLite type. The adapter is called with a..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def register_converter(typename: int, converter: int) -> int:
    """Mock: Register the *converter* :term:`callable` to convert SQLite objects of type *typename* into a Python object of a specifi..."""
    return 0
