r"""Test 4809 -- gen #37 route #358 (expected FAIL): witness r14: `if self:` with `__len__` returning -1 under `no_exception \all` (lowered `self <> 0`); PROVED (CPython ValueError). FAIL (PyCSL-R358 truth test of an erased value).
"""
# pycsl-expected: FAIL
class P:
    def __len__(self) -> int:
        return -1

    #@ no_exception \all
    def m(self) -> int:
        if self:
            return 1
        return 0


if __name__ == "__main__":
    try:
        P().m()
        assert False, "expected ValueError"
    except ValueError:
        pass
