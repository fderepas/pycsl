r"""Test 3786 -- gen #37 route #305 (expected FAIL): an IMPORTED module (`multi_file_lib/r305_shadow_keyerror.py`) defines `class KeyError(Exception)`; `raise sm.KeyError(...)` under `except LookupError` + `no_exception \all`. The dependency modules are parsed (route #181) and their class statements binding a builtin exception name are refused (route #305).
"""
# pycsl-expected: FAIL
import multi_file_lib.r305_shadow_keyerror as sm

#@ no_exception \all
#@ ensures \result == 1
def g(x: int) -> int:
    try:
        if x < 0:
            raise sm.KeyError("x")
    except LookupError:
        return 1
    return 1

if __name__ == "__main__":
    assert g(-1) == 1
