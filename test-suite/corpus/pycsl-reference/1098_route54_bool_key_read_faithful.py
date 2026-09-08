"""Test 1098 — ROUTE #54 control: the later entry wins, and the fold now says so.

TRUE OF THE PROGRAM: Python returns 20.

FAILED at the parent commit 967c68e1, proves here. A key the fold can normalise but whose
VALUE it cannot represent must still SHADOW an earlier entry at the same key — otherwise the
fold answers a value Python has overwritten, which is exactly witness 1097.
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ ensures \result == 20
#@ assigns \nothing
def f() -> int:
    d = {1: 10, True: 20}
    return d[1]


if __name__ == "__main__":
    assert f() == 20
