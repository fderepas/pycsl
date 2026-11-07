r"""Test 5070 -- gen #37 route #375 (expected FAIL): `t = self; t *= 2` under `no_exception \all`; PROVED at base (TypeError). FAILS now.
"""
# pycsl-expected: FAIL
class W:
    #@ no_exception \all
    def m(self) -> int:
        t = self
        t *= 2
        return 0

if __name__ == "__main__":
    print(W().m())
