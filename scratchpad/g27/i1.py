r"""I1 — ladder (c): the VACUOUS row owed a re-probe. `_emit_option_tuple_unpack`'s docstring
asserts "the Python guard `if X is not None:` makes the `None` arm dead", and the emitter NEVER
CHECKS for a guard. Here there is NO guard and the option IS None at run time."""
from typing import Optional, Tuple

_ = 0  # anchor


class C:
    n: int

    def __init__(self) -> None:
        self.n = 0

    #@ assigns \nothing
    def info(self) -> Optional[Tuple[int, int]]:
        return None

    #@ ensures \result == 7
    #@ assigns \nothing
    def probe(self) -> int:
        p = self.info()
        a, b = p
        return a + b
