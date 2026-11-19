r"""Test 4292 -- gen #37 route #326 (expected FAIL): the rebind happens in a DEPENDENCY's top-level code (`multi_file_lib/r326poke.py`), which runs on import before the importer's next import. REFUSED: PYCSL-SEM-IMPORT-STATE-MANIPULATED.
"""
# pycsl-expected: FAIL
from multi_file_lib.r326poke import noop
from multi_file_lib.r326smod import f

#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return f() + noop()

if __name__ == "__main__":
    assert g() == 2, g()
