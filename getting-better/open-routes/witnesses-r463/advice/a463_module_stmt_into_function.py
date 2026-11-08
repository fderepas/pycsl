# advice of the module-level-claim refusal followed on witness 7190: the code and its claim moved into a function.
#@ ensures \result == 2
def main() -> int:
    x = 1
    #@ assert x == 1
    y = x + 1
    return y
