from __future__ import annotations

from typing import List, Optional, Set


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
            # `val constant FOO ...`, `val function FOO ...` → name is parts[2]
            # `val FOO ...`                                  → name is parts[1]
            if parts[1] in ("constant", "function") and len(parts) > 2:
                name = parts[2]
            else:
                name = parts[1]
        elif len(parts) >= 2 and parts[0] in ("function", "predicate"):
            # `function FOO ...` / `predicate FOO ...` → name is parts[1]
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
            # A record type may carry trailing `invariant {…}` / `by {…}`
            # clauses on the following lines, and a mutually-recursive datatype
            # group continues with `with <name> = …` lines (A5a-residual) — both
            # are part of the type declaration. Skip past them so the
            # abstract-val block isn't spliced into the middle of the type decl
            # (a Why3 syntax error / unbound-type symbol).
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

    def _advance_past_referenced_axiom_decls(self, out: List[str], idx: int) -> int:
        """gap-9: if the abstract-val block would be inserted at `idx` but a
        pending (emitted) abstract op REFERENCES a symbol declared by a
        preamble-logic `val function …` / `predicate …` / `inductive …` line at
        or after `idx` (the `_filesystem_sys_access` stub citing `dir_lookup`),
        advance `idx` to just past that declaration so the abstract block lands
        AFTER its dependency. No-op (returns `idx` unchanged) unless such a
        forward reference exists — so every existing file is byte-identical.
        Symbols carried ONLY by the deduped axiom-block twin of an abstract op
        are excluded (they would otherwise drag the block past their own kept
        declaration)."""
        # Names declared by the axiom block (their abstract-op twins are deduped
        # away in `_insert_abstract_val_block`, so they must not count as
        # "referenced" here).
        axiom_names: Set[str] = set()
        for d in getattr(self, "_axiom_emitted_decls", set()):
            p = d.split()
            if len(p) >= 3 and p[0] == "val" and p[1] in ("function", "constant"):
                axiom_names.add(p[2])
            elif len(p) >= 2 and p[0] == "val":
                axiom_names.add(p[1])
            elif len(p) >= 2 and p[0] in ("function", "predicate"):
                axiom_names.add(p[1])
        abs_text = " ".join(
            decl for name, decl in getattr(self, "_abstract_ops", {}).items()
            if name not in axiom_names)
        if not abs_text:
            return idx

        def _decl_symbol(stripped: str) -> Optional[str]:
            p = stripped.split()
            if len(p) >= 3 and p[0] == "val" and p[1] == "function":
                return p[2]
            if len(p) >= 2 and p[0] in ("function", "inductive", "predicate"):
                return p[1]
            return None

        new_idx = idx
        for j in range(idx, len(out)):
            s = out[j].strip()
            if s.startswith(("val function ", "function ", "inductive ", "predicate ")):
                sym = _decl_symbol(s)
                if sym and sym in abs_text:
                    new_idx = j + 1
        if new_idx == idx:
            return idx
        # Skip continuation lines of the last advanced-past decl (a predicate
        # body, an `inductive … =` rule `| …`, a record `invariant`/`by `) and a
        # trailing blank, so the block isn't spliced mid-declaration.
        while (new_idx < len(out) and
               out[new_idx].strip().startswith(
                   ("invariant", "by ", "with ", "| ", "axiom "))):
            new_idx += 1
        if new_idx < len(out) and out[new_idx].strip() == "":
            new_idx += 1
        return new_idx

    def _insert_abstract_val_block(self, out: List[str]) -> None:
        """Insert the abstract-val block (collected during transpilation)
        at the position selected by `_find_abstract_val_insert_idx`.

        Skips declarations whose symbol name is already emitted by
        `_emit_axiom_block` (axiom-required `val function` decls live
        at the top of the module). Without this, `bit_and` and the
        `struct_pack_<id>` / `struct_unpack_<id>` symbols would be
        declared twice — Why3 rejects with "Symbol X already defined".
        """
        if not self._abstract_ops:
            return

        # Names already declared by the axiom block (`_emit_preamble_axioms`),
        # for the cited qualnames ONLY — recorded in `_axiom_emitted_decls`.
        # Skipping these avoids a double declaration; using the actually-emitted
        # set (not every `_AXIOM_FUNCTIONS` entry) is essential for symbols like
        # `permut` that ARE abstract-ops in files that don't cite their axiom.
        axiom_decl_names: Set[str] = set()
        for d in getattr(self, "_axiom_emitted_decls", set()):
            parts = d.split()
            if len(parts) >= 3 and parts[0] in ("val", "function"):
                if parts[1] in ("function", "constant"):
                    axiom_decl_names.add(parts[2])
                else:
                    axiom_decl_names.add(parts[1])
            elif len(parts) >= 2 and parts[0] in ("function", "predicate"):
                # `function FOO …` / `predicate FOO …` → name is parts[1]
                axiom_decl_names.add(parts[1])

        # module-emission.md: in the `_transpile_modular` path the genuinely shared
        # (non-self) abstract ops are declared once in `Shared` and `use`d everywhere, so
        # a non-Shared module must NOT re-declare them (Why3 would flag the symbol as an
        # ambiguous double declaration). `_shared_op_skip` names exactly those; empty on
        # the flat path → byte-identical.
        shared_skip: Set[str] = getattr(self, "_shared_op_skip", set())
        insert_idx = self._find_abstract_val_insert_idx(out)
        abs_lines = ["", "  (* Abstract operations for unsupported Python patterns *)"]
        for name, decl in sorted(self._abstract_ops.items()):
            if name in axiom_decl_names:
                continue
            if name in shared_skip:
                continue
            abs_lines.append(f"  {decl}")
        # If everything got deduped, don't leave a dangling comment.
        if len(abs_lines) == 2:
            return
        abs_lines.append("")
        for line in reversed(abs_lines):
            out.insert(insert_idx, line)
