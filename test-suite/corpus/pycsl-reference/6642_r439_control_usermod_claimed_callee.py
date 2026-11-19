r"""Test 6642 -- route #439 (expected PASS): CONTROL: a `no_exception \all` caller of imported user-module functions that CLAIM `no_exception \all` (hashing a `str`) or hash nothing (`int` arithmetic) is not refused. PROVED at base and candidate.
"""
# pycsl-expected: PASS
from multi_file_lib.r439_okhash import hs, inc

#@ no_exception \all
#@ ensures \result == n + 2
def f(k: str, n: int) -> int:
    return hs(k, n) + inc(n) - n


if __name__ == "__main__":
    try:
        r = f("a", 1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
