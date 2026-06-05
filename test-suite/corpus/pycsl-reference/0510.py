"""Test 0510 — string + dict: store a string length in a dict and read it back.

Combines the real `str` model (`len(s)` → `String.length`) with the dict model (`map int (option
int)`): writing `d[0] = len(s)` and reading `d[0]` proves `\result == \str_length(s)`."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ requires \str_length(s) >= 0
#@ ensures \result == \str_length(s)
def store_len(s: str) -> int:
    d = {}
    d[0] = len(s)
    return d[0]
