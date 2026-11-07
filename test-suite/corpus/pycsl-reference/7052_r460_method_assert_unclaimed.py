r"""Test 7052 -- route #460 (expected FAIL): an UN-claimed METHOD `Acc.take` asserting its argument, reached from `run` claiming `#@ no_exception \all` through `a.take(n)` (CPython AssertionError for run(-3)). PROVED at base 370db7dc2; now FAILS.
"""
# pycsl-expected: FAIL


class Acc:
    def __init__(self) -> None:
        self.total = 0

    def take(self, n: int) -> int:
        assert n >= 0
        return n + 1


#@ no_exception \all
def run(n: int) -> int:
    a = Acc()
    return a.take(n)


if __name__ == "__main__":
    print("result", run(-3))  # CPython: AssertionError
