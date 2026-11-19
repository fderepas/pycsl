r"""Test 6337 -- route #428 (expected PASS): CONTROL: a module FUNCTION of a `_sm406` module (`json.dumps`) and an allow-listed constructor (`collections.OrderedDict`) taking an object-valued argument in `__init__`; `getattr(r, "k", 7) == 7` (GD) still proves (CPython 7). PROVED at base and candidate.
"""
# pycsl-expected: PASS
import json
import collections


class R:
    def __init__(self) -> None:
        self.v: int = 1
        self.s: str = json.dumps(self.v)
        self.o = collections.OrderedDict([(self.v, self.v)])


#@ ensures \result == 7
def f(r: R) -> int:
    return getattr(r, "k", 7)


if __name__ == "__main__":
    print(f(R()))
