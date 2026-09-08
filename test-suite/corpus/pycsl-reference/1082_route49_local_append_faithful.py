"""Test 1082 — ROUTE #49 control: a LOCAL list's appends are faithful and must keep proving.

TRUE OF THE PROGRAM: Python returns 2.

The half of route #49 that must NOT be refused. A local list is not shared with any caller,
so growing it through `Seq.snoc` is exactly right, and `len` tracks the logical length. The
refusal is therefore keyed on the name being a FORMAL PARAMETER — not on `.append` itself —
and this driver is what says so: a refusal written against the method name would make this
file fail, and it is the shape most ordinary Python code uses.
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    a = []
    a.append(1)
    a.append(2)
    return len(a)
