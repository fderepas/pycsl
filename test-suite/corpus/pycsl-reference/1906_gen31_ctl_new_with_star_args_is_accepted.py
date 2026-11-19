r"""Test 1906 — gen #31 CONTROL for 1905 (expected PASS): `__new__(cls, *args, **kwargs)`.

A `__new__` that accepts anything cannot be narrower than `__init__`, so 1905's refusal
must not fire. This is the shape real Python code uses when it overrides allocation
without caring about the constructor's signature, and it RUNS: `grab(3)` is 3.

IF THIS FILE EVER FAILS, the arity rule has started counting a `*args` `__new__` as a fixed
arity and is refusing a class every call of which succeeds.
"""
# pycsl-expected: PASS
_ = 0  # anchor


class Holder:
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self, n: int):
        self.x = n


#@ requires k >= 0
#@ ensures \result == k
def grab(k: int) -> int:
    h = Holder(k)
    return h.x
