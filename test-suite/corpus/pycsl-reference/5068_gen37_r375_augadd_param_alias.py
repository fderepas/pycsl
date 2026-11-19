r"""Test 5068 -- gen #37 route #375 (expected FAIL): `t = w; t += 1` on a field-less-class parameter; PROVED at base (TypeError). FAILS now.
"""
# pycsl-expected: FAIL
class W:
    pass

#@ no_exception \all
def f(w: W) -> int:
    t = w
    t += 1
    return 0

if __name__ == "__main__":
    print(f(W()))
