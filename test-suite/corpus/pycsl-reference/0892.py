"""Test 0892 — compound-key const-map `.get(k, [])` → list-of-tuple (FAITHFUL).

compound-key-const-map lowering. A module-level CONSTANT dict whose key is a
COMPOUND (tuple) type `Tuple[str, Optional[str]]` and whose value is a
`List[<tuple>]` (`TRIGGERS`, mirroring `exception_model.py`) lowers FAITHFULLY,
NOT to an opaque int:

  - the constant becomes an opaque Why3 map constant
        val constant tRIGGERS : map (string, option string)
                                    (option (list (string, string)))
    (content UNMODELLED — sound under the weak `ensures True` contract — but the
    TYPE is faithful: native tuple key, `option`-wrapped list-of-tuple value);
  - the key parameter `op_key: Tuple[str, Optional[str]]` is the native WhyML
    tuple `(string, option string)`;
  - the return `List[Trigger]` is the PURE, immutable `list (string, string)`
    (`array <record>` would be Why3-rejected for a mutable element);
  - `TRIGGERS.get(op_key, [])` lowers to the real defaulting lookup
        (match Map.get tRIGGERS op_key with Some l_ -> l_ | None -> Nil end)
    — the `[]` default is `Nil`, the honest missing-key result.

This proves under `ensures True` (the body is a well-typed `list (string,
string)`) and is faithful: the return IS the defaulting map lookup, not a
dropped/opaque-int stub. `map`/`option`/`list`/tuples are Why3 stdlib and an
opaque `val constant` is not an axiom — no TCB growth.

The recognizer is TIGHTLY GATED on the tuple-key + list-value shape, so a plain
`Dict[str, int]` const dict is unaffected (the full reference corpus stays
byte-identical).
"""
_ = 0  # anchor
from typing import Dict, List, Optional, Tuple

Trigger = Tuple[str, str]

TRIGGERS: Dict[Tuple[str, Optional[str]], List[Trigger]] = {
    ("binop", "div"):      [("ZeroDivisionError", "no_div_zero ({1})")],
    ("subscript", "read"): [("IndexError",        "in_bounds ({0}) ({1})")],
    ("map_get", None):     [("KeyError",          "Map.get {0} {1} <> None")],
}


#@ requires True
#@ ensures True
#@ assigns \nothing
def triggers_for(op_key: Tuple[str, Optional[str]]) -> List[Trigger]:
    """Return the list of (exception, trigger_template) pairs for an IR
    operation key. Empty list means the operation cannot raise."""
    return TRIGGERS.get(op_key, [])


if __name__ == "__main__":
    assert triggers_for(("binop", "div")) == [("ZeroDivisionError", "no_div_zero ({1})")]
    assert triggers_for(("attr_call", "pop")) == []
