r"""M7 — `@dataclass(kw_only=True)`: EVERY field is KEYWORD-ONLY, so the synthesized
`__init__` binds nothing positionally. The model puts them in the POSITIONAL list."""
from dataclasses import dataclass

_ = 0  # anchor


@dataclass(kw_only=True)
class Pee:
    xfld: int = 0
    yfld: int = 0


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    p = Pee(yfld=1, xfld=2)
    return p.yfld
