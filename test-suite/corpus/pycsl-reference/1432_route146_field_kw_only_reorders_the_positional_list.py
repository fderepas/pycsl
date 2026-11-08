r"""Test 1432 - ROUTE #146: `field(kw_only=True)` makes exactly that field keyword-only, so the OTHER field becomes Python's FIRST positional parameter. The model kept both in `init_params`, bound `xfld` from the 5, let the explicit `xfld=1` keyword overwrite it, and left `yfld` on its default: `\result == 0` PROVED while CPython returns 5. Keyword-only fields now leave on route #82's by-name channel.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field

_ = 0  # anchor


@dataclass
class Pee:
    xfld: int = field(kw_only=True, default=0)
    yfld: int = 0


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    p = Pee(5, xfld=1)
    return p.yfld
