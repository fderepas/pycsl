# advice of the orphan-header refusal followed on witness 7189: the claim moved above the construct (into a function).
def g() -> int:
    x = 1
    y = x
    #@ assert y == 1
    return y
