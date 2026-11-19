r"""Test 4532 -- gen #37 route #338 (expected FAIL): #334 residual 1: `self.r = v` with `v` unannotated stayed int (the record literal is typed at VERIFIED call sites), but `__main__` (unverified) builds `U(0.5)`, and `c.r % 1 == 0` PROVED. REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK): an unannotated-parameter initialiser is of unknown type when unverified module code names the class.
"""
# pycsl-expected: FAIL
class U:
    def __init__(self, v) -> None:
        self.r = v

#@ ensures \result == True
def g_unannot_init(c: U) -> bool:
    return c.r % 1 == 0

if __name__ == "__main__":
    assert g_unannot_init(U(0.5)) == True
