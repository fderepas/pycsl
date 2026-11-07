r"""Test 5392 -- gen #37 route #383 (expected PASS): CONTROL: #383 sources (alias, `.get`, comprehension, method `-> D`, `{*ds}`, field) over a FROZEN element class, in a file with an unhashable class (CPython ok).
"""
# pycsl-expected: PASS
from dataclasses import dataclass
from typing import List, Dict, Tuple

@dataclass
class U:
    x: int

@dataclass(frozen=True)
class D:
    x: int

DD = D
DL = List[D]

class R:
    def __init__(self, m: Dict[str, D], d: D) -> None:
        self.m = m
        self.d = d
    #@ assigns \nothing
    def get(self) -> D:
        return self.d

#@ no_exception \all
#@ ensures \result == 1
def g(d: DD, ds: DL, m: Dict[str, D], r: R) -> int:
    s0 = {d}
    v = m.get("a")
    s1 = {v}
    xs = [d for _ in range(1)]
    s4 = {*xs}
    s5 = {r.get()}
    e = r.get()
    s6 = {e}
    s7 = {*ds}
    s10 = {r.d}
    return 1

if __name__ == "__main__":
    print(g(D(1), [D(2)], {"a": D(3)}, R({"a": D(4)}, D(5))))
