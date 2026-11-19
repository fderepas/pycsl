r"""Test 6868 -- routes #441 / #444-#458 callee reach (expected FAIL): a claimed `f` calls an UNclaimed `g` whose `len(n)` on an `int` raises TypeError; route #441's signature table judged only the claiming function, so `#@ no_exception \all` PROVED on main db6c57253. Refused PYCSL-R441-BUILTIN-SIGNATURE (the caller's claim reaches `g`).
"""
# pycsl-expected: FAIL


def g(n: int) -> int:
    return len(n)


#@ no_exception \all
def f(n: int) -> int:
    return g(n)


if __name__ == "__main__":
    try:
        print("result", f(1))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
