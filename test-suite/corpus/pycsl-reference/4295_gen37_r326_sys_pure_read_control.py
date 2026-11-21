r"""Test 4295 -- gen #37 route #326 (expected PASS): CONTROL: PURE READS of import state (`len(sys.path)`, `"sys" in sys.modules`, `hasattr(sys, "meta_path")`, `isinstance(sys.path_hooks, list)`) beside a local import are not refused: they cannot edit the import system or hand out an alias. PROVES.
"""
# pycsl-expected: PASS
import sys
from multi_file_lib.r326smod import f

#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return f()

if __name__ == "__main__":
    assert len(sys.path) > 0
    assert "sys" in sys.modules
    assert hasattr(sys, "meta_path")
    assert isinstance(sys.path_hooks, list)
    assert g() == 2, g()
