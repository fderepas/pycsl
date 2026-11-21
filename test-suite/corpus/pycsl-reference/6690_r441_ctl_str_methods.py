r"""Test 6690 -- routes #440 / #441 (expected PASS): CONTROL: `str` methods with rows in the signature table, on receivers and arguments DERIVED `str` / `int` / a tuple of `str` (`strip`, `lower`, `replace`, `split` with a literal separator, `startswith` of a tuple of `str`, `count`, `find`), each under `#@ no_exception \all`. Admitted; PROVED at candidate (CPython ok).
"""
# pycsl-expected: PASS


#@ no_exception \all
def f1(s: str, t: str) -> int:
    return len(s.strip()) + len(s.lower()) + len(s.replace("a", t))


#@ no_exception \all
def f2(s: str) -> int:
    return len(s.split(","))


#@ no_exception \all
def f3(s: str) -> int:
    return 1 if s.startswith(("a", "b")) else 0


#@ no_exception \all
def f4(s: str, t: str) -> int:
    return s.count(t) + s.find(t)


if __name__ == "__main__":
    print(f1(" Ab ", "b"), f2("a,b"), f3("ab"), f4("abb", "b"))
