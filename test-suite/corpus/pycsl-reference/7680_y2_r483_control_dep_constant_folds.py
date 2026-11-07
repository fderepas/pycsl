r"""Test 7680 -- routes #483 / #484 CONTROL (expected PASS: PROVED at base and candidate): the dependency binds `K = 3` once and runs only allow-listed code (`math.floor`) at import, so `from y2_c483a import K` still folds.
"""
# pycsl-expected: PASS
from multi_file_lib.y2_c483a import K


#@ ensures \result == 3 * n
def f(n: int) -> int:
    return n * K


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
