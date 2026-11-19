# advice of the trailing-`#@` refusal followed on witness 7186: the assert on its own line after the statement.
#@ ensures \result == n
def f(n: int) -> int:
    y = n + 1
    #@ assert y == n + 1
    return n
