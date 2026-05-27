from __future__ import annotations

from typing import List


class AbstractOpsMixin:
    """Registry of abstract `val` declarations and the late-emission block.

    During expression / statement emission the transpiler accumulates abstract
    val declarations for Python operations with no native WhyML equivalent
    (e.g. `pow_int`, `stmt_get`, generic iterator helpers). Deduplication is by
    name; same-name different-arity collisions are disambiguated by suffixing
    `_N`. The final block is inserted by `_insert_abstract_val_block`
    immediately after the last `type` declaration so that abstract vals
    referencing record types resolve correctly.
    """

    def _add_abstract_op(self, decl: str) -> None:
        """Register an abstract val declaration, deduplicating by name+arity.
        Different arities for the same function get unique names (e.g., stmt_get, stmt_get_2)."""
        parts = decl.split()
        if len(parts) >= 2 and parts[0] == "val":
            if parts[1] == "constant":
                name = parts[2] if len(parts) > 2 else decl
            else:
                name = parts[1]
        else:
            name = decl
        if name not in self._abstract_ops:
            self._abstract_ops[name] = decl
        else:
            # If same name, same declaration → skip
            if self._abstract_ops[name] == decl:
                return
            # Different arity → store under name_N key
            # Count params in existing and new
            existing = self._abstract_ops[name]
            existing_params = existing.count("(x")
            new_params = decl.count("(x")
            if new_params != existing_params:
                # Store under arity-suffixed key
                arity_key = f"{name}_{new_params}"
                self._abstract_ops[arity_key] = decl
            else:
                # Same arity but different declaration — keep longer
                if len(decl) > len(existing):
                    self._abstract_ops[name] = decl

    def _find_abstract_val_insert_idx(self, out: List[str]) -> int:
        """Pick the insertion point for the abstract-val block. Abstract
        vals may reference class record types (e.g. `val getattr_FooClass
        (x: fooclass) (f: int) : int`); those types are emitted by
        `_emit_type_decls` AFTER `_emit_preamble_helpers'` `let pycsl_div`
        / `let pycsl_mod`. Inserting at the first `let` would place the
        vals BEFORE their referenced types and Why3 would reject the file
        with "unbound type symbol".

        Strategy: if any `type ...` line exists in `out`, insert
        immediately after the LAST such line (skipping a trailing blank).
        Otherwise, fall back to the historical "insert before first `let`
        / non-ghost `val`" behaviour."""
        last_type_idx = -1
        for i, line in enumerate(out):
            if line.strip().startswith("type "):
                last_type_idx = i
        if last_type_idx >= 0:
            insert_idx = last_type_idx + 1
            if insert_idx < len(out) and out[insert_idx].strip() == "":
                insert_idx += 1
            return insert_idx
        for i, line in enumerate(out):
            stripped = line.strip()
            if stripped.startswith("let ") or stripped.startswith("let rec "):
                return i
            if stripped.startswith("val ") and "ghost" not in line:
                return i
        return len(out) - 1

    def _insert_abstract_val_block(self, out: List[str]) -> None:
        """Insert the abstract-val block (collected during transpilation)
        at the position selected by `_find_abstract_val_insert_idx`."""
        if not self._abstract_ops:
            return
        insert_idx = self._find_abstract_val_insert_idx(out)
        abs_lines = ["", "  (* Abstract operations for unsupported Python patterns *)"]
        for decl in sorted(self._abstract_ops.values()):
            abs_lines.append(f"  {decl}")
        abs_lines.append("")
        for line in reversed(abs_lines):
            out.insert(insert_idx, line)
