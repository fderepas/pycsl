r"""Test 8300 -- route #510 residual (control, expected PASS): the dependency's module-scope `type Vec = list[int]` rebinds no value it exports; this file imports `Vec` and reads it only as an annotation, and calls the dependency's `inc`; CPython f(4) returns 5
"""
# pycsl-expected: PASS
from multi_file_lib.u12_r510_ctl import Vec, inc


#@ ensures \result == n + 1
def f(n: int, xs: Vec) -> int:
    return inc(n)


if __name__ == "__main__":
    print(f(4, [1]))
