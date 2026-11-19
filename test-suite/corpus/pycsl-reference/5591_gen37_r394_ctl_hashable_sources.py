r"""Test 5591 -- gen #37 route #394 (expected PASS): CONTROL: every source the allow-list now derives, over HASHABLE values: a module global bound once to an int / a str / a tuple of those / a frozen dataclass instance, a class attribute (`C.K`, `self.K`), `set(d.values())` / `frozenset(d.keys())` / `set(d.items())` of a `Dict[str, int]`, `copy.copy` / `dataclasses.replace` of a frozen dataclass (CPython ok). PROVED at base and candidate.
"""
# pycsl-expected: PASS
import copy
import dataclasses
from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class P:
    x: int


K = 5
NAME = "a"
PAIR = (1, "b")
ORIGIN = P(0)


class C:
    K = 3

    #@ no_exception \all
    #@ assigns \nothing
    #@ ensures \result == 1
    def m(self) -> int:
        s = {self.K}
        return 1


#@ no_exception \all
#@ ensures \result == 1
def f(d: Dict[str, int], q: P) -> int:
    a = {K, NAME, PAIR, ORIGIN, C.K}
    v = set(d.values())
    e = frozenset(d.keys())
    g = set(d.items())
    h = {copy.copy(q), dataclasses.replace(q)}
    return 1


if __name__ == "__main__":
    print(f({"a": 1}, P(1)), C().m())
