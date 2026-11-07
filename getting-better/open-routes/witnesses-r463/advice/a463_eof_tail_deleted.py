# advice of the end-of-file refusal followed on witness 7188: the column-0 trailing line deleted.
#@ ensures \result == n
def f(n: int) -> int:
    x = n
    return x
    #@ assert 1 == 1
