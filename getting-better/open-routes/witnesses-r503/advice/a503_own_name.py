# route #503 advice 'give the rebound value its own name, so that the alias's root is bound
# once': witness b60100 with the second binding renamed; `a is b` is now one object.
#@ ensures \result == True
def f(n: int) -> bool:
    a = n + 1000
    b = a
    a2 = n + 1000
    return a is b
