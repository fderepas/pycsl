"""PyCSL mock for Python's shlex module — Simple lexical analysis for Unix shell-like languages."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def split(s: int, comments: int, posix: int) -> int:
    """Mock: Split the string *s* using shell-like syntax. If *comments* is :const:`False` (the default), the parsing of comments in ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def join(split_command: int) -> int:
    """Mock: Concatenate the tokens of the list *split_command* and return a string. This function is the inverse of :func:`split`. >..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def quote(s: int) -> int:
    """Mock: Return a shell-escaped version of the string *s*.  The returned value is a string that can safely be used as one token i..."""
    return 0
