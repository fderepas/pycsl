r"""Test 5069 -- gen #37 route #375 (expected FAIL): `{*self}` under `no_exception \all`: the display was replaced by an opaque value without its starred element; PROVED (TypeError). FAILS now.
"""
# pycsl-expected: FAIL
class W:
    #@ no_exception \all
    def m(self) -> int:
        s = {*self}
        return 0

if __name__ == "__main__":
    print(W().m())
