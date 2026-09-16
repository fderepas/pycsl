r"""Test 1536 - ROUTE #158 (gen #29): `xs = []; all(x > 0 for x in xs)` - the local carries the placeholder; `\result != 1` PROVED; CPython 1.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result != 1
def probe() -> int:
    xs = []
    return 1 if all(x > 0 for x in xs) else 0

