r"""Test 4544 -- gen #37 route #338: CONTROL: an unannotated `__init__` parameter whose class is only constructed by VERIFIED code (`mk() -> U` builds `U(3)`; `__main__` names `mk`, not `U`) stays int; PROVES.
"""
class U:
    def __init__(self, v) -> None:
        self.r = v

def mk() -> U:
    return U(3)

#@ ensures \result == True
def g(c: U) -> bool:
    return c.r % 1 == 0

if __name__ == "__main__":
    assert g(mk()) == True
