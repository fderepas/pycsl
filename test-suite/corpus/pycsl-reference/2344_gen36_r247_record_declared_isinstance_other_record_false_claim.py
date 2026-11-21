r"""Test 2344 — route #247 (expected FAIL): every record class has the one tag `tag_record`, so a subject
declared `pa` decided `isinstance(r, pb)` TRUE (`(5 = 5)`); `\result == 1` PROVED at afe28c69. CPython
`f(pa(1))` = 0. A record/variant tag now decides only for the SAME declared class.
"""
# pycsl-expected: FAIL


class pa:
    def __init__(self, v: int) -> None:
        self.v = v


class pb:
    def __init__(self, v: int) -> None:
        self.v = v


#@ ensures \result == 1
#@ assigns \nothing
def f(r: pa) -> int:
    if isinstance(r, pb):
        return 1
    return 0


if __name__ == "__main__":
    assert f(pa(1)) == 0
