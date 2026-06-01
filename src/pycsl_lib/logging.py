"""PyCSL mock for Python's logging module — Flexible event logging system for applications."""
_ = 0  # anchor

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/logging.html#logging.getLogger
#@ ensures \result >= 0
def getLogger(name: int) -> int:
    """Mock: Return a logger with the specified name or, if name is ``None``, return the root logger of the hierarchy. If specified, ..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/logging.html#logging.getLoggerClass
#@ ensures True
def getLoggerClass() -> int:
    """Mock: Return either the standard :class:`Logger` class, or the last class passed to :func:`setLoggerClass`. This function may ..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/logging.html#logging.getLogRecordFactory
#@ ensures True
def getLogRecordFactory() -> int:
    """Mock: Return a callable which is used to create a :class:`LogRecord`. .. versionadded:: 3.2 This function has been provided, a..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/logging.html#logging.debug
#@ ensures True
def debug(msg: int) -> int:
    """Mock: This is a convenience function that calls :meth:`Logger.debug`, on the root logger. The handling of the arguments is in ..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/logging.html#logging.info
#@ ensures True
def info(msg: int) -> int:
    """Mock: Logs a message with level :const:`INFO` on the root logger. The arguments and behavior are otherwise the same as for :fu..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/logging.html#logging.warning
#@ ensures True
def warning(msg: int) -> int:
    """Mock: Logs a message with level :const:`WARNING` on the root logger. The arguments and behavior are otherwise the same as for ..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/logging.html#logging.error
#@ ensures True
def error(msg: int) -> int:
    """Mock: Logs a message with level :const:`ERROR` on the root logger. The arguments and behavior are otherwise the same as for :f..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/logging.html#logging.critical
#@ ensures True
def critical(msg: int) -> int:
    """Mock: Logs a message with level :const:`CRITICAL` on the root logger. The arguments and behavior are otherwise the same as for..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/logging.html#logging.Logger.exception
#@ ensures True
#@ assigns \nothing
def exception(msg: int) -> int:
    """Mock: Logs a message with level :const:`ERROR` on the root logger. The arguments and behavior are otherwise the same as for :f..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/logging.html#logging.LoggerAdapter.log
#@ requires level >= 0
#@ ensures True
def log(level: int, msg: int) -> int:
    """Mock: Logs a message with level *level* on the root logger. The arguments and behavior are otherwise the same as for :func:`de..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/logging.html#logging.disable
#@ requires level >= 0
#@ ensures True
def disable(level: int) -> int:
    """Mock: Provides an overriding level *level* for all loggers which takes precedence over the logger's own level. When the need a..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/logging.html#logging.addLevelName
#@ ensures True
#@ assigns \nothing
def addLevelName(level: int, levelName: int) -> int:
    """Mock: Associates level *level* with text *levelName* in an internal dictionary, which is used to map numeric levels to a textu..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/logging/__init__.py
#@ requires True
#@ ensures True
def getLevelNamesMapping() -> int:
    """Mock: Returns a mapping from level names to their corresponding logging levels. For example, the string 'CRITICAL' maps to :co..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/logging.html#logging.getLevelName
#@ ensures True
def getLevelName(level: int) -> int:
    """Mock: Returns the textual or numeric representation of logging level *level*. If *level* is one of the predefined levels :cons..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/logging.html#logging.getHandlerByName
#@ ensures True
def getHandlerByName(name: int) -> int:
    """Mock: Returns a handler with the specified *name*, or ``None`` if there is no handler with that name. .. versionadded:: 3.12"""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/logging.html#logging.getHandlerNames
#@ ensures True
def getHandlerNames() -> int:
    """Mock: Returns an immutable set of all known handler names. .. versionadded:: 3.12"""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/logging.html#logging.makeLogRecord
#@ ensures \result >= 0
def makeLogRecord(attrdict: int) -> int:
    """Mock: Creates and returns a new :class:`LogRecord` instance whose attributes are defined by *attrdict*. This function is usefu..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/logging.html#logging.basicConfig
#@ ensures \result == 0
def basicConfig() -> int:
    """Mock: Does basic configuration for the logging system by either creating a :class:`StreamHandler` with a default :class:`Forma..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/logging.html#logging.shutdown
#@ ensures True
#@ assigns \nothing
def shutdown() -> int:
    """Mock: Informs the logging system to perform an orderly shutdown by flushing and closing all handlers. This should be called at..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/logging.html#logging.setLoggerClass
#@ ensures True
def setLoggerClass(klass: int) -> int:
    """Mock: Tells the logging system to use the class *klass* when instantiating a logger. The class should define :meth:`!__init__`..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/logging.html#logging.setLogRecordFactory
#@ requires factory != 0
#@ ensures True
def setLogRecordFactory(factory: int) -> int:
    """Mock: Set a callable which is used to create a :class:`LogRecord`. :param factory: The factory callable to be used to instanti..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/logging.html#logging.captureWarnings
#@ ensures True
def captureWarnings(capture: int) -> int:
    """Mock: This function is used to turn the capture of warnings by logging on and off. If *capture* is ``True``, warnings issued b..."""
    return 0
