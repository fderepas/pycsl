r"""Test 5885 -- driver run #3 route #226 polarity flip (expected FAIL): the `#@ requires line >= 0` that stage 2d uses as a PREMISE of `goal _check_class_inv_e` (the mirror `errors.py` shape) is not a `requires { }` of an emitted `e__init`; this file shows it cannot certify a bad construction: `E("m", line=-1)` inside a VERIFIED function raises the record's type-invariant VC, which FAILS (CPython `where()` is -1).
"""
# pycsl-expected: FAIL


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


#@ ensures \result >= 0
def bad() -> int:
    e = E("m", line=-1)
    return e.where()


if __name__ == "__main__":
    print(bad())
