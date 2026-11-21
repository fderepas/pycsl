r"""N1 — a @dataclass class-body default that is NOT an ast.Constant: `-7` is a
UnaryOp, so the field gets NO entry in field_defaults and `_field_default` hands back
the DEFINITE literal 0. This is route #139's miss one level up: gen #27 repaired the
`__init__`-body collector, not the class-body one."""
from dataclasses import dataclass

_ = 0  # anchor


@dataclass
class Pee:
    xfld: int = -7


#@ ensures \result == -7
#@ assigns \nothing
def probe() -> int:
    p = Pee()
    return p.xfld
