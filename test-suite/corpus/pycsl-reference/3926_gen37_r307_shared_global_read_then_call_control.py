r"""Test 3926 -- gen #37 route #307 (expected PASS): CONTROL: `counter + bump()` on a `#@ shared` global proves the CPython value 1.
"""
# pycsl-expected: PASS
#@ shared counter
counter = 0

def bump() -> int:
    global counter
    counter += 1
    return counter

#@ ensures \result == 1
def f() -> int:
    return counter + bump()

if __name__ == "__main__":
    assert f() == 1
