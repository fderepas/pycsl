"""PyCSL mock for Python's tokenize module — Lexical scanner for Python source code."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def tokenize(readline: int) -> int:
    """Mock: The :func:`.tokenize` generator requires one argument, *readline*, which must be a callable object which provides the sa..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def generate_tokens(readline: int) -> int:
    """Mock: Tokenize a source reading unicode strings instead of bytes. Like :func:`.tokenize`, the *readline* argument is a callabl..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def untokenize(iterable: int) -> int:
    """Mock: Converts tokens back into Python source code.  The *iterable* must return sequences with at least two elements, the toke..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def detect_encoding(readline: int) -> int:
    """Mock: The :func:`detect_encoding` function is used to detect the encoding that should be used to decode a Python source file. ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def open(filename: int) -> int:
    """Mock: Open a file in read only mode using the encoding detected by :func:`detect_encoding`. .. versionadded:: 3.2"""
    return 0
