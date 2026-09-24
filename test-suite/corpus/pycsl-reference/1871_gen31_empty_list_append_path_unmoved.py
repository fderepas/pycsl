r"""Test 1871 — gen #31 BOUND for 1869/1870 (expected PASS): the append path is untouched.

`Array.make 1024 0` is spelled the same for TWO jobs — the CAPACITY of an append target,
whose real length is carried by an `X_len` sidecar, and the VALUE of an empty list that is
never appended to. A Why3 array's length IS its capacity, so one literal cannot serve both,
which is why the repair corrects the CONSEQUENCE (the emitted `Array.length result` of a
function that returns the bare placeholder) instead of the literal.

This file is the guard on that distinction: a list that IS appended to was faithful before
the repair — `\length(\result) == 1` proved, `== 0` and `== 1024` both failed — and must
stay exactly that way. If a future attempt moves the literal itself, this file is the one
that should go red first.
"""
# pycsl-expected: PASS
_ = 0  # anchor


#@ ensures \length(\result) == 1
#@ assigns \nothing
def mk() -> list:
    xs = []
    xs.append(7)
    return xs
