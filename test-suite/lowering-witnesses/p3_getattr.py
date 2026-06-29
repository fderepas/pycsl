"""Witness driver — Pattern 3: `getattr(obj, name, default)`.

Previously `getattr(self, "_x", 0)` fell through to an opaque `getattr_N`
abstract val that mismatched on record-typed `self` ("unbound symbol self" /
type @rho mismatch). Fix (expressions.py `_lower_getattr`):

  • If `obj` is a Var of a known record type and `name` is a string literal
    matching a declared field → emit the genuine record field access
    `obj.<field>` (so `\result == self.f` postconditions can prove).
  • Otherwise (the dynamic-config case `getattr(self, "_x", {})` where `_x`
    isn't a declared field) → emit the `default` argument. getattr DOES return
    `default` for an absent attribute, so this is sound (the real runtime
    value is opaque; fails-safe). A non-scalar default (dict/list/set) is
    coerced to `0` so the enclosing int-typed `ref` slot type-checks — the
    collection content is then unmodeled (a `.get` chain on it will not prove).
"""
#@ class invariant self.v >= 0
class Cfg:
    def __init__(self) -> None:
        self.v: int = 0


#@ requires True
#@ ensures True
def getattr_known_field(self: Cfg) -> int:
    return getattr(self, "v", 0)


#@ requires True
#@ ensures True
def getattr_unknown_field(self: Cfg) -> int:
    return getattr(self, "_current_symbol_table", 0)
