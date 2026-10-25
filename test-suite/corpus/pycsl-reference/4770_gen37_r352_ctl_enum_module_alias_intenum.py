r"""Test 4770 -- gen #37 route #352 (expected PASS): CONTROL: `import enum as e; class P(e.IntEnum)` (the mirror's `_Precedence` shape) keeps int semantics: `x - x == 0` under `no_exception \all` proves (CPython 0).
"""
# pycsl-expected: PASS
import enum as e

class P(e.IntEnum):
    LOW = 1
    HIGH = 2

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    x = P.LOW
    return x - x

if __name__ == "__main__":
    assert f() == 0
