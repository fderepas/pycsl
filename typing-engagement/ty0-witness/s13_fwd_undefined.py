#@ requires True
#@ ensures \result == x
def f(x: "Baz") -> "Baz":
    return x
