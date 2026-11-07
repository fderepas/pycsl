r"""Test 4206 -- gen #37 route #322 (expected PASS): CONTROL: `xs = [1, 2]; sum(xs) == 3` still folds.
"""
# pycsl-expected: PASS
#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    xs = [1, 2]
    return sum(xs)

if __name__ == "__main__":
    assert f() == 3, f()
