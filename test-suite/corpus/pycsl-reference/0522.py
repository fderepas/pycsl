"""Test 0522 — record-param method call (no-more-int-3 A2a; Track 3 follow-on).

A method call on a record-typed PARAM (`a.bump(k)`) resolves the callee's
contract exactly like a method call on a locally-constructed record
(`c = C(); c.m()`): the callee's result-only and param-referencing `ensures`
propagate to the call site. Track 3 landed read-only field reads on a record
param (0519); before A2a, a *method* call on that param lowered to a bare
abstract op with no `ensures`, so the result was unprovable.

Scope: A2a delivers only the propagation record locals already get (result-only
/ param-referencing `ensures`). A *field-referencing* callee ensure (`\result ==
self.x`) does NOT propagate — that is the pre-existing method-call contract gap
(it fails for record LOCALS too, not just params), tracked separately. Read-only:
the called method must not mutate `a` (Why3 records are by-value).
"""
_ = 0  # anchor
class Adder:
    def __init__(self, base: int):
        self.base = base

    #@ requires k >= 0
    #@ ensures \result == k + 1
    #@ assigns \nothing
    def bump(self, k: int) -> int:
        return k + 1


#@ requires k >= 0
#@ ensures \result == k + 1
#@ assigns \nothing
def via_param(a: Adder, k: int) -> int:
    return a.bump(k)
