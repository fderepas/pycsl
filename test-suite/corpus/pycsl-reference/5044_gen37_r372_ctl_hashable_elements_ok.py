r"""Test 5044 -- gen #37 route #372 (expected PASS): CONTROL: `{r.f}` frozen field, `{t[1]}` int component, `{m[0]}` frozen value (CPython ok).
ROUTE #506 (run #4): now expected FAIL -- REFUSED PYCSL-R506-TRIGGER-SITE-UNLOWERED by design. The subscript sits in a position the lowering never evaluates, so the IndexError / KeyError obligation the `no_exception \all` claim covers is absent from the VC; the program is CPython-honest only because of its guard / data, which the model never checks (`{t[1]}` / `{m[0]}`: tw-twin `{m[5]}` PROVED at base, CPython KeyError; bound-first twin 8028).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class F:
    x: int


@dataclass
class D:
    x: int


class R:
    def __init__(self, f: F) -> None:
        self.f = f


#@ no_exception \all
#@ ensures \result == 1
def g(r: R, t: Tuple[D, int], m: Dict[int, F]) -> int:
    s = {r.f}
    u = {t[1]}
    if 0 in m:
        v = {m[0]}
    return 1


if __name__ == "__main__":
    print(g(R(F(1)), (D(1), 2), {0: F(2)}))
