#@ requires True
#@ ensures \result == x
def f_before(x: Foo) -> Foo:
    return x


class Foo:
    pass
