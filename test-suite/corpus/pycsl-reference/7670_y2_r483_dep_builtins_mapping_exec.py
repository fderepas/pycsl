r"""Test 7670 -- route #483 (expected FAIL: PROVED at base, REFUSED): the dependency rebinds its constant through its `__builtins__` MAPPING (`__builtins__['exec']('K = 0')`) while `from y2_h483a import K` folds `K = 1` under an ensures-only claim; CPython returns 0.
"""
# pycsl-expected: FAIL
from multi_file_lib.y2_h483a import K


#@ ensures \result == n
def f(n: int) -> int:
    return n * K


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
