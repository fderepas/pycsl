r"""Test 7547 -- route #476 control (expected PASS): c1_def_after_main_unread -- a def after the guard that no verified function reads stays admitted.
"""
def g(x: int) -> int:
    return x + 1


#@ ensures \result == n + 1
def f(n: int) -> int:
    return g(n)


if __name__ == "__main__":
    print(f(1))


def h(x: int) -> int:
    return x
