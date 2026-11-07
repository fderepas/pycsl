r"""Test 4469 -- gen #37 route #335 (control, expected PASS): control: subclass `__init__` stores the invariant field itself (`self.n = 4`) without `super()`. PROVED. 
"""
# pycsl-expected: PASS
#@ class invariant self.n >= 0
class B:
    def __init__(self) -> None:
        self.n = 0

class S(B):
    def __init__(self) -> None:
        self.n = 4

#@ ensures \result >= 0
def f(b: B) -> int:
    return b.n

if __name__ == "__main__":
    assert f(S()) >= 0
