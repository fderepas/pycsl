"""Test 0872 — module-const-dict-get faithful lowering lock (POSITIVE).

Locks the module-level constant str->str dict `.get(k, default)` recognizer. A
top-level `OP_MAP = {"==":"=", ...}` read via `OP_MAP.get(k, default)` lowers to a
FAITHFUL chained string-valued if-then-else
    (if k = "==" then "=" else if k = "!=" then "<>" else ... else default)
— exactly the `OP_MAP.get(op, op)` shape in `identifiers.op_translate`, whose string
argument previously leaked to an opaque int `val`.

Two laws:
  (HIT)     OP_MAP.get("==", "==") == "="   — a matched key returns its mapped value.
  (DEFAULT) OP_MAP.get("zzz", "zzz") == "zzz" — an absent key returns the default.
Both discharge (best-of-N: Z3's native string theory decides the literal
disequality on the fall-through arms). NO new axiom, NO `\trusted`.
"""
OP_MAP = {
    "==": "=",
    "!=": "<>",
    "//": "div",
    "%": "mod",
}


#@ ensures \result == "="
def translate_hit() -> str:
    """OP_MAP.get("==", "==") == "=" — matched-key hit returns the mapped value."""
    return OP_MAP.get("==", "==")


#@ ensures \result == "zzz"
def translate_default() -> str:
    """OP_MAP.get("zzz", "zzz") == "zzz" — absent-key read returns the default."""
    return OP_MAP.get("zzz", "zzz")


if __name__ == "__main__":
    assert translate_hit() == "="
    assert translate_default() == "zzz"
