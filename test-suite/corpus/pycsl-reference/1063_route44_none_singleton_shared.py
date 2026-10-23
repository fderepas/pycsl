"""Test 1063 — ROUTE #44 control: two `None`s are the SAME object.

TRUE OF THE PROGRAM: `None == None` is True, so Python returns 7.

This is why route #44's opaque constant is SHARED where route #41's was PER-NAME, and
the difference is not a style choice. Route #41's erased locals denote DIFFERENT objects
(a generator and a tuple), so one shared constant would have let the model prove `x == y`
for two of them — one unsoundness traded for another. `None` really is ONE object, so the
shared constant is the faithful model and this driver is what says so: a per-name
`pycsl_none_x` / `pycsl_none_y` would make this test undecidable while Python is certain.
"""
_ = 0  # anchor
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = None
    y = None
    if x == y:
        return 7
    return 0
