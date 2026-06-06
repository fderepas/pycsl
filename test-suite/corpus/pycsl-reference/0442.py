"""0442 — same-file inheritance (Layer B + C).

`Sub(Base)` inherits Base's field `start`, Base's class invariant
`start >= 0`, and Base's method `get`; it adds its own field `extra`, its own
invariant `extra >= 0`, and an own method `total`. Verification relies on the
merge:

  * `Sub.total` returns `self.start + self.extra` and `ensures \\result >= 0` —
    provable only because BOTH invariants (inherited `start >= 0` ∧ own
    `extra >= 0`) hold on a `Sub`.
  * The inherited `get` is monomorphized onto `Sub` (its `self.start` resolves
    against Sub's merged record).

Without the merge, Sub's record would lack `start`, both `self.start` reads
would be opaque, and neither postcondition would discharge.
"""


#@ class invariant self.start >= 0
class Base:
    def __init__(self):
        self.start: int = 7

    #@ ensures \result == self.start
    #@ assigns \nothing
    def get(self) -> int:
        return self.start


#@ class invariant self.extra >= 0
class Sub(Base):
    def __init__(self):
        super().__init__()
        self.extra: int = 0

    #@ ensures \result >= 0
    #@ assigns \nothing
    def total(self) -> int:
        return self.start + self.extra


if __name__ == "__main__":
    s = Sub()
    assert s.get() == 7
    assert s.total() == 7
    print("PASS")
