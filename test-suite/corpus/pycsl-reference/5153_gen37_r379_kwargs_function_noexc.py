r"""Test 5153 -- gen #37 route #379 (expected FAIL): a plain function call `h(1, **{"y": 5})` under `no_exception` (CPython TypeError). PROVED at base b815ee8d8.
"""
# pycsl-expected: FAIL
#@ assigns \nothing
def h(x: int) -> int:
    return x

#@ no_exception \all
def f() -> int:
    kw = {"y": 5}
    return h(1, **kw)

if __name__ == "__main__":
    print(f())
