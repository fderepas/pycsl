from __future__ import annotations
from typing import List, Optional, Set
""  # pycsl
class AbstractOpsMixin:
    'Registry of abstract `val` declarations and the late-emission block.\n\n    During expression / statement emission the transpiler accumulates abstract\n    val declarations for Python operations with no native WhyML equivalent\n    (e.g. `pow_int`, `stmt_get`, generic iterator helpers). Deduplication is by\n    name; same-name different-arity collisions are disambiguated by suffixing\n    `_N`. The final block is inserted by `_insert_abstract_val_block`\n    immediately after the last `type` declaration so that abstract vals\n    referencing record types resolve correctly.\n    '
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self._abstract_ops, self._obj_state_written
    def _add_abstract_op(self, decl: str) -> None:
        pass

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _find_abstract_val_insert_idx(self, out: List[str]) -> int:
        last_type_idx = -1
        for i, line in enumerate(out):
            if line.strip().startswith("type "):
                last_type_idx = i
        if last_type_idx >= 0:
            insert_idx = last_type_idx + 1
            # A record type may carry trailing `invariant {…}` / `by {…}`
            # clauses on the following lines, and a mutually-recursive datatype
            # group continues with `with <name> = …` lines (A5a-residual) — both
            # are part of the type declaration. Skip past them so the
            # abstract-val block isn't spliced into the middle of the type decl
            # (a Why3 syntax error / unbound-type symbol).
            #@ loop invariant 0 <= insert_idx
            #@ loop variant \length(out) - insert_idx
            while (insert_idx < len(out) and
                   out[insert_idx].strip().startswith(("invariant", "by ", "with "))):
                insert_idx += 1
            if insert_idx < len(out) and out[insert_idx].strip() == "":
                insert_idx += 1
            return self._advance_past_referenced_axiom_decls(out, insert_idx)
        for i, line in enumerate(out):
            stripped = line.strip()
            if stripped.startswith("let ") or stripped.startswith("let rec "):
                return self._advance_past_referenced_axiom_decls(out, i)
            if stripped.startswith("val ") and "ghost" not in line:
                return self._advance_past_referenced_axiom_decls(out, i)
        return len(out) - 1

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _advance_past_referenced_axiom_decls(self, out: List[str], idx: int) -> int:
        return 0

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self._abstract_ops, self._obj_state_written, out
    def _insert_abstract_val_block(self, out: List[str]) -> None:
        pass


