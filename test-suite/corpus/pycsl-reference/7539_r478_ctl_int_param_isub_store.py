r"""Test 7539 -- route #478 control (expected PASS) under `--memory-model store`: `n -= 1` on an INT parameter is a faithful local rebinding and stays admitted (PROVED at 8aaa864ca and now).
"""
# pycsl-flags: --memory-model store
#@ requires n >= 1
#@ ensures \result == n - 1
#@ assigns \nothing
def f(n: int) -> int:
    n -= 1
    return n
