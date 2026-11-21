r"""Test 2558 — route #255 (expected FAIL): `k.get()` on a `K` whose `get` is declared `-> Any` was not erased (route #249 erased only a
module function or a `self.` call): `v = k.get(); return v - v` PROVED `\result == 0`.
CPython: a user `__sub__` returns 7. PROVED at e6f26cde; now REFUSED fail-closed (route #252's flow refusal, now reached).
"""
# pycsl-expected: FAIL
from typing import Any


class K:
    def __init__(self, a: Any) -> None:
        self.a: Any = a

    #@ assigns \nothing
    def get(self) -> Any:
        return self.a


#@ ensures \result == 0
#@ assigns \nothing
def f(k: K) -> int:
    v = k.get()
    return v - v

if __name__ == "__main__":
    class S:
        def __sub__(self, o: object) -> int:
            return 7

        def __abs__(self) -> "S":
            return self

        def __gt__(self, o: object) -> bool:
            return False

        def __lt__(self, o: object) -> bool:
            return False

        def __getattr__(self, n: str) -> "S":
            return self

    print(f(K(S())))
