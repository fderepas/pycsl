r"""Test 4268 -- gen #37 route #325 control (expected PASS): an opaque `time.time()` compared `==` to a literal in program code (no reflexivity) stays admitted.
"""
# pycsl-expected: PASS
import time
#@ ensures \result >= 0
#@ assigns \nothing
def g() -> int:
    t = time.time()
    if t == 0:
        return 1
    return 2

if __name__ == "__main__":
    assert g() >= 0
