"""WL-03 COLLAPSED/WRONG-REPR — a `Tuple[T1,...]` PARAMETER collapses to bare `int`
(opaque `subscript_get`), losing slot structure, though the tau-table claims
tau(Tuple[T1,...]) = tuple (the faithful model is realized only for LOCAL/returned
tuples, NOT params/fields).

Detector D2/D3:
  * mixed-slot `Tuple[int,str]` param: `t[1]` (should be str) -> opaque int at a
    `string` return -> TYPEERR (this file).
  * all-int `Tuple[int,int]` param: body `t[0]` is opaque `subscript_get` (content
    UNPROVABLE), and a contract-side `\result == t[0]` is itself ill-typed.
Compare wl03_tuple_local_FAITHFUL.py (a locally-constructed tuple IS faithful)."""
_ = 0
from typing import Tuple
#@ ensures \result == t[1]
def f(t: Tuple[int, str]) -> str:
    return t[1]
