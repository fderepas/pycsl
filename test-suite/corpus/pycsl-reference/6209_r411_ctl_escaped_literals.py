r"""Test 6209 -- route #411 (expected PASS): CONTROL: escaped literals have their Python lengths and characters: `len("é") == 1`, `len("\n") == 1`, `len("a\"b") == 3`, `len("a\\b") == 3`, `len("é" + s) == len(s) + 1`, `s[0]` of `"é"` raises nothing, `len("x\t") == 2`, `"\n" != "\r"` (CPython agrees). FAILED at base 77b33f239 (each such literal was 4 characters per escape to Z3), PROVED after the repair.
"""
# pycsl-expected: PASS
#@ ensures \result == 1
def f1() -> int:
    t = "é"
    return len(t)


#@ requires s == "\n"
#@ ensures \result == 1
def f2(s: str) -> int:
    return len(s)


#@ requires s == "a\"b"
#@ ensures \result == 3
def f3(s: str) -> int:
    return len(s)


#@ requires s == "a\\b"
#@ ensures \result == 3
def f4(s: str) -> int:
    return len(s)


#@ ensures \result == True
def f5(s: str) -> bool:
    t = "é" + s
    return len(t) == len(s) + 1


#@ requires s == "é"
#@ no_exception \all
def f6(s: str) -> str:
    return s[0]


#@ ensures \result == 2
def f7() -> int:
    t = "x\t"
    return len(t)


#@ ensures \result == True
def f8() -> bool:
    t = "\n"
    u = "\r"
    return t != u

if __name__ == "__main__":
    print(f1(), f2("\n"), f3("a\"b"), f4("a\\b"), f5("ab"), f6("é"), f7(), f8())
