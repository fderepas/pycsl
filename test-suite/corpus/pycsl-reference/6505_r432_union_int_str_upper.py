r"""Test 6505 -- route #432 (expected FAIL): `.upper()` on `Union[int, str]` under `#@ no_exception \all`. PROVED at base 1c083dcbe (= 78b519f63 emission); CPython raises AttributeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R432-OPTIONAL-RECEIVER-ATTRIBUTE).
"""
# pycsl-expected: FAIL
from typing import Optional
from typing import Union

#@ no_exception \all
def f(x: Union[int, str]) -> int:
    return len(x.upper())


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
