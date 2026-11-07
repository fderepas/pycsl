# Route #527 advice probe: witness g1026_ah1000_concat with the operand narrowed first
# (`if r.s is not None:`), as PYCSL-R527-OPTIONAL-OPERAND advises.
from typing import Optional
from dataclasses import dataclass


@dataclass
class R:
    s: Optional[str]
    t: str


#@ no_exception \all
def f(r: R) -> int:
    if r.s is not None:
        w = r.s + "x"
    return 1


if __name__ == "__main__":
    print("result", f(R(None, "ab")), f(R("q", "ab")))
