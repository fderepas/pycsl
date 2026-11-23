r"""Test 10421 -- run #9 u70, review rt77 F1b, route #624 (FAIL, PRE-EXISTING). Same as 10420 through an
alias, `import qa70 as L` and `L.val1()`: `g() == 2` PROVED at daa36070b, CPython prints "result 1".
u70 refused it (NAME-CLASH); since u72 the dependency function keeps its own identity (a fresh
WhyML name when the name is taken) and each call binds to the def CPython runs: the claim fails.
"""
# pycsl-expected: FAIL
import qa70 as L


#@ ensures \result == 2
#@ assigns \nothing
def val1() -> int:
    return 2


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return L.val1()


if __name__ == "__main__":
    print("result", g())
