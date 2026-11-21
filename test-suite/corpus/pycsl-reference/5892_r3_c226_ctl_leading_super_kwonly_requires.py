r"""Test 5892 -- driver run #3 route #226 polarity flip CONTROL (expected PASS): the mirror `errors.py` shape — a leading `super().__init__(message)`, then `self.line = line` from a keyword-only int parameter under `#@ requires line >= 0`, and a subclass without its own `__init__`; both classes get `forall line : int. line = line -> (line >= 0) -> ..`.
"""
# pycsl-expected: PASS


#@ class invariant self.line >= 0
class E(Exception):
    #@ requires line >= 0
    def __init__(self, message: str, *, line: int = 0) -> None:
        super().__init__(message)
        self.line = line

    #@ ensures \result >= 0
    #@ assigns \nothing
    def where(self) -> int:
        return self.line


class F(E):
    pass


if __name__ == "__main__":
    print(E("m", line=3).where(), F("n").where())
