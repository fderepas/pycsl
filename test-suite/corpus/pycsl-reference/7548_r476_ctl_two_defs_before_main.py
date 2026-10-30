r"""Test 7548 -- route #476 control (expected PASS): c2_two_defs_before_main -- two defs of `g` both BEFORE the guard: the live binding at the frontier is the last one, which the model uses; stays admitted.
"""
def g(x: int) -> int:
    return 1 // (x - x)


def g(x: int) -> int:
    return x


#@ no_exception \all
#@ ensures \result == n
def f(n: int) -> int:
    return g(n)


if __name__ == "__main__":
    print(f(1))
