r"""Test 1912 — gen #32 (expected PASS): ROUTE #227's COMPLETENESS CONTROL.

A rebinding CLEARS the `None` record (`_erased_truthy_locals` pops the entry on a non-`None`
assignment), so after `v = 0` the name is an ordinary integer and the arithmetic is exact.
`f()` really is 3 in Python.

This is the control that says #227's fence is a fence and not a blanket: the refusal keys on
the RECORD, and the record is what the emitter already maintains. It is also the condition
the refusal's own advice names — advice that names a condition the emitter CHECKS, which is
the discriminator route #90 was paid for.
"""
# pycsl-expected: PASS
_ = 0  # anchor
#@ ensures \result == 3
#@ no_exception \all
#@ assigns \nothing
def f() -> int:
    v = None
    v = 0
    return v - v + 3
