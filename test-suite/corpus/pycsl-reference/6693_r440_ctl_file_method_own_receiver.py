r"""Test 6693 -- route #440 (expected PASS): CONTROL: a file class `Buffer` defines `rindex`; `b.rindex(v)` on a receiver DERIVED `Buffer` is admitted (the file method's own contract speaks for it), under `#@ no_exception \all`. PROVED at candidate (CPython ok).
"""
# pycsl-expected: PASS


class Buffer:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result == 0
    def rindex(self, v: int) -> int:
        return 0


#@ no_exception \all
#@ ensures \result == 0
def last(b: Buffer, v: int) -> int:
    return b.rindex(v)


if __name__ == "__main__":
    print(last(Buffer(), 3))
