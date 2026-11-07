# route #518 advice followed: witness 8160 with the default's value bound in a statement of its
# own (`T = 0`) before the lambda and the plain name used in the default; K is no longer
# rebound, so CPython's f() is 5, as claimed (= control 8171).
K = 5
T = 0
_l = lambda a=T: a


#@ ensures \result == 5
def f() -> int:
    return K


if __name__ == "__main__":
    print(f())
