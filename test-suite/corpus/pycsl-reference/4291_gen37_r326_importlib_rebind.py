r"""Test 4291 -- gen #37 route #326 (expected FAIL): `importlib.import_module("multi_file_lib.r326poke")` DYNAMICALLY runs a module whose top-level code rebinds `sys.modules["multi_file_lib.r326smod"]` (no `sys` in this file, and pycsl never reads a dynamically-imported module), so the later `from multi_file_lib.r326smod import f` binds the package's f (1); pycsl PROVED the file's `g() == 2`. REFUSED: PYCSL-SEM-IMPORT-STATE-MANIPULATED (dynamic-import machinery beside a locally-resolved import).
"""
# pycsl-expected: FAIL
import importlib
importlib.import_module("multi_file_lib.r326poke")
from multi_file_lib.r326smod import f

#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return f()

if __name__ == "__main__":
    assert g() == 2, g()
