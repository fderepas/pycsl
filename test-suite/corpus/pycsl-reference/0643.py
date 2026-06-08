"""Test 0643 — the exec splice rejects control flow, fail-loud (07-1839 P5b).

The splice admits only straight-line assignments / pure expressions; admitting control flow would
change the CFG and break inline-equivalence. `exec("if …")` is therefore REJECTED with a parse error
rather than silently mis-modelled.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare


#@ assigns \nothing
def f() -> int:
    exec("if True:\n    x = 1")
    return 0
