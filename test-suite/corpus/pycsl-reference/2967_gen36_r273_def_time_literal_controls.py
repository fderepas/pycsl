r"""Test 2967 — route #273 CONTROL (expected PASS): what the repair must NOT touch — a
nested def whose defaults are literals / a bare parameter name / an empty-list display, a
lambda with a `None` default, and a nested class of literal attributes and a method. None
of these evaluates anything that can raise, write or diverge. CPython: 3.
"""
# pycsl-expected: PASS

#@ ensures \result == 3
#@ assigns \nothing
def f(x: int) -> int:
    def inner(y: int = 2, z: int = x, w: int = -1) -> int:
        return y
    h = lambda a=None: a

    class K:
        """a nested class of literal attributes"""
        v = 1
        u: int = 2

        def get(self) -> int:
            return 1
    return 3

if __name__ == "__main__":
    print(f(0))
