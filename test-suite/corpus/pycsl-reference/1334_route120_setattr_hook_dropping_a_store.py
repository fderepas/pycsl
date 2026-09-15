r"""Test 1334 — ROUTE #120: a `__setattr__` that drops `a = 5` was never consulted; `self.a = 5; return self.a` PROVED `\result == 5` while CPython returns 0. Refused.
"""
# pycsl-expected: FAIL
class C:
    a: int

    #@ assigns self.a
    def __init__(self) -> None:
        self.a = 0

    def __setattr__(self, name, value):
        if name == "a" and value == 5:
            return
        object.__setattr__(self, name, value)

    #@ ensures \result == 5
    #@ assigns self.a
    def put(self) -> int:
        self.a = 5
        return self.a
