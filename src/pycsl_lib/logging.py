"""PyCSL mock for Python's logging module — Flexible event logging system for applications."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def getLogger(name: int) -> int:
    """Mock: Return a logger with the specified name or, if name is ``None``, return the root logger of the hierarchy. If specified, ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getLoggerClass() -> int:
    """Mock: Return either the standard :class:`Logger` class, or the last class passed to :func:`setLoggerClass`. This function may ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getLogRecordFactory() -> int:
    """Mock: Return a callable which is used to create a :class:`LogRecord`. .. versionadded:: 3.2 This function has been provided, a..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def debug(msg: int) -> int:
    """Mock: This is a convenience function that calls :meth:`Logger.debug`, on the root logger. The handling of the arguments is in ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def info(msg: int) -> int:
    """Mock: Logs a message with level :const:`INFO` on the root logger. The arguments and behavior are otherwise the same as for :fu..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def warning(msg: int) -> int:
    """Mock: Logs a message with level :const:`WARNING` on the root logger. The arguments and behavior are otherwise the same as for ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def error(msg: int) -> int:
    """Mock: Logs a message with level :const:`ERROR` on the root logger. The arguments and behavior are otherwise the same as for :f..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def critical(msg: int) -> int:
    """Mock: Logs a message with level :const:`CRITICAL` on the root logger. The arguments and behavior are otherwise the same as for..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def exception(msg: int) -> int:
    """Mock: Logs a message with level :const:`ERROR` on the root logger. The arguments and behavior are otherwise the same as for :f..."""
    return 0

#@ \trusted
#@ requires level >= 0
#@ ensures \result >= 0
def log(level: int, msg: int) -> int:
    """Mock: Logs a message with level *level* on the root logger. The arguments and behavior are otherwise the same as for :func:`de..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def disable(level: int) -> int:
    """Mock: Provides an overriding level *level* for all loggers which takes precedence over the logger's own level. When the need a..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def addLevelName(level: int, levelName: int) -> int:
    """Mock: Associates level *level* with text *levelName* in an internal dictionary, which is used to map numeric levels to a textu..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getLevelNamesMapping() -> int:
    """Mock: Returns a mapping from level names to their corresponding logging levels. For example, the string 'CRITICAL' maps to :co..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getLevelName(level: int) -> int:
    """Mock: Returns the textual or numeric representation of logging level *level*. If *level* is one of the predefined levels :cons..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getHandlerByName(name: int) -> int:
    """Mock: Returns a handler with the specified *name*, or ``None`` if there is no handler with that name. .. versionadded:: 3.12"""
    return 0

#@ \trusted
#@ ensures \result == 0
def getHandlerNames() -> int:
    """Mock: Returns an immutable set of all known handler names. .. versionadded:: 3.12"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def makeLogRecord(attrdict: int) -> int:
    """Mock: Creates and returns a new :class:`LogRecord` instance whose attributes are defined by *attrdict*. This function is usefu..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def basicConfig() -> int:
    """Mock: Does basic configuration for the logging system by either creating a :class:`StreamHandler` with a default :class:`Forma..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def shutdown() -> int:
    """Mock: Informs the logging system to perform an orderly shutdown by flushing and closing all handlers. This should be called at..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def setLoggerClass(klass: int) -> int:
    """Mock: Tells the logging system to use the class *klass* when instantiating a logger. The class should define :meth:`!__init__`..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def setLogRecordFactory(factory: int) -> int:
    """Mock: Set a callable which is used to create a :class:`LogRecord`. :param factory: The factory callable to be used to instanti..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def captureWarnings(capture: int) -> int:
    """Mock: This function is used to turn the capture of warnings by logging on and off. If *capture* is ``True``, warnings issued b..."""
    return 0
