"""Test 1096 — ROUTE #54 control: the repair is EXACT, not merely fail-closed.

TRUE OF THE PROGRAM: Python's `len({1: 10, True: 20})` is 1.

This file FAILED at the parent commit 967c68e1 and proves here. Giving the fold Python's own
key equality — normalise a literal key to its VALUE, a `Bool` key being the int 1/0 — does
not just stop the wrong answer, it produces the right one. Route #45 was the campaign's first
repair to buy completeness as well as soundness; this is the third, after route #50.
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    d = {1: 10, True: 20}
    return len(d)


if __name__ == "__main__":
    assert f() == 1
