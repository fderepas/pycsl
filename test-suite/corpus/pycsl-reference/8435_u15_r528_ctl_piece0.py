r"""Test 8435 -- route #528 (control, expected PASS): `len(s.split(",")[0])`: a non-empty literal separator always yields at least one piece, so `[0]` keeps its lowering (byte-identical); CPython returns 2 / 1
"""
# pycsl-expected: PASS
#@ no_exception \all
#@ ensures \result >= 0
def f(s: str) -> int:
    return len(s.split(",")[0])


if __name__ == "__main__":
    print("result", f("ab"), f("a,b"))
