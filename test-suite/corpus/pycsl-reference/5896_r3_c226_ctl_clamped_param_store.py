r"""Test 5896 -- driver run #3 route #226 polarity flip CONTROL (expected PASS): the mirror `errors.py` repair — a leading `super().__init__(message)`, then `self.line = max(line, 0)` from a keyword-only int parameter with NO precondition; goal stage 2d states `forall line : int. line_f = (if line >= 0 then line else 0) -> ..`, which discharges.
"""
# pycsl-expected: PASS


#@ class invariant self.line >= 0
class E(Exception):
    def __init__(self, message: str, *, line: int = 0) -> None:
        super().__init__(message)
        self.line = max(line, 0)

    #@ ensures \result >= 0
    #@ assigns \nothing
    def where(self) -> int:
        return self.line


class F(E):
    pass


if __name__ == "__main__":
    print(E("m", line=-3).where(), F("n").where())
