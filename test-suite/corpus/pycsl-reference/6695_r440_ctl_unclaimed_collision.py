r"""Test 6695 -- route #440 (expected PASS): CONTROL: the table is consulted only under a `no_exception` claim: an UNCLAIMED function calling `path.rindex("")` (no row; it never raises: CPython returns `len(path)`) with a file `rindex` name in scope is not judged, and its `ensures \result >= 1` proves (not a tail-`return`-only `== <int>` contract, check-vacuous-drivers; CPython ok on the driver's input).
"""
# pycsl-expected: PASS


class Buffer:
    #@ ensures \result == 0
    def rindex(self, v: int) -> int:
        return 0


#@ ensures \result >= 1
def one(path: str) -> int:
    path.rindex("")
    return 1


if __name__ == "__main__":
    print(one("a.b"))
