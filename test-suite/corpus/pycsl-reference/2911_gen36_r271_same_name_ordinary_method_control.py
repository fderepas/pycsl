r"""Test 2911 — route #271 CONTROL (expected PASS): class `P` has an ORDINARY method `block`
while class `U` has a GENERATOR `block` used only as a `with` item; `self.block()` inside `P`
resolves to `P.block` (the mirror's `_Parser.block` / `_Unparser.block` shape) and is not
refused. CPython `P().run()` = 2.
"""
# pycsl-expected: PASS
from contextlib import contextmanager
from typing import Iterator

class U:
    def __init__(self) -> None:
        pass

    @contextmanager
    #@ assigns \nothing
    def block(self) -> Iterator[None]:
        yield

    #@ assigns \nothing
    def emit(self) -> int:
        with self.block():
            pass
        return 0

class P:
    def __init__(self) -> None:
        pass

    #@ ensures \result == 2
    #@ assigns \nothing
    def block(self) -> int:
        return 2

    #@ ensures \result == 2
    #@ assigns \nothing
    def run(self) -> int:
        return self.block()

if __name__ == "__main__":
    print(P().run(), U().emit())
