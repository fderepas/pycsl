# route #503 advice 'Write `==` if you mean equality': witness b60100 with `is` -> `==`.
#@ ensures \result == True
def f(n: int) -> bool:
    a = n + 1000
    b = a
    a = n + 1000
    return a == b
