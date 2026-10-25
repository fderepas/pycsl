r"""Test 4814 -- gen #37 route #358 (expected FAIL): witness r46: `not self` with `__len__` returning -1 under `no_exception \all`; PROVED (CPython ValueError). FAIL (PyCSL-R358 truth test).
"""
# pycsl-expected: FAIL
class P:
    def __len__(self) -> int:
        return -1

    #@ no_exception \all
    def m(self) -> bool:
        return not self


if __name__ == "__main__":
    try:
        P().m()
        assert False, "expected ValueError"
    except ValueError:
        pass
