r"""Test 9611 -- route #589 CONTROL (expected PASS): dropped arguments that cannot raise -- literals, a negated number, a tuple display, a parameter, and a local assigned earlier in the SAME try block -- are not refused; the handler path computes the result.
"""
# pycsl-expected: PASS
class E(Exception):
    pass


#@ no_exception \all
#@ ensures \result == k + 2
def f(k: int) -> int:
    try:
        w = k + 1
        raise E("a", 1, -2, (3, "b"), k, w)
    except E:
        return k + 2
    return 0


if __name__ == "__main__":
    print(f(3))
