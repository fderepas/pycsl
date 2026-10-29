# Advice probe (route #458): witness 6867 with both operands declared of one class (`n: str`).
#@ no_exception \all
def f(n: str, s: str) -> int:
    return len(n + s)
