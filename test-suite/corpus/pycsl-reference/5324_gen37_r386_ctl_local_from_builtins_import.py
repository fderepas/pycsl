r"""Test 5324 -- gen #37 route #386 (expected PASS): control: function-local `from builtins import max` binds the builtin itself; PROVED.
"""
# pycsl-expected: PASS
#@ ensures \result == 3
#@ assigns \nothing
def m() -> int:
    from builtins import max
    return max(3, 1)


if __name__ == "__main__":
    assert m() == 3
