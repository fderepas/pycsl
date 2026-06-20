# pycsl_lib/insp — formal model for inspect (introspection utilities)
#
# Models key functions from CPython's inspect module. Object handles are
# represented as non-negative ints. String-returning functions use str.


#@ requires func >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def unwrap(func: int) -> int:
    """RST: 'Get the object wrapped by func.'
    Follows __wrapped__ chain. Returns the innermost function."""
    return func


#@ requires func >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def signature(func: int) -> int:
    """RST: 'Return a Signature object for the given callable.'
    Returns a signature handle."""
    return 0


#@ assigns \nothing
def cleandoc(doc: str) -> str:
    """RST: 'Clean up indentation from docstrings.'
    Returns the cleaned string."""
    return doc


#@ requires obj >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def getfile(obj: int) -> int:
    """RST: 'Return the name of the file in which an object was defined.'
    Returns filename length."""
    return 1


#@ requires obj >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def getdoc(obj: int) -> int:
    """RST: 'Get the documentation string for an object.'
    Returns docstring length (0 if none)."""
    return 0


#@ requires obj >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def getsource(obj: int) -> int:
    """RST: 'Return the text of the source code for an object.'
    Returns source length."""
    return 1


#@ requires obj >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def getsourcelines(obj: int) -> int:
    """RST: 'Return source lines and starting line number for an object.'
    Returns line count."""
    return 1


#@ requires obj >= 0
#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def isfunction(obj: int) -> int:
    """RST: 'Return True if the object is a Python function.'"""
    return 0


#@ requires obj >= 0
#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def isclass(obj: int) -> int:
    """RST: 'Return True if the object is a class.'"""
    return 0


#@ requires obj >= 0
#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def ismethod(obj: int) -> int:
    """RST: 'Return True if the object is a bound method.'"""
    return 0


#@ requires obj >= 0
#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def ismodule(obj: int) -> int:
    """RST: 'Return True if the object is a module.'"""
    return 0


#@ requires frame >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def getlineno(frame: int) -> int:
    """RST: 'Return the line number of the current line in frame.'"""
    return 1
