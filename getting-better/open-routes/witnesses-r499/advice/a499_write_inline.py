# Advice probe (route #499): witness 7920 with the exec'd statement written inline, as advised.
#@ ensures \result == 2
def f(n: int) -> int:
    x = 1
    x = 2
    return x


if __name__ == "__main__":
    assert f(0) == 2
