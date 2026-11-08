r"""Test 7574 -- route #474 residual CONTROL (expected PASS: PROVED at base and candidate): a package whose `__init__` only imports `sub`; `K = 1` still folds.
"""
# pycsl-expected: PASS
from multi_file_lib.f2_p474c.sub import K


#@ ensures \result == 1
def f(n: int) -> int:
    return K


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
