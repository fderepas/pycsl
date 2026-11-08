r"""Test 7682 -- routes #483 / #484 CONTROL (expected PASS: PROVED at base and candidate): a dependency instantiates its own class at import; its `__init__` stores only instance fields of `self` and reads `getattr(self, "v", 0)` with a literal name.
"""
# pycsl-expected: PASS
import multi_file_lib.y2_c484c
K = 1


#@ ensures \result == n
def f(n: int) -> int:
    return n * K


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
