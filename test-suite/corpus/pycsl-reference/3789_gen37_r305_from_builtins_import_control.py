r"""Test 3789 -- gen #37 route #305 (expected PASS): control: `from builtins import KeyError` rebinds the builtin to itself; a builtin KeyError raised under `except LookupError` is caught (route #260 hierarchy) and `\result == 1` must still PROVE.
"""
from builtins import KeyError

#@ ensures \result == 1
def g(x: int) -> int:
    try:
        if x < 0:
            raise KeyError("x")
    except LookupError:
        return 1
    return 1

if __name__ == "__main__":
    assert g(-1) == 1
