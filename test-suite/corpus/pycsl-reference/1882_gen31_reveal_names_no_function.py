r"""Test 1882 — gen #31 WITNESS (expected FAIL): `#@ reveal` naming no function is refused.

This file is the one that cost the least to find and says the most. `#@ reveal` was
IMPLEMENTED THIS GENERATION, eight hours before the audit that found this hole, and it had
exactly the same defect as the oldest directives in the tree: the repair collects the
module's reveal names into a set and asks whether the function being stubbed is in it, so a
name that matches nothing simply never matches, and nothing looks.

    #@ reveal no_such_function
    [+] Verification SUCCESS! All contracts formally proven.

Filed as wall-lesson (v4) — run the new audit against your own newest increment first. The
instinct is to point a fresh instrument at old code, and the code written today was written
WITHOUT the instrument, so it is the least likely to survive it.

Control: 1883, the same file revealing a function that exists.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ reveal no_such_function
#@ requires x > 0
#@ ensures \result == x
#@ assigns \nothing
def caller(x: int) -> int:
    return x
