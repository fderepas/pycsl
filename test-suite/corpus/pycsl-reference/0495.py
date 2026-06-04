"""Test 0495 — class: parametrized construction via __init__ (base_op.md Tier A).

`C(a, b)` now constructs a record whose scalar fields are initialised from the __init__ body's
`self.x = <expr over params>` assignments with the actual args substituted — previously `C(args)`
was an opaque int op that ignored the arguments. Here `Point(2, 3)` builds `{x = 2; y = 2 + 3}`,
so reading `.y` discharges `\result == 5`. Only scalar (int) fields take a substituted value;
list/dict fields and inits that touch a non-param (a local, a method call, another field) keep
their default witness."""
_ = 0  # anchor
class Point:
    def __init__(self, a: int, b: int):
        self.x = a
        self.y = a + b


#@ ensures \result == 5
def make() -> int:
    p = Point(2, 3)
    return p.y
