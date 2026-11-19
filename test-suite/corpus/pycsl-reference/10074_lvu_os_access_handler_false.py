r"""Test 10074 -- lvU `os.access` (expected FAIL): the `except ValueError` arm is REACHABLE (an
embedded NUL; a lone surrogate raises UnicodeEncodeError, a ValueError), so `\result == 0` is
false (CPython: `safe("a\x00b")` is 1). Measured verdict: refused -- a `try` body with an `except
ValueError` arm is judged under ValueError (the existing handler rule), where the route #161 census
does not admit the world query (the same holds for lvQ's `subprocess.run`). Control: 10070.
"""
# pycsl-expected: FAIL
import os


#@ ensures \result == 0
#@ assigns \nothing
def safe(p: str) -> int:
    try:
        if os.access(p, os.X_OK):
            return 0
    except ValueError:
        return 1
    return 0


if __name__ == "__main__":
    r = safe("a\x00b")
    print("VIOLATION contract" if r != 0 else "result", r)
