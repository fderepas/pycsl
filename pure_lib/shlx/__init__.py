# Pure model for shlex — shell-like lexer
# Models as token-count based parsing.


#@ requires length >= 0
#@ ensures \result >= 0
#@ ensures \result <= length
def split(length: int) -> int:
    """Split shell command string into tokens. Returns token count."""
    return length


#@ requires length >= 0
#@ ensures \result >= length
def quote(length: int) -> int:
    """Shell-quote a string. Output >= input length."""
    return length + 2


#@ requires length >= 0
#@ ensures \result >= length
def join(length: int) -> int:
    """Join tokens into shell command. Output >= input count."""
    return length
