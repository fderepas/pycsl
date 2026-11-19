r"""Test 6680 -- route #440 A1 (expected FAIL): a file class defines `rindex`; `path.rindex(".")` on a `str` under `#@ no_exception ValueError` only. The builtin `str.rindex` has no row in the signature table (its ValueError is not modelled), so it is refused under ANY claim, as route #161 refuses an unlisted callee; CPython raises ValueError (the `__main__` driver prints VIOLATION). REFUSED (PYCSL-R440-METHOD-NOT-ADMITTED).
"""
# pycsl-expected: FAIL


class Buffer:
    def rindex(self, v: int) -> int:
        return 0


#@ no_exception ValueError
def last_dot(path: str) -> int:
    return path.rindex(".")


if __name__ == "__main__":
    try:
        r = last_dot("README")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
