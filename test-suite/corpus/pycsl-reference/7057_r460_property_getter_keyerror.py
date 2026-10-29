r"""Test 7057 -- route #460 (expected FAIL): red-team 37 carrier e3/k002 -- a claiming `f` (`#@ no_exception \all`) reads `c.v`, an UN-claimed `@property` whose body reads `self.d['k']` (CPython KeyError for f({})). PROVED at base 370db7dc2; the getter is reached through the attribute-load edge and is now judged under the reached claim (FAILS, as the same getter claiming `\all` itself does at base).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class C:
    def __init__(self, d: Dict[str, int]) -> None:
        self.d = d

    @property
    def v(self) -> int:
        return self.d['k']



#@ no_exception \all
def f(d: Dict[str, int]) -> int:
    c = C(d)
    return c.v


if __name__ == "__main__":
    try:
        r = f({})
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
