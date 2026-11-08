r"""Test 7573 -- route #474 residual CONTROL (expected PASS: PROVED at base and candidate): `from f2_h474c import K`, no program module writes it, so `K = 1` still folds.
"""
# pycsl-expected: PASS
from multi_file_lib.f2_h474c import K


#@ ensures \result == 1
def f(n: int) -> int:
    return K


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
