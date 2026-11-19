r"""Test 4528 -- gen #37 route #337 (expected PASS): CONTROL: identity `x is x` of a field-less class instance PROVES (erasure keeps `is`).
"""
# pycsl-expected: PASS
class P:
    pass

#@ ensures \result == True
def same(x: P) -> bool:
    return x is x

if __name__ == "__main__":
    assert same(P()) == True
