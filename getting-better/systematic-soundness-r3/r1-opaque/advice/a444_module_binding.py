# Advice probe (route #444): witness 6852 with the global bound at module level (`LATE = ...`).
LATE = 2


#@ no_exception \all
def f(a: int) -> int:
    return a + LATE
