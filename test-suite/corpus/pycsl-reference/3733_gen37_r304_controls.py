r"""Test 3733 -- gen #37 route #304 (expected PASS): CONTROLS -- own raises route #304 keeps proving: a raise DEAD under the precondition (named and `\all`, function and method), a raise caught by an enclosing handler of the same function (named and `\all`), a raise OUTSIDE a named `no_exception` set (a builtin `KeyError` and a user class `Unrel(Exception)` under `no_exception ValueError`, each with its declared `#@ raises ... when x < 0`: a covered class would be wrapped AND declared and fail), a declared `#@ raises ValueError when x < 0` without `no_exception`, and a `no_exception \all` caller of a guarded raiser. All honest; must still PROVE.
"""


class Unrel(Exception):
    pass


#@ requires x >= 0
#@ no_exception ValueError
#@ ensures \result == 0
def guarded_named(x: int) -> int:
    if x < 0:
        raise ValueError("neg")
    return 0


#@ requires x >= 0
#@ no_exception \all
#@ ensures \result == 0
def guarded_all(x: int) -> int:
    if x < 0:
        raise RuntimeError("neg")
    return 0


#@ no_exception \all
#@ ensures \result == 9 or \result == 0
def caught_all(x: int) -> int:
    try:
        if x < 0:
            raise ValueError("neg")
    except ValueError:
        return 9
    return 0


#@ no_exception ValueError
#@ ensures \result == 9 or \result == 0
def caught_named(x: int) -> int:
    try:
        if x < 0:
            raise ValueError("neg")
    except ValueError:
        return 9
    return 0


#@ no_exception ValueError
#@ raises KeyError when x < 0
#@ ensures \result == 0
def outside_named(x: int) -> int:
    if x < 0:
        raise KeyError("neg")
    return 0


#@ no_exception ValueError
#@ raises Unrel when x < 0
#@ ensures \result == 0
def outside_named_user(x: int) -> int:
    if x < 0:
        raise Unrel()
    return 0


#@ raises ValueError when x < 0
#@ ensures \result == 0
def declared(x: int) -> int:
    if x < 0:
        raise ValueError("neg")
    return 0


#@ no_exception \all
#@ ensures \result == 0
def caller(y: int) -> int:
    return guarded_all(y * y)


class C:
    def __init__(self) -> None:
        self.v: int = 0

    #@ requires x >= 0
    #@ no_exception \all
    #@ ensures \result == 0
    def m(self, x: int) -> int:
        if x < 0:
            raise ValueError("neg")
        return 0


if __name__ == "__main__":
    assert guarded_named(1) == 0
    assert guarded_all(1) == 0
    assert caught_all(-1) == 9
    assert caught_named(-1) == 9
    assert outside_named(1) == 0
    assert outside_named_user(1) == 0
    assert declared(1) == 0
    assert caller(-3) == 0
    assert C().m(1) == 0
