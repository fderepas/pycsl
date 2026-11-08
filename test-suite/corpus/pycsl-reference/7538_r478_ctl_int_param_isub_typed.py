r"""Test 7538 -- route #478 control (expected PASS) under `--memory-model typed`: `n -= 1` on an INT parameter is a faithful local rebinding and stays admitted (PROVED at 8aaa864ca and now).
"""
# pycsl-flags: --memory-model typed
#@ requires n >= 1
#@ ensures \result == n - 1
#@ assigns \nothing
def f(n: int) -> int:
    n -= 1
    return n
