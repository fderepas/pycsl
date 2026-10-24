r"""Test 4294 -- gen #37 route #326 (expected PASS): CONTROL: `sys` attributes that are not import state (`sys.argv`, `sys.stdout`) beside a local import: not refused, PROVES.
"""
# pycsl-expected: PASS
import sys
from multi_file_lib.r326smod import f

#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return f()

if __name__ == "__main__":
    sys.stdout.write(str(len(sys.argv)) + "\n")
    assert g() == 2, g()
