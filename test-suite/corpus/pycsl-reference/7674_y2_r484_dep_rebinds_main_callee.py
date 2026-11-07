r"""Test 7674 -- route #484 (expected FAIL: PROVED at base, REFUSED): a dependency rebinds this file's callee (`m.g = lambda x: 0` through `import __main__ as m`); CPython returns 0.
"""
# pycsl-expected: FAIL
def g(x: int) -> int:
    return x


import multi_file_lib.y2_h484b


#@ ensures \result == n
def f(n: int) -> int:
    return g(n)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
