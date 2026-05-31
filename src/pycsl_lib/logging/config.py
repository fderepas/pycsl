"""PyCSL mock for Python's logging.config module — Configuration of the logging module."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def dictConfig(config: int) -> int:
    """Mock: Takes the logging configuration from a dictionary.  The contents of this dictionary are described in :ref:`logging-confi..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fileConfig(fname: int, defaults: int, disable_existing_loggers: int, encoding: int) -> int:
    """Mock: Reads the logging configuration from a :mod:`configparser`\-format file. The format of the file should be as described i..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def listen(port: int, verify: int) -> int:
    """Mock: Starts up a socket server on the specified port, and listens for new configurations. If no port is specified, the module..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def stopListening() -> int:
    """Mock: Stops the listening server which was created with a call to :func:`listen`. This is typically called before calling :met..."""
    return 0
