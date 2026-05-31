"""PyCSL mock for Python's getpass module — Portable reading of passwords and retrieval of the userid."""
_ = 0  # anchor

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/getpass.html#getpass.getpass
#@ ensures True
def getpass(prompt: int, stream: int, echo_char: int) -> int:
    """Mock: Prompt the user for a password without echoing.  The user is prompted using the string *prompt*, which defaults to ``'Pa..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/getpass.html#getpass.getuser
#@ ensures \result != ""
def getuser() -> int:
    """Mock: Return the 'login name' of the user. This function checks the environment variables :envvar:`LOGNAME`, :envvar:`USER`, :..."""
    return 0
