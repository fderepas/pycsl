r"""Test 2883 — route #269 R3 (expected FAIL): 2882 through a GENERATOR, `sum(self.spin(x)
for x in xs)`, lowered to `sum_1 (any int)` — the call vanished, so `\result == 7` PROVED at
8b0bfbbd. CPython: `m([1])` never returns. Now `m`'s termination VC fails.
"""
# pycsl-expected: FAIL
from typing import List

class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result == 0
    #@ assigns \nothing
    #@ \diverges
    def spin(self, k: int) -> int:
        while k > 0:
            k = k + 1
        return 0

    #@ ensures \result == 7
    #@ assigns \nothing
    def m(self, xs: List[int]) -> int:
        s = sum(self.spin(x) for x in xs)
        return 7

if __name__ == "__main__":
    import threading
    t = threading.Thread(target=C().m, args=([1],), daemon=True)
    t.start()
    t.join(1.0)
    print("does not terminate" if t.is_alive() else "returned")
