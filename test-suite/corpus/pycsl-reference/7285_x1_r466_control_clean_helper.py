r"""Test 7285 -- route #466 CONTROL (expected PASS: PROVED at base and candidate): the imported helper's top level is clean (constants, a dataclass with `field(default_factory=list)`, a def).
"""
# pycsl-expected: PASS
from multi_file_lib.x1_hc466 import g


#@ no_exception \all
#@ ensures \result == n + 1
def f(n: int) -> int:
    return g(n)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
