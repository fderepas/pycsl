"""PyCSL mock for Python's warnings module — Issue warning messages and control their disposition."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def warn(message: int, category: int, stacklevel: int, source: int, skip_file_prefixes: int) -> int:
    """Mock: Issue a warning, or maybe ignore it or raise an exception.  The *category* argument, if given, must be a :ref:`warning c..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def warn_explicit(message: int, category: int, filename: int, lineno: int, module_: int, registry: int, module_globals: int) -> int:
    """Mock: This is a low-level interface to the functionality of :func:`warn`, passing in explicitly the message, category, filenam..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def showwarning(message: int, category: int, filename: int, lineno: int, file: int, line: int) -> int:
    """Mock: Write a warning to a file.  The default implementation calls ``formatwarning(message, category, filename, lineno, line)`..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def formatwarning(message: int, category: int, filename: int, lineno: int, line: int) -> int:
    """Mock: Format a warning the standard way.  This returns a string which may contain embedded newlines and ends in a newline.  *l..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def filterwarnings(action: int, message: int, category: int, module_: int, lineno: int, append: int) -> int:
    """Mock: Insert an entry into the list of :ref:`warnings filter specifications <warning-filter>`.  The entry is inserted at the f..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def simplefilter(action: int, category: int, lineno: int, append: int) -> int:
    """Mock: Insert a simple entry into the list of :ref:`warnings filter specifications <warning-filter>`.  The meaning of the funct..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def resetwarnings() -> int:
    """Mock: Reset the warnings filter.  This discards the effect of all previous calls to :func:`filterwarnings`, including that of ..."""
    return 0
