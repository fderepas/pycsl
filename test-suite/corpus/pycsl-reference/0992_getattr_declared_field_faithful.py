"""Test 0992 — the POSITIVE half of ROUTE #22: `getattr(obj, "field", d)` on a DECLARED
field now proves the TRUE postcondition.

`0991` is the same body with the FALSE `#@ ensures \result == 0`, which used to prove and
now correctly fails. This file carries the TRUE `#@ ensures \result == 7`, and it proves —
which nothing could do before, because the read lowered to the literal default and the
guard consuming it was decided by a constant.

Stating both halves matters: a fix that merely REFUSED the shape would make 0991 fail too,
and the two files would not tell it apart from a faithful lowering. Only 0992 distinguishes
"the erasure is closed" from "the construct is banned". The lowering is now the genuine
record read `self.a`, identical to a direct field access.
"""
# pycsl-expected: PASS
_ = 0  # anchor


class C:
    #@ requires True
    #@ ensures self.a == 7
    #@ assigns self.a
    def __init__(self) -> None:
        self.a: int = 7

    #@ requires self.a == 7
    #@ ensures \result == 7
    #@ assigns \nothing
    def get(self) -> int:
        v = getattr(self, "a", 0)
        if v:
            return 7
        return 0


if __name__ == "__main__":
    print(C().get())
