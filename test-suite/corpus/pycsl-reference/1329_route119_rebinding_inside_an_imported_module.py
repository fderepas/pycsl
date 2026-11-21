r"""Test 1329 — ROUTE #119: the rebinding `inc = dec` sits in an IMPORTED module (`multi_file_lib/r119_rebindlib.py`). Route #118's refusal lived in `pycsl._run_pipeline`, which imported dependencies never pass through (`ir_resolve` runs its own Module 1-3-5), so `inc(3)` PROVED `\result == 4` while CPython returns 2. The refusal now lives in Module3_Weaver.process, shared by both pipelines.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from multi_file_lib.r119_rebindlib import inc


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return inc(3)
