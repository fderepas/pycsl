#@ requires True
#@ ensures \result == x
def f(x: "Foo") -> "Foo":
    return x


class Foo:
    pass
