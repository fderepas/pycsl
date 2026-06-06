"""0440 — class-level integer constant usable in a contract (self.CAP → literal).

`CAP` is a class-body constant (not an `__init__` field). It is referenced as
`self.CAP` in both the contract and the body. Module 5 collects class-body int
constants into the class IR (`_collect_class_constants`); Module 6 lowers
`self.CAP` to its literal `64` in the FieldGet handler, so the bound is provable
rather than an opaque `getattr`. Without that, `self.CAP` would be an
uninterpreted int and `ensures \result <= self.CAP` could not be discharged.
"""


#@ class invariant self.count >= 0
class Bucket:
    CAP = 64

    def __init__(self):
        self.count: int = 0

    #@ requires self.count < self.CAP
    #@ assigns self.count
    #@ ensures \result == self.count
    #@ ensures \result <= self.CAP
    def add_one(self) -> int:
        self.count = self.count + 1
        return self.count


if __name__ == "__main__":
    b = Bucket()
    assert b.add_one() == 1
    print("PASS")
