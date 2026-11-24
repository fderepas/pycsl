r"""Test 10420 -- run #9 u70, review rt77 F1, route #624 (FAIL, PRE-EXISTING). `import qa70` beside a LOCAL
`def val1`: pycsl skipped the dependency's `val1` because the name was taken and lowered `qa70.val1()` to
the local one, so `g() == 2` PROVED at daa36070b. CPython runs qa70.val1 and prints "result 1".
u70 refused it (NAME-CLASH); since u72 the dependency function keeps its own identity (a fresh
WhyML name when the name is taken) and each call binds to the def CPython runs: the claim fails.
"""
# pycsl-expected: FAIL
import qa70


#@ ensures \result == 2
#@ assigns \nothing
def val1() -> int:
    return 2


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return qa70.val1()


if __name__ == "__main__":
    print("result", g())
