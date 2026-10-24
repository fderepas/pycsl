r"""Test 4290 -- gen #37 route #326 (expected FAIL): `sys.modules.update({"multi_file_lib.r326smod": <the r326pkg module>})` (inside a `\trusted` helper called at module scope, which the module-scope write checks do not see) makes the later `from multi_file_lib.r326smod import f` bind the package's f (1); pycsl PROVED the file's `f() == 2`. REFUSED: PYCSL-SEM-IMPORT-STATE-MANIPULATED.
"""
# pycsl-expected: FAIL
import sys
import multi_file_lib.r326pkg
#@ \trusted
#@ assigns \nothing
def _setup() -> None:
    sys.modules.update({"multi_file_lib.r326smod": sys.modules["multi_file_lib.r326pkg"]})
_setup()
from multi_file_lib.r326smod import f

#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return f()

if __name__ == "__main__":
    assert g() == 2, g()
