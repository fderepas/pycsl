# Advice probe (route #499): witness 7924's exec moved to module level, as advised (= control 7931).
exec("y = 6")


#@ ensures \result == 6
#@ assigns \nothing
def f() -> int:
    return y


if __name__ == "__main__":
    assert f() == 6
