from __future__ import annotations

import re
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

    # self-tcb-reduction M5 (stmt_ir bespoke campaign): the converted expr/stmt
    # handlers (functions.py `_emit_py_expr_compare_bespoke`, `_emit_py_stmt_*_bespoke`,
    # `_emit_py_expr_{lambda,listcomp,setcomp,dictcomp}_bespoke`) emit RAW `self__<disp>_1`
    # dispatcher references (the trusted recursive dispatch `self._py_expr_to_ir`
    # / `self._py_stmts_to_ir` / `self._py_op_to_str`). In a STANDALONE emit of the
    # emitter class, some non-stub method body ALSO calls one of those `self.<m>(...)`
    # through the regular `_handle_dotted_call` lowering, which registers the abstract
    # `val self__<m>_1` via `_add_abstract_op`. But when the emitter class is IMPORTED
    # (frontend/__init__.py, frontend/ir_resolve.py — its methods become bodyless
    # stubs), that trigger never fires, leaving the bespoke references UNBOUND
    # (`unbound function or predicate symbol 'self__py_expr_to_ir_1'`). This is the SAME
    # class of bug as the undeclared-union skip: a cross-emission symbol referenced but
    # not declared. Signatures match the standalone-emitted decls exactly (the pyast_ir
    # ADT `emit_ir` / `stmt_ir` types), so registering here is dedup-byte-identical in
    # standalone and corpus-inert (no corpus program builds stmt_ir nodes — `_uses_stmt_ir`
    # is false — so these symbols never appear in `out`).
    _SELF_DISPATCH_VAL_DECLS = {
        "self__py_expr_to_ir_1": "val self__py_expr_to_ir_1 (x0: emit_ir) : emit_ir",
        "self__py_op_to_str_1": "val self__py_op_to_str_1 (x0: int) : string",
        "self__py_stmts_to_ir_1": "val self__py_stmts_to_ir_1 (x0: array int) : seq stmt_ir",
    }

    def _register_referenced_self_dispatch_vals(self, out: List[str]) -> None:
        """Register the abstract `val` for any stmt_ir-bespoke `self__<disp>_1`
        dispatcher referenced in the emitted body but not yet declared (the
        imported-emitter unbound-symbol fix). No-op unless a bespoke handler emitted
        one of these symbols — so every non-emitter file is byte-identical."""
        joined = None
        for sym, decl in self._SELF_DISPATCH_VAL_DECLS.items():
            if sym in self._abstract_ops:
                continue
            if joined is None:
                joined = "\n".join(out)
            if re.search(r"\b" + re.escape(sym) + r"\b", joined):
                self._add_abstract_op(decl)

    def _insert_abstract_val_block(self, out: List[str]) -> None:
        """Insert the abstract-val block (collected during transpilation)
        at the position selected by `_find_abstract_val_insert_idx`.

        Skips declarations whose symbol name is already emitted by
        `_emit_axiom_block` (axiom-required `val function` decls live
        at the top of the module). Without this, `bit_and` and the
        `struct_pack_<id>` / `struct_unpack_<id>` symbols would be
        declared twice — Why3 rejects with "Symbol X already defined".
        """
        self._register_referenced_self_dispatch_vals(out)
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

    def _insert_array_init_use(self, out: List[str]) -> None:
        """tierA-listfield-impl.md: pull `array.Init` in ONLY when the gated
        list-field binding of `_bind_listfield_from_seq` actually fired (it emits
        `Init.init`, the stdlib-PROVEN `seq -> array` reconciliation). Inserted
        immediately AFTER `use array.Array`: `array.Init` does `use export Array`, so
        the `([])` resolution order that the map.Map/array.Array ordering comment in
        `_emit_preamble_uses` depends on is unchanged. The flag is never set unless the
        binding fired, so every other emitted file is byte-identical."""
        if not getattr(self, "_needs_array_init", False):
            return
        line = "  use array.Init"
        if line in out:
            return
        try:
            idx = out.index("  use array.Array")
        except ValueError:
            return
        out.insert(idx + 1, line)

    def _insert_late_content_ops(self, out: List[str]) -> None:
        """cleared-array item 1 (call comprehensions). A content-comp `val` whose
        `ensures` references a USER `let function` (e.g. `[g(x) for x in a]` →
        `… result[i] = g(src[i])`) must be declared AFTER that function — the early
        abstract-op block precedes ALL functions, so `g` would be unbound there.

        Each deferred op is (op_name, decl, using_func): the function whose BODY
        contains the comprehension. Splice the decl immediately BEFORE that
        function's opening `let … using_func` line. By SCC order the referenced
        `g` is a callee of using_func, so it is emitted before using_func — hence
        this position lands the `val` after `g` and before its sole consumer.

        No-op unless a call comprehension fired (`_late_content_ops` non-empty), so
        every existing file is byte-identical. Insert in reverse so earlier splices
        do not shift the anchor indices of later ones."""
        late = getattr(self, "_late_content_ops", None)
        if not late:
            return
        for op_name, decl, using_func in reversed(late):
            if not using_func:
                self._add_abstract_op(decl)  # fallback: no anchor → early block
                continue
            # Match the function's opening line: `  let … <using_func> ( |:` — the
            # ident as a whole word after a `let`/`let rec`/`let [rec] function`.
            anchor = re.compile(
                r"^\s*let(\s+rec)?(\s+function|\s+lemma|\s+rec\s+function|\s+rec\s+lemma)?\s+"
                + re.escape(using_func) + r"(\s|\(|$)")
            idx = None
            for i, line in enumerate(out):
                if anchor.match(line):
                    idx = i
                    break
            if idx is None:
                # Anchor not found (defensive) → fall back to the early block.
                self._add_abstract_op(decl)
                continue
            # Mirror `_insert_abstract_val_block`: 2-space indent on the first
            # line, continuation `ensures` lines keep their own 4-space indent.
            decl_lines = decl.split("\n")
            block = ["  (* content-comp (call) abstract op *)",
                     f"  {decl_lines[0]}"] + decl_lines[1:] + [""]
            for line in reversed(block):
                out.insert(idx, line)
