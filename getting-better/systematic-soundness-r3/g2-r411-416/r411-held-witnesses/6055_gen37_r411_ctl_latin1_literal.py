r"""Test 6055 -- gen #37 route #411 (expected PASS): CONTROL: a Latin-1 literal is one Char per code point: `len("é") == 1`, `t[0] == "é"`, `"é" + s` has length `1 + len(s)`, and `t[0]` under `no_exception \all` (CPython agrees). PROVED at candidate (at base `len == 1` failed: the literal was two bytes).
"""
# pycsl-expected: PASS
#@ ensures \result == 1
def f() -> int:
    t = "é"
    return len(t)


#@ ensures \result == True
def g() -> bool:
    t = "é"
    return t[0] == "é"


#@ ensures \result == True
def h(s: str) -> bool:
    t = "é" + s
    return len(t) == len(s) + 1


#@ no_exception \all
def k() -> str:
    t = "aé"
    return t[1]


if __name__ == "__main__":
    print(f(), g(), h("ab"), k())
