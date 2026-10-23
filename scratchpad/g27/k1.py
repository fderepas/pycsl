r"""K1 — deferral census #1: a derived @dataclass. `init_params` is synthesized from THIS
class's AnnAssigns only and `ir_resolve` merges fields but not `init_params`, so a legal
`C(1, 2)` is 'over-arity' to the model and every field falls to its definite default."""
from dataclasses import dataclass

_ = 0  # anchor


@dataclass
class B:
    a: int


@dataclass
class C(B):
    b: int


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = C(1, 2)
    return c.b
