"""PyCSL mock for Python's codeop module — Compile (possibly incomplete) Python code."""
_ = 0  # anchor

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/codeop.html#codeop.compile_command
#@ ensures \result >= 0
def compile_command(source: int, filename: int, symbol: int) -> int:
    """Mock: Tries to compile *source*, which should be a string of Python code and return a code object if *source* is valid Python ..."""
    return 0
