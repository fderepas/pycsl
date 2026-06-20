# Pure model for shlex — shell-like lexer


#@ requires length >= 0
#@ ensures \result >= 0
#@ ensures \result <= length
def split(length: int) -> int:
    """Split shell command string into tokens. Returns token count."""
    return length


#@ assigns \nothing
def quote(s: str) -> str:
    """Return a shell-escaped version of the string s."""
    return s


#@ requires length >= 0
#@ ensures \result >= length
def join(length: int) -> int:
    """Join tokens into shell command. Returns output length."""
    return length
