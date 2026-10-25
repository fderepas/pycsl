r"""Test 5071 -- gen #37 route #375 (expected FAIL): NEW shape: `(*self,)` under `no_exception \all` (TypeError). FAILS now.
"""
# pycsl-expected: FAIL
class W:
    #@ no_exception \all
    def m(self) -> int:
        t = (*self,)
        return 0

if __name__ == "__main__":
    print(W().m())
