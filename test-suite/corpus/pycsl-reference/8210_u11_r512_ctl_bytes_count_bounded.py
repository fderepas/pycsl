r"""Test 8210 -- route #512 (control, expected PASS): `bytearray(n)` / `bytes(n)` as plain statements under `requires 0 <= n <= 1000` (the count form's Py_ssize_t assert discharges), read, and the read put in a dict display; CPython f(5) returns 1
"""
# pycsl-expected: PASS


#@ requires 0 <= n and n <= 1000
#@ no_exception \all
#@ ensures \result == 1
def f(n: int) -> int:
    b = bytearray(n)
    c = bytes(n)
    k = 0
    if n > 0:
        k = b[0] + c[0]
    v = {"k": k}
    return 1


if __name__ == "__main__":
    print(f(5))
