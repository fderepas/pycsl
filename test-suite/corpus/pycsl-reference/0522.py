"""Test 0522 — record-param method call (no-more-int-3 A2a; Track 3 follow-on).

A method call on a record-typed PARAM (`p.get_x()`) should resolve the callee's
contract, exactly like a method call on a locally-constructed record
(`c = C(); c.m()`). Track 3 landed read-only field reads on a record param
(0519); a *method* call on that param still lowered to a bare abstract op with
no `ensures`, so the result was unprovable. This driver flips to PASS when A2a
unions the record-param classes into the method-call resolution map.

Read-only: the called method must not mutate `p` (Why3 records are by-value).
"""
# pycsl-expected: FAIL
_ = 0  # anchor
class Point:
    def __init__(self, a: int, b: int):
        self.x = a
        self.y = b

    #@ requires self.x >= 0
    #@ ensures \result == self.x
    #@ assigns \nothing
    def get_x(self) -> int:
        return self.x


#@ requires p.x == 5
#@ ensures \result == 5
#@ assigns \nothing
def read_via_method(p: Point) -> int:
    return p.get_x()
