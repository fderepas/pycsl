r"""Test 8439 -- route #528 (control, expected PASS): `w.split()[0] if w.split() else w` and `w.split()[-1] if w.split() else w` -- the true arm of a truth test of the same no-arg split of a plain name keeps its lowering (no `no_exception` claim: route #72 refuses a no-arg split under a ValueError claim); CPython returns 4 / 2
"""
# pycsl-expected: PASS


#@ ensures \result >= 0
def f(w: str) -> int:
    a = w.split()[0] if w.split() else w
    b = w.split()[-1] if w.split() else w
    return len(a) + len(b)


if __name__ == "__main__":
    print("result", f("  "), f("x y"))
