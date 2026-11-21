r"""Test 4360 -- gen #37 route #328 (expected PASS): control: an INT global `R = 2` beside the emitter's `with Return r -> r`: `R % 1 == 0` PROVES.
"""
# pycsl-expected: PASS
R = 2
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    if R % 1 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert g() == 1
