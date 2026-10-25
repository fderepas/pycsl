r"""Test 5044 -- gen #37 route #372 (expected PASS): CONTROL: `{r.f}` frozen field, `{t[1]}` int component, `{m[0]}` frozen value (CPython ok).
"""
# pycsl-expected: PASS
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
