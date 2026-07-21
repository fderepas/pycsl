"""Test 0893 — emit_ir `alternatives` node-LIST projection lock (POSITIVE).

`alternatives` (a match-pattern `Or` node's alternative sub-pattern list) joins
`captures`/`args`/`elts`/`parts` in `_EMIT_IR_PROJ` as an `args_of` node-list
projection, so an IR-node-typed parameter (`pat: ExprIR`) whose
`.get("alternatives", [])` is read yields a REAL `array emit_ir` whose elements
are `emit_ir` nodes — not the opaque int-hash `*_get_*` fallback (which typed the
local as `int` and made every element read an abstract integer).

This is the capability the self-annotation mirror's
`ControlFlowStmtMixin._pattern_has_constructor` needs: it reads
`pat.get("alternatives", [])`, indexes it, and RECURSES on each element as a
pattern node. With the int-hash fallback that recursion did not even type-check
(`int` passed where `emit_ir` was expected).

Exercises: the `kind_of` discriminant on `.get("pattern")`, the list projection
(`args_of`), `len` over it, the element subscript (an `emit_ir`), and the
terminating recursion on the projected element. If this test regresses,
`alternatives` has fallen back to the opaque getter.
"""
from typing import Any, Dict, Set
from dataclasses import dataclass

ExprIR = Dict[str, Any]


def mutable_state(cls): return cls


@mutable_state
@dataclass
class PatternWalker:
    _seen: int = 0

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def pattern_has_constructor(self, pat: ExprIR) -> bool:
        """True if `pat` is a constructor pattern, or an `Or` with one among
        its alternatives (the emitter-shaped `Or`-pattern walker)."""
        p = pat.get("pattern")
        if p == "Constructor":
            return True
        if p == "Or":
            alts = pat.get("alternatives", [])
            n_alt = len(alts)
            i_alt = 0
            #@ loop invariant 0 <= i_alt and i_alt <= n_alt
            #@ loop variant n_alt - i_alt
            while i_alt < n_alt:
                if self.pattern_has_constructor(alts[i_alt]):
                    return True
                i_alt = i_alt + 1
            return False
        return False
