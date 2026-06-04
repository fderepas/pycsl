"""Test 0496 — class: trivial __new__ + parametrized __init__ (base_op.md Tier A).

A trivial `__new__` (`return super().__new__(cls)`) is the default allocation and is accepted;
construction proceeds via `__init__`, so `Holder(k)` builds `{x = k}` and `.x` discharges
`\result == k`. A NON-trivial `__new__` (caching / singleton / returning another instance) is
rejected under UB-7.6 — see the negative 0497."""
_ = 0  # anchor
class Holder:
    def __new__(cls):
        return super().__new__(cls)

    def __init__(self, n: int):
        self.x = n


#@ requires k >= 0
#@ ensures \result == k
def grab(k: int) -> int:
    h = Holder(k)
    return h.x
