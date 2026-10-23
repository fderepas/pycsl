r"""Test 3925 -- gen #37 route #307 (expected FAIL): `#@ shared` global read then a call that writes it, `counter + bump()`: the read ran AFTER the call (Why3 right-to-left); CPython returns 1, the model proved 2.
"""
# pycsl-expected: FAIL
#@ shared counter
counter = 0

def bump() -> int:
    global counter
    counter += 1
    return counter

#@ ensures \result == 2
def f() -> int:
    return counter + bump()

if __name__ == "__main__":
    assert f() == 2
