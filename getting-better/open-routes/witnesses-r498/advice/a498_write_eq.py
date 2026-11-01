# Advice probe (route #498): witness 7900 with `is` replaced by `==`, as the refusal advises.
#@ ensures \result == True
def f(n: int) -> bool:
    return (n + 1) == (n + 1)


if __name__ == "__main__":
    assert f(1000) == True
