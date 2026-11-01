r"""Test 8026 -- route #506 (control, expected PASS): un-claimed g evaluates `t = (1, 10 // n)`, but no handler in the file can catch ZeroDivisionError (f catches KeyError only) and nothing claims it, so the dropped element is unobservable by any proved claim; CPython f(4) returns 5)
"""
# pycsl-expected: PASS

#@ ensures \result == n + 1
def g(n: int) -> int:
    t = (1, 10 // n)
    return n + 1


#@ ensures \result == n + 1
def f(n: int) -> int:
    try:
        return g(n)
    except KeyError:
        return 0


if __name__ == "__main__":
    print("result", f(4))
