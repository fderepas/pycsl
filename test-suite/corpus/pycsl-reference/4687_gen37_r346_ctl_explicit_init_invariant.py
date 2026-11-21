r"""Test 4687 -- gen #37 route #346: CONTROL: invariant class with an explicit `__init__` (no `__post_init__`); PROVES (CPython 0).
"""
#@ class invariant self.x >= 0
class B:
    def __init__(self) -> None:
        self.x = 0

#@ ensures \result >= 0
def f(b: B) -> int:
    return b.x

if __name__ == "__main__":
    print(f(B()))
