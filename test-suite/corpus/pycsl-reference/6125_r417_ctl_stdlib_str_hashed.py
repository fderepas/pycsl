r"""Test 6125 -- route #417 (expected PASS): CONTROL: `{os.path.join("a", "b")}` and `{os.path.join("x", "y"): 1}` (stdlib functions on the str allow-list) under `no_exception \all` (CPython ok). PROVED at base and candidate.
"""
# pycsl-expected: PASS
import os


#@ no_exception \all
def f() -> int:
    s = {os.path.join("a", "b")}
    d = {os.path.join("x", "y"): 1}
    return 0


if __name__ == "__main__":
    print(f())
