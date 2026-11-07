r"""Test 4265 -- gen #37 route #325 control (expected PASS): an INT class attribute (`C.R = 5`) keeps its int model.
"""
# pycsl-expected: PASS
class C:
    R = 5
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    if C.R % 1 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert g() == 1
