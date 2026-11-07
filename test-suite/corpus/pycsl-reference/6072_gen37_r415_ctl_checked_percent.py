r"""Test 6072 -- gen #37 route #415 (expected PASS): CONTROL: allow-listed `%` formatting under `no_exception \all`: a literal format with only %d / %s / %r / %%, a tuple display of one operand per directive of a matching static type (int for %d, bounded for route #281's 4300-digit row; int / str / float for %s / %r), and a single str operand for a one-directive format (CPython ok). PROVED at base and candidate.
"""
# pycsl-expected: PASS
#@ requires -1000 <= a and a <= 1000
#@ no_exception \all
def f(a: int, s: str, x: float) -> str:
    return "%d-%s-%r %% %s" % (a, s, x, a)


#@ no_exception \all
def g(s: str) -> str:
    return "<%s>" % s


if __name__ == "__main__":
    print(f(1, "a", 2.5), g("b"))
