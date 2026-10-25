r"""Test 5462 -- gen #37 systematic rule S1 (expected PASS): CONTROL: `import typing as t; class Q(t.NamedTuple)` resolves to `typing.NamedTuple`, a modelled base of S1's table (the dotted, aliased spelling is admitted like the bare one); PROVED (CPython 3).
"""
# pycsl-expected: PASS
import typing as t

class Q(t.NamedTuple):
    a: int
    b: int

#@ ensures \result == 3
def f() -> int:
    q = Q(1, 2)
    return q.a + q.b

if __name__ == "__main__":
    assert f() == 3
