r"""Test 10422 -- run #9 u70, review rt77 F2, route #625 (FAIL, PRE-EXISTING). qa70 and qb70 each define
`helper` (returning 1 and 2): pycsl kept ONE `val helper` (qa70's) for both qualified calls, so the false
`g() == 2 or g() == 4` PROVED at daa36070b (and the true `== 3` failed). CPython prints "result 3".
u70 refused it (NAME-CLASH); since u72 the dependency function keeps its own identity (a fresh
WhyML name when the name is taken) and each call binds to the def CPython runs: the claim fails.
"""
# pycsl-expected: FAIL
import qa70
import qb70


#@ ensures \result == 2 or \result == 4
#@ assigns \nothing
def g() -> int:
    return qa70.helper() + qb70.helper()


if __name__ == "__main__":
    print("result", g())
