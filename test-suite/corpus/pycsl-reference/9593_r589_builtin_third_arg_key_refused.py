r"""Test 9593 -- route #589 WITNESS (expected FAIL: REFUSED PYCSL-R589-RAISE-ARGUMENT-UNEVALUATED at HEAD, every model): a BUILTIN exception drops its later arguments too: `raise ValueError("a", 1, d["zz"])` under `except ValueError` and `except KeyError`. CPython raises KeyError first and returns 2; the claim `\result == 1` is false.
"""
# pycsl-expected: FAIL
from typing import Dict


#@ ensures \result == 1
def f(d: Dict[str, int]) -> int:
    try:
        raise ValueError("a", 1, d["zz"])
    except KeyError:
        return 2
    except ValueError:
        return 1
    return 0


if __name__ == "__main__":
    print(f({"a": 1}))
