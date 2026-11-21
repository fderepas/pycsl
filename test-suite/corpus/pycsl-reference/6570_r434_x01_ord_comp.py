r"""Test 6570 -- route #434 (expected FAIL): `[ord(w) for w in ws]` under `no_exception \all`, f(["ab"]) (CPython TypeError): the comprehension is lowered opaque, so the driver's site census REFUSES it (`PYCSL-R434-UNCHECKED-SITE`). PROVED at base 78b519f63.
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(ws: list[str]) -> int:
    xs = [ord(w) for w in ws]
    return 0


if __name__ == "__main__":
    try:
        print("result", f(["ab"]))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
