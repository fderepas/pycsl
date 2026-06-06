from __future__ import annotations

from typing import Any, Dict, List, Set, Tuple

from module6_whyml.identifiers import whyml_ident, safe_mutex_name, safe_exc_name
from module6_whyml.ir_scanner import IRScanner


class PreambleEmissionMixin:
    """Preamble emission: top-of-file `use` clauses, exception type declarations, helper let-bindings, axiom blocks, shared state for the concurrent memory model, record/sum type declarations, and opaque class aliases. Mixed into Module6_WhyMLTranspiler."""

    # §2.1.12 — registry of hand-curated axiom bodies for `#@ proof`
    # qualnames. MVP step before `proof2why3` extraction lands (see
    # docs/cross-validated-spec-sources.md). Each entry's body is the canonical statement that
    # the paired Rocq + Lean theorems establish — cross-checked
    # manually for the MVP, automatically via the cross-check
    # pipeline in v1.
    _AXIOM_REGISTRY: Dict[str, str] = {
        # Pycsl.Reference.Gcd — Euclidean GCD properties.
        # Cross-validated by 0342.proofs/rocq/gcd.v + 0342.proofs/lean/Gcd.lean.
        # The `a >= 0 -> b >= 0 ->` side conditions on each entry mirror
        # the `nat`-lift: Rocq+Lean prove these theorems over `nat`, and
        # the WhyML `int` axioms add the non-negativity side conditions
        # explicitly. Identified as missing from gcd_step + gcd_result_nonneg
        # by `python -m pycsl.proof2why3.crosscheck` (sticky-01.md Phase 1+2+3 v0).
        "Pycsl.Reference.Gcd.gcd_result_nonneg":
            "forall a b : int. a >= 0 -> b >= 0 -> 0 <= gcd a b",
        "Pycsl.Reference.Gcd.gcd_result_positive":
            "forall a b : int. a >= 0 -> b >= 0 -> (a > 0 \\/ b > 0) -> gcd a b > 0",
        "Pycsl.Reference.Gcd.gcd_divides_a":
            "forall a b : int. a >= 0 -> b >= 0 -> (a > 0 \\/ b > 0) -> mod a (gcd a b) = 0",
        "Pycsl.Reference.Gcd.gcd_divides_b":
            "forall a b : int. a >= 0 -> b >= 0 -> (a > 0 \\/ b > 0) -> mod b (gcd a b) = 0",
        "Pycsl.Reference.Gcd.gcd_0":
            "forall a : int. a >= 0 -> gcd a 0 = a",
        "Pycsl.Reference.Gcd.gcd_step":
            "forall a b : int. a >= 0 -> b >= 0 -> b > 0 -> "
            "gcd a b = gcd b (mod a b)",
        "Pycsl.Reference.Gcd.gcd_greatest":
            "forall a b k : int. a >= 0 -> b >= 0 -> k >= 0 -> "
            "(a > 0 \\/ b > 0) -> "
            "k > 0 -> mod a k = 0 -> mod b k = 0 -> k <= gcd a b",

        # Pycsl.Reference.Perm — permutation framing lemmas over the
        # `\permutation` predicate (`predicate permut`). no-more-int A2b
        # stage-4: the uninterpreted `permut` is constrained by
        # proof-assistant-imported axioms. `permut_refl` (reflexivity) is the
        # first, cross-validated by 0538.proofs/rocq/Perm.v (Permutation_refl)
        # + 0538.proofs/lean/Perm.lean (List.Perm.refl). The axiom is stated
        # over `array int` (the logic model of an array), which the stage-4
        # spike verified is sound — no `seq` snapshot needed (Gap 2 obviated).
        "Pycsl.Reference.Perm.permut_refl":
            "forall s : array int. permut s s",
        # The framing lemma: reversing a list permutes its elements. The SMT
        # solver cannot derive this (uninterpreted `permut`, no multiset
        # reasoning) — it is the proof-assistant-imported axiom that does.
        # Cross-validated by 0539.proofs/rocq/Rev.v (`Permutation_rev`) +
        # 0539.proofs/lean/Rev.lean (`List.reverse_perm`).
        "Pycsl.Reference.Perm.rev_permutation":
            "forall s : array int. permut (array_rev s) s",

        # Pycsl.Reference.Json — an INDUCTIVE property over a recursive
        # `#@ datatype Json` (no-more-int A4 generalization demo). `json_mirror`
        # swaps every `JPair`'s children; mirroring twice is the identity.
        # Cross-validated by 0542.proofs/rocq/Json.v + lean/Json.lean
        # (`mirror_involution`, proved by structural induction). The axiom
        # quantifies over the user type `json`, which is why `#@ proof` axioms
        # are now emitted AFTER the type declarations.
        "Pycsl.Reference.Json.mirror_involution":
            "forall x : json. json_mirror (json_mirror x) = x",

        # UnixFs.Bitmap — bitwise properties needed by inode/block
        # bitmap allocators. Cross-validated by
        # unix-filesystem/UnixInodeFileSystem.proofs/rocq/UnixInodeFileSystem.v.
        # Discharges Z3 timeout on `(x >> y) & 1 ∈ {0, 1}` in
        # _get_bitmap (3.4B-step Z3 blowup → 0-step axiom citation).
        "UnixFs.Bitmap.bit_and_one_in_zero_one":
            "forall n : int. 0 <= bit_and n 1 /\\ bit_and n 1 < 2",

        # UnixFs.Struct — struct.pack / struct.unpack round-trip per
        # format slot_id. Cross-validated by the witness Coq model
        # in unix-filesystem/UnixInodeFileSystem.proofs/rocq/
        # UnixInodeFileSystem.v (Module UnixFs.Struct.Fmt_<id>).
        # Witness closes round-trip by `reflexivity`; the WhyML axiom
        # constrains the abstract `val function struct_pack_<id>` /
        # `val function struct_unpack_<id>` symbols emitted by
        # Module6's `_handle_struct_call` dispatch.
        #
        # Note: array equality in Why3 is by Array.= (extensional).
        # The tuple-result equality decomposes per-component, which
        # the SMT solver dispatches by structural matching.
        "UnixFs.Struct.i1a1.round_trip":
            "forall fmt : int. forall x0 : int. forall x1 : array int. "
            "struct_unpack_i1a1 fmt (struct_pack_i1a1 fmt x0 x1) = (x0, x1)",

        "UnixFs.Struct.i2.round_trip":
            "forall fmt x0 x1 : int. "
            "struct_unpack_i2 fmt (struct_pack_i2 fmt x0 x1) = (x0, x1)",

        "UnixFs.Struct.i18.round_trip":
            "forall fmt x0 x1 x2 x3 x4 x5 x6 x7 x8 x9 "
            "x10 x11 x12 x13 x14 x15 x16 x17 : int. "
            "struct_unpack_i18 fmt "
            "(struct_pack_i18 fmt x0 x1 x2 x3 x4 x5 x6 x7 x8 x9 "
            "x10 x11 x12 x13 x14 x15 x16 x17) "
            "= (x0, x1, x2, x3, x4, x5, x6, x7, x8, x9, "
            "x10, x11, x12, x13, x14, x15, x16, x17)",
    }

    # Functions that an axiom block needs declared. Looked up by qualname
    # prefix; declarations emitted once each when any matching axiom fires.
    # Values are List[str] so a single prefix can carry several function
    # declarations — required for `UnixFs.Struct.<slot_id>.round_trip`
    # axioms that mention both `struct_pack_<id>` and `struct_unpack_<id>`.
    _AXIOM_FUNCTIONS: Dict[str, List[str]] = {
        "Pycsl.Reference.Gcd.": ["function gcd (a : int) (b : int) : int"],
        # Declare the `\permutation` predicate before its axioms. Same symbol
        # `_handle_permutation_expr` emits via `_add_abstract_op` — the
        # abstract-val dedup skips it here so it is declared exactly once.
        "Pycsl.Reference.Perm.": ["predicate permut (a: array int) (b: array int)"],
        # The `rev_permutation` axiom additionally needs `array_rev` (the
        # `reversed(...)` model) declared before it. Keyed on the longer prefix
        # so `permut_refl` (which doesn't mention it) stays unchanged.
        "Pycsl.Reference.Perm.rev_permutation":
            ["val function array_rev (a: array int) : array int"],
        # A4: `json_mirror` over the user `json` datatype. The axiom block is
        # emitted after `_emit_type_decls`, so `json` is in scope here.
        "Pycsl.Reference.Json.":
            ["val function json_mirror (x: json) : json"],
        # Declare bit_and here (before the axiom block) so the axiom
        # `forall n. 0 <= bit_and n 1 < 2` typechecks. Uses Why3's
        # `val function` idiom — both program and logic symbol — so
        # the body of _get_bitmap can call it AND the axiom can
        # constrain it. Abstract-ops dedupes against this declaration.
        "UnixFs.Bitmap.": ["val function bit_and (x : int) (y : int) : int"],
        # UnixFs.Struct: round-trip axioms per format slot_id.
        # Each format gets its own pack/unpack `val function` symbol
        # so the axiom (forall fmt args, unpack (pack args) = args)
        # typechecks against the same symbols emitted by Module6's
        # `_handle_struct_call` dispatch.
        "UnixFs.Struct.i1a1.": [
            "val function struct_pack_i1a1 (fmt: int) (x0: int) (x1: array int) : array int\n"
            "    ensures { Array.length result = 32 }",
            "val function struct_unpack_i1a1 (fmt: int) (data: array int) : (int, array int)",
        ],
        "UnixFs.Struct.i2.": [
            "val function struct_pack_i2 (fmt: int) (x0: int) (x1: int) : array int",
            "val function struct_unpack_i2 (fmt: int) (data: array int) : (int, int)",
        ],
        "UnixFs.Struct.i18.": [
            "val function struct_pack_i18 (fmt: int) "
            "(x0: int) (x1: int) (x2: int) (x3: int) (x4: int) (x5: int) "
            "(x6: int) (x7: int) (x8: int) (x9: int) (x10: int) (x11: int) "
            "(x12: int) (x13: int) (x14: int) (x15: int) (x16: int) (x17: int) "
            ": array int\n"
            "    ensures { Array.length result = 64 }",
            "val function struct_unpack_i18 (fmt: int) (data: array int) : "
            "(int, int, int, int, int, int, int, int, int, "
            "int, int, int, int, int, int, int, int, int)",
        ],
    }

    def _scan_preamble_needs(self, functions: List[Dict[str, Any]],
                             all_bodies: List[Any]) -> Dict[str, Any]:
        """Scan all function bodies once to collect feature flags for preamble emission."""
        has_list_param = any(
            v in ("list", "dict")
            for func in functions
            for v in func.get("symbol_table", {}).values()
        )
        needs_matrix = any(func.get("array2d_params") for func in functions)
        # Phase 3 of missing-bytes-struct-feature.md: axioms in
        # _AXIOM_REGISTRY may mention `array int` (e.g. round_trip on
        # struct_pack_i1a1). If any cited axiom contains that token,
        # force `use array.Array` even when the body is \trusted and
        # the IR scanner finds no array usage.
        axiom_needs_array = False
        for func in functions:
            for entry in func.get("proof", []):
                qn = entry.get("qualname", "")
                body = self._AXIOM_REGISTRY.get(qn, "")
                if "array int" in body or "array " in body:
                    axiom_needs_array = True
                    break
            if axiom_needs_array:
                break
        if self._value_semantic:
            needs_array = (
                has_list_param
                or any(IRScanner.uses_for(body) for body in all_bodies)
                or any(IRScanner.uses_subscript(body) for body in all_bodies)
                or any(IRScanner.uses_arrayset(body) for body in all_bodies)
                or any(IRScanner.uses_array_lit(body) for body in all_bodies)
                or any(IRScanner.uses_ghost_type(body, {"array"}) for body in all_bodies)
                or axiom_needs_array
            )
        else:
            needs_array = False
        needs_minmax = any(IRScanner.uses_minmax(body) for body in all_bodies)
        needs_continue = any(IRScanner.uses_continue(body) for body in all_bodies)
        needs_break = any(IRScanner.uses_break(body) for body in all_bodies)
        needs_return_exc = False
        needs_return_void = False
        tuple_return_arities: Set[int] = set()
        n = len(functions)
        i = 0
        while i < n:
            func = functions[i]
            has_ret = IRScanner.has_in_loop_return(func["body"]) or IRScanner.has_early_return(func["body"])
            if has_ret:
                ret_type = IRScanner.find_return_type(func["body"])
                if ret_type == "unit":
                    needs_return_void = True
                elif ret_type.startswith("(") and "," in ret_type:
                    # Tuple return — needs a dedicated Return_<arity> exception
                    # so the value carries through; the plain `exception Return int`
                    # would force `_coerce_to_int` to hash the whole tuple.
                    tuple_return_arities.add(ret_type.count(",") + 1)
                else:
                    needs_return_exc = True
            i += 1
        needs_string = (
            any(IRScanner.uses_ghost_type(body, {"string"}) for body in all_bodies)
            # strings-plan Stage 1: a runtime `str` param/local/return also needs string.String
            or any("str" in f.get("symbol_table", {}).values() for f in functions)
            or any(f.get("return_annotation") == "str" for f in functions)
        )
        # no-more-int Stage D: a `float` param/local/return is Why3 `real`; RealInfix
        # provides the disambiguated `+.`/`-.`/`*.`/`/.`/`<.` operators alongside int.Int.
        needs_real = (
            any("float" in f.get("symbol_table", {}).values() for f in functions)
            or any(f.get("return_annotation") == "float" for f in functions)
        )
        # no-more-int-7 §B′: a `seq int`-valued dict (`Dict[_, List[int]]`) needs
        # `seq.Seq` for the immutable list-snapshot model.
        needs_seq = any(
            "seq" in v for f in functions for v in f.get("dict_value_types", {}).values()
        )
        needs_map_ghost = any(IRScanner.uses_ghost_type(body, {"ghost_dict", "ghost_set"}) for body in all_bodies)
        needs_ghost_dict = any(IRScanner.uses_ghost_type(body, {"ghost_dict"}) for body in all_bodies)
        # Body-level Python dicts are modelled as `ref (map int (option int))`
        # (parallel to ghost dicts). Triggered by:
        #   - `find_array_and_dict_vars` detecting any `d = {}` / `d = dict()`
        #     / `d = {k: v}` / `s = set()` / `s = {a, b}` in the body.
        #   - inline set/dict literals (e.g. `held | {mutex}`) or
        #     `.add()`/`.discard()`/`.remove()` method calls anywhere in
        #     the IR — these emit `map_update_some` / `map_update_none`
        #     into the abstract-val block, which requires `use map.Map`
        #     and `use option.Option` in the preamble.
        needs_body_dict = False
        for body in all_bodies:
            _arr, body_dicts = IRScanner.find_array_and_dict_vars(body)
            if body_dicts or IRScanner.uses_inline_set_or_dict_ops(body):
                needs_body_dict = True
                break
        # Map types can also appear ONLY in function signatures (set/dict/
        # frozenset parameters lowered by `_param_type_str` to
        # `map int (option int)`), without any body-level map usage.
        # Without this check the preamble omits `use map.Map` and the
        # signature's `map` type symbol is unbound — see
        # `src/self-annotate/src/exception_model.py:predicate_definitions`
        # which takes a `set` parameter but has no body-level dict ops.
        if not needs_body_dict:
            for func in functions:
                if any(v in ("set", "dict", "frozenset")
                       for v in func.get("symbol_table", {}).values()):
                    needs_body_dict = True
                    break
        needs_list_ghost = any(IRScanner.uses_ghost_type(body, {"ghost_list"}) for body in all_bodies)
        needs_sum = any(IRScanner.uses_sum(func) for func in functions)
        needs_set_card = any(IRScanner.uses_set_card(func) for func in functions)
        needs_divmod = any(IRScanner.uses_divmod(body) for body in all_bodies)
        # `no_exception` predicate vocabulary is emitted if any function in
        # the file declares a no_exception clause (Phase 1 NoException
        # workplan). See src/pycsl/exception_model.py for the predicates.
        needs_no_exception = any(
            func.get("contracts", {}).get("no_exception") or
            func.get("contracts", {}).get("no_exception_all")
            for func in functions
        )
        bounded_sizes = {func["bounded_int"] for func in functions if func.get("bounded_int")}
        user_exceptions: Set[str] = set()
        n2 = len(all_bodies)
        i2 = 0
        while i2 < n2:
            user_exceptions |= IRScanner.collect_user_exceptions(all_bodies[i2])
            i2 += 1
        # Also surface exceptions named only in a `raises` CONTRACT clause
        # (e.g. an `\abstract` val with `raises SyntaxError when ...` and no
        # body raise) — collect_user_exceptions scans bodies, not specs, so
        # such an exception would otherwise be an unbound symbol in WhyML.
        for func in functions:
            for rc in func.get("contracts", {}).get("raises", []):
                exc = rc.get("exc_type")
                if exc:
                    user_exceptions.add(exc)
        return {
            "needs_array": needs_array,
            "needs_matrix": needs_matrix,
            "needs_minmax": needs_minmax,
            "needs_continue": needs_continue,
            "needs_break": needs_break,
            "needs_return_exc": needs_return_exc,
            "needs_return_void": needs_return_void,
            "needs_body_dict": needs_body_dict,
            "tuple_return_arities": tuple_return_arities,
            "needs_string": needs_string,
            "needs_real": needs_real,
            "needs_seq": needs_seq,
            "needs_map_ghost": needs_map_ghost,
            "needs_ghost_dict": needs_ghost_dict,
            "needs_list_ghost": needs_list_ghost,
            "needs_sum": needs_sum,
            "needs_set_card": needs_set_card,
            "needs_divmod": needs_divmod,
            "needs_no_exception": needs_no_exception,
            "bounded_sizes": bounded_sizes,
            "user_exceptions": user_exceptions,
        }

    def _emit_preamble_uses(self, needs: Dict[str, Any]) -> List[str]:
        """Phase A: emit module header and `use` declarations for libraries."""
        out = [
            "module PyCSL_Program",
            "  use int.Int",
            "  use int.EuclideanDivision",
            "  use ref.Ref",
        ]
        sorted_bsz = sorted(needs["bounded_sizes"])
        n = len(sorted_bsz)
        i = 0
        while i < n:
            out.append(f"  use mach.int.Int{sorted_bsz[i]}")
            i += 1
        if needs["needs_string"]:
            out.append("  use string.String")
        if needs.get("needs_real"):
            out.append("  use real.RealInfix")  # no-more-int Stage D — `+.`/`-.`/… on real
        if needs.get("needs_seq"):
            out.append("  use seq.Seq")  # no-more-int-7 §B′ — immutable list-snapshot value model
        if self._value_semantic:
            if needs["needs_matrix"]:
                out.append("  use matrix.Matrix")
            if needs["needs_minmax"]:
                out.append("  use int.MinMax")
            if needs["needs_map_ghost"] or needs.get("needs_body_dict"):
                out.append("  use map.Map")
                out.append("  use map.Const")
            if needs["needs_ghost_dict"] or needs.get("needs_body_dict"):
                # Body-level Python dicts are modelled as
                # `ref (map int (option int))` (parallel to ghost dicts);
                # `None` marks absent keys.
                out.append("  use option.Option")
            # `array.Array` MUST be imported AFTER `map.Map` — both
            # provide a `([])` operator, and when both are in scope the
            # later import wins. With map.Map imported last, `arr[i]` on
            # an `array int` is mis-resolved to `Map.get`, producing
            # "expected 'mu -> 'mu1, got array int @rho" type errors.
            # See ConcurrencyChecker (which combines body-set ops with
            # array-typed function parameters).
            if needs["needs_array"]:
                out.append("  use array.Array")
            if needs["needs_list_ghost"]:
                out.append("  use list.List")
                out.append("  use list.Length")
                out.append("  use list.NthNoOpt")
                out.append("  use list.Mem")
                out.append("  use list.Append")
        else:
            out.append("  use map.Map")
            if needs["needs_list_ghost"]:
                out.append("  use list.List")
                out.append("  use list.Length")
                out.append("  use list.NthNoOpt")
                out.append("  use list.Mem")
                out.append("  use list.Append")
            if needs["needs_minmax"]:
                out.append("  use int.MinMax")
            out.append("")
            out.append("  type loc = int")
            out.append("  constant max_addr : int = 1073741824")
            hv = self._heap_var
            out.append(f"  val ghost {hv} : ref (map loc int)")
            out.append("")
            out.append(f"  predicate valid (m: map loc int) (base: loc) (n: int) =")
            out.append(f"    n >= 0 /\\ base >= 0 /\\ base + n <= max_addr")
            out.append("")
            out.append(f"  predicate separated (a: loc) (na: int) (b: loc) (nb: int) =")
            out.append(f"    a + na <= b \\/ b + nb <= a")
            out.append("")
        return out

    def _emit_preamble_exceptions(self, needs: Dict[str, Any]) -> List[str]:
        """Phase B: emit exception type declarations."""
        out: List[str] = []
        if needs["needs_continue"]:
            out.append("")
            out.append("  exception PyCSL_Continue")
        if needs["needs_break"]:
            out.append("")
            out.append("  exception PyCSL_Break")
        if needs["needs_return_exc"]:
            out.append("")
            out.append("  exception Return int")
        if needs["needs_return_void"]:
            out.append("")
            out.append("  exception Return_void")
        for arity in sorted(needs.get("tuple_return_arities", set())):
            # Tuple returns: each arity gets its own exception carrying the
            # full tuple, avoiding the int-hash collapse the plain `Return int`
            # would force via `_coerce_to_int`.
            parts = ", ".join(["int"] * arity)
            out.append("")
            out.append(f"  exception Return_{arity} ({parts})")
        # Sanitize each user-exception name; collapse Python local-alias
        # imports (`from X import Y as _Y`) by deduping via set after
        # leading-underscore strip. See `safe_exc_name` in identifiers.py.
        sanitized_exc = sorted({safe_exc_name(n) for n in needs["user_exceptions"]})
        for exc in sanitized_exc:
            out.append(f"  exception {exc}")
        return out

    def _emit_preamble_helpers(self, needs: Dict[str, Any]) -> List[str]:
        """Phase C: emit helper lemmas, pycsl_sum, pycsl_div, pycsl_mod function bodies."""
        out: List[str] = []
        if needs.get("needs_list_ghost"):
            # axiom mem_head: base case of mem — makes \mem(x, \cons(x, l)) proofs tractable
            # without recursive unfolding. This is the head-match case of mem's definition,
            # so it is mathematically sound to assume it as an axiom.
            out.append("")
            out.append("  axiom mem_head : forall x: int, l: list int. mem x (Cons x l)")
        if needs["needs_sum"]:
            out.append("")
            out.append("  let rec function pycsl_sum (a: array int) (lo hi: int) : int")
            out.append("    requires { 0 <= lo }")
            out.append("    requires { hi <= Array.length a }")
            out.append("    variant { hi - lo }")
            out.append("  = if lo >= hi then 0 else a[lo] + pycsl_sum a (lo + 1) hi")
            out.append("")
            out.append("  let rec lemma pycsl_sum_snoc (a: array int) (lo hi: int) : unit")
            out.append("    requires { 0 <= lo <= hi <= Array.length a }")
            out.append("    variant { hi - lo }")
            out.append("    ensures { hi > lo -> pycsl_sum a lo hi = pycsl_sum a lo (hi - 1) + a[hi - 1] }")
            out.append("  = if lo < hi - 1 then pycsl_sum_snoc a (lo + 1) hi")
        if needs["needs_set_card"]:
            out.append("")
            out.append("  let rec function set_card (s: map int bool) (lo hi: int) : int")
            out.append("    requires { lo <= hi }")
            out.append("    variant { hi - lo }")
            out.append("  = if lo >= hi then 0")
            out.append("    else (if Map.get s lo then 1 else 0) + set_card s (lo + 1) hi")
            out.append("")
            out.append("  let rec lemma set_card_add_hi (s: map int bool) (lo hi: int) : unit")
            out.append("    requires { lo <= hi }")
            out.append("    variant { hi - lo }")
            out.append("    ensures { set_card (Map.set s hi true) lo (hi + 1) = set_card s lo hi + 1 }")
            out.append("  = if lo < hi then set_card_add_hi s (lo + 1) hi")
        if needs["needs_divmod"]:
            out.append("")
            if "ZeroDivisionError" in needs["user_exceptions"]:
                out.append("  let pycsl_div (x: int) (y: int) : int")
                out.append("    raises { ZeroDivisionError -> y = 0 }")
                out.append("    ensures { y <> 0 /\\ result = div x y }")
                out.append("  = if y = 0 then raise ZeroDivisionError else div x y")
                out.append("")
                out.append("  let pycsl_mod (x: int) (y: int) : int")
                out.append("    raises { ZeroDivisionError -> y = 0 }")
                out.append("    ensures { y <> 0 /\\ result = mod x y }")
                out.append("  = if y = 0 then raise ZeroDivisionError else mod x y")
            else:
                out.append("  let pycsl_div (x: int) (y: int) : int")
                out.append("    requires { [@expl:division by zero] y <> 0 }")
                out.append("    ensures { result = div x y }")
                out.append("  = div x y")
                out.append("")
                out.append("  let pycsl_mod (x: int) (y: int) : int")
                out.append("    requires { [@expl:modulo by zero] y <> 0 }")
                out.append("    ensures { result = mod x y }")
                out.append("  = mod x y")
        return out

    def _emit_preamble_axioms(self, ir: Dict[str, Any]) -> List[str]:
        """Emit Why3 function decls + axioms for `#@ proof` cites.

        Scans every function in the program IR for `proof` entries.
        Dedups by qualname (Rocq + Lean cite the same target). Emits
        each axiom under a sanitized name `pycsl_axiom_<...>` and
        records the prover provenance in a Why3 comment.
        """
        # Record the axiom-block function/predicate decls ACTUALLY emitted for
        # this module, so the abstract-val dedup
        # (`_insert_abstract_val_block`) skips exactly those — not every entry
        # in `_AXIOM_FUNCTIONS`. A symbol like `permut` is declared here only
        # when its axiom is cited; a file that uses `\permutation` WITHOUT a
        # `#@ proof` still needs the abstract-ops declaration.
        self._axiom_emitted_decls: Set[str] = set()
        seen_qualnames: Set[str] = set()
        for func in ir.get("functions", []):
            for entry in func.get("proof", []):
                seen_qualnames.add(entry["qualname"])
        if not seen_qualnames:
            return []

        # Pair each qualname with the registry entry; halt if any
        # unknown — failure is at transpile time.
        out: List[str] = []
        # Declare backing functions once each (e.g. `function gcd`).
        declared_fns: Set[str] = set()
        for qn in sorted(seen_qualnames):
            for prefix, fn_decls in self._AXIOM_FUNCTIONS.items():
                if qn.startswith(prefix):
                    for fn_decl in fn_decls:
                        if fn_decl not in declared_fns:
                            out.append(f"  {fn_decl}")
                            declared_fns.add(fn_decl)
        self._axiom_emitted_decls = set(declared_fns)
        if declared_fns:
            out.append("")

        # Emit each axiom. Comment records the prover pairing.
        for qn in sorted(seen_qualnames):
            if qn not in self._AXIOM_REGISTRY:
                raise PyCSLIRError(
                    f"#@ proof {qn}: not in Module6 axiom registry. "
                    f"Either add the axiom body to _AXIOM_REGISTRY or run "
                    f"`proof2why3 emit` (when available — see "
                    f"docs/cross-validated-spec-sources.md)."
                )
            axiom_name = "pycsl_axiom_" + qn.replace(".", "_")
            body = self._AXIOM_REGISTRY[qn]
            # Provers cite this qualname — for the MVP we record both
            # under one cite. v1 emits the canonical-hash status from
            # the cross-check manifest.
            out.append(f"  (* {qn} — cross-validated Rocq + Lean *)")
            out.append(f"  axiom {axiom_name} : {body}")
        out.append("")
        return out

    def _emit_preamble_no_exception_predicates(self, needs: Dict[str, Any]) -> List[str]:
        """Phase D: emit the WhyML predicate library for `no_exception`.

        Only emitted when at least one function declares `no_exception`
        (per `needs_no_exception`). The predicate definitions come from
        `exception_model.PREDICATE_LIBRARY` — the single source of truth.
        """
        if not needs.get("needs_no_exception"):
            return []
        from exception_model import predicate_definitions
        out: List[str] = [""]
        for line in predicate_definitions():
            out.append(f"  {line}")
        return out

    def _emit_preamble(self, needs: Dict[str, Any]) -> List[str]:
        """Emit the WhyML module header: use declarations, exception types, helper functions."""
        out = self._emit_preamble_uses(needs)
        out += self._emit_preamble_exceptions(needs)
        out += self._emit_preamble_helpers(needs)
        out += self._emit_preamble_no_exception_predicates(needs)
        # NOTE: `#@ proof` axioms are emitted by `transpile()` AFTER the type
        # declarations (not here) — an axiom may quantify over a user
        # `#@ datatype` (e.g. `forall x: json. …` for the A4 round-trip), which
        # must be declared first. Builtin-typed axioms (gcd/permut/…) are
        # order-insensitive, so this only repositions them, preserving pass/fail.
        out.append("")
        return out

    def _emit_shared_state(self) -> List[str]:
        """Emit shared variable declarations and mutex invariant predicates (concurrent model)."""
        out: List[str] = []
        shared_vars = self.ir.get("shared_vars", [])
        mutex_invariants_ir = self.ir.get("mutex_invariants", {})
        if shared_vars:
            self._shared_var_names = {sv["name"] for sv in shared_vars}
            out.append("  (* --- shared state (concurrent model) --- *)")
            n = len(shared_vars)
            i = 0
            while i < n:
                sv = shared_vars[i]
                safe_name = whyml_ident(sv["name"])
                out.append(f"  val {safe_name} : ref int")
                i += 1
            out.append("")
        if mutex_invariants_ir:
            sorted_mi = sorted(mutex_invariants_ir.items())
            n = len(sorted_mi)
            i = 0
            while i < n:
                mutex, inv_ir = sorted_mi[i]
                safe_mutex = safe_mutex_name(mutex)
                self._in_spec = True
                inv_str = self._expr_to_whyml(inv_ir, set())
                self._in_spec = False
                out.append(f"  predicate {safe_mutex}_inv = {inv_str}")
                i += 1
            out.append("")
            sorted_mi2 = sorted(mutex_invariants_ir.items())
            n2 = len(sorted_mi2)
            i2 = 0
            while i2 < n2:
                mutex2, _ = sorted_mi2[i2]
                safe_mutex2 = safe_mutex_name(mutex2)
                out.append(f"  let _check_initial_{safe_mutex2} () : unit =")
                out.append(f"    assert {{ {safe_mutex2}_inv }}")
                out.append("")
                i2 += 1
        return out

    def _inductive_sig_whyml(self, signature: str) -> str:
        """inductive.md: a predicate's WhyML arg-type list (Why3 `inductive p t1 t2`
        takes UNNAMED arg types). From a source signature `"(n: int, x: Json)"`
        extract the types and map them (scalars stay, a datatype/class lowercases):
        `int json`."""
        inner = signature.strip().lstrip("(").rstrip(")").strip()
        if not inner:
            return ""
        scalars = {"int": "int", "bool": "bool", "str": "string", "float": "real"}
        types = []
        for part in inner.split(","):
            ty = part.split(":")[-1].strip() if ":" in part else "int"
            types.append(scalars.get(ty, whyml_ident(ty.lower())))
        return " ".join(types)

    def _emit_inductive_decls(self, inductive_decls: List[Dict[str, Any]]) -> List[str]:
        """inductive.md: emit each `#@ inductive` predicate as a Why3
        `inductive p t1 … = | Rule : clause … end`. Each rule's clause is the
        WhyML of its (contract-expression) Horn-clause body, lowered in spec
        context. Empty list → no output (byte-identical for non-inductive modules)."""
        if not inductive_decls:
            return []
        out: List[str] = []
        prev_spec = self._in_spec
        self._in_spec = True
        def _emit_member(kw: str, m: Dict[str, Any]) -> None:
            mname = whyml_ident(m["name"].lower())
            msig = self._inductive_sig_whyml(m["signature"])
            out.append(f"  {kw} {mname} {msig} =" if msig else f"  {kw} {mname} =")
            for (rname, clause_ir) in m["rules"]:
                clause = self._expr_to_whyml(clause_ir, set())
                out.append(f"    | {whyml_ident(rname).capitalize()} : {clause}")
        for ind in inductive_decls:
            # The head predicate uses `inductive`; each P2 mutual member uses `with`,
            # forming one Why3 group `inductive p … = | … with q … = | …`.
            _emit_member("inductive", ind)
            for m in ind.get("members", []):
                _emit_member("with", m)
            # A single Why3 `inductive` (or a `with`-joined group) takes NO closing
            # `end` (an `end` would close the enclosing module).
            out.append("")
        self._in_spec = prev_spec
        return out

    def _emit_type_decls(self, type_decls: List[Dict[str, Any]]) -> Tuple[List[str], Set[str]]:
        """Emit record type declarations. Returns (lines, declared_types)."""
        out: List[str] = []
        declared_types: Set[str] = set()
        # WhyML record field labels are global within a scope, so a field name
        # used by more than one record (e.g. an inherited field present in both
        # `base` and `sub`) collides. Qualify only those ambiguous names as
        # `<record>_<field>`; unique field names stay bare so existing
        # single-record files emit byte-identically (zero regression).
        _field_counts: Dict[str, int] = {}
        for _td in type_decls:
            if _td.get("kind") == "record":
                for _f in _td["fields"]:
                    _field_counts[_f["name"]] = _field_counts.get(_f["name"], 0) + 1
        self._ambiguous_fields = {fn for fn, c in _field_counts.items() if c > 1}
        n = len(type_decls)
        i = 0
        _VPAY = {"int": "int", "bool": "int", "str": "string", "float": "real"}
        # no-more-int-3 A5a: declared `#@ datatype` names, so a constructor
        # payload that NAMES a datatype (a self-reference `Node(Tree, Tree)` or
        # another variant) resolves to that variant's Why3 type instead of the
        # `_VPAY` int default. A single self-recursive type emits directly
        # (`type tree = Leaf | Node tree tree`); Why3 handles the self-reference.
        _variant_names = {td["name"] for td in type_decls
                          if td.get("kind") == "variant"}

        def _fmt_variant(vtd: Dict[str, Any]) -> str:
            """Register a variant's WhyML mapping + constructors and return its
            `<name>['a…] = Ctor pay | …` body (sans the `type`/`with` keyword)."""
            tn = vtd["name"].lower()
            declared_types.add(tn)
            # A5d: a parametric datatype `Option[T]` → `type option 't = …`. Each
            # type parameter `T` becomes a Why3 type variable `'t`; a payload
            # naming a type param resolves to that variable (not the int default).
            tparams = vtd.get("type_params", []) or []
            _tpvar = {p: f"'{p.lower()}" for p in tparams}
            header = tn + ("".join(f" {_tpvar[p]}" for p in tparams) if tparams else "")
            self._variant_types[vtd["name"]] = {
                "whyml_name": tn,
                "constructors": {c["name"]: c for c in vtd["constructors"]}}
            cstrs: List[str] = []
            for c in vtd["constructors"]:
                pay = " ".join(
                    _tpvar[t] if t in _tpvar
                    else _VPAY[t] if t in _VPAY
                    else (t.lower() if t in _variant_names else "int")
                    for t in c.get("payload", []))
                self._constructors[c["name"]] = {
                    "type": vtd["name"], "whyml_type": tn,
                    "arity": c["arity"], "payload": c.get("payload", [])}
                cstrs.append(c["name"] + (f" {pay}" if pay else ""))
            return f"{header} = {' | '.join(cstrs)}"

        # A5a-residual: mutually-recursive datatypes (e.g. `Tree` ↔ `Forest`)
        # must share one Why3 `type a = … with b = …` block, else the first
        # names the sibling before it is declared. Group variants by SCC of the
        # cross-reference graph (a payload naming ANOTHER variant is an edge).
        # A group of size 1 (independent or single self-recursive) is unchanged
        # — emitted as a plain `type … = …` — so existing files stay
        # byte-identical.
        _vrefs: Dict[str, Set[str]] = {}
        for _td in type_decls:
            if _td.get("kind") != "variant":
                continue
            _r: Set[str] = set()
            for _c in _td["constructors"]:
                for _t in _c.get("payload", []):
                    if _t in _variant_names and _t != _td["name"]:
                        _r.add(_t)
            _vrefs[_td["name"]] = _r

        def _reach(start: str) -> Set[str]:
            seen: Set[str] = set()
            stack = list(_vrefs.get(start, ()))
            while stack:
                x = stack.pop()
                if x in seen:
                    continue
                seen.add(x)
                stack.extend(_vrefs.get(x, ()))
            return seen

        _reach_map = {nm: _reach(nm) for nm in _vrefs}
        _vorder = [td["name"] for td in type_decls if td.get("kind") == "variant"]
        _td_by_name = {td["name"]: td for td in type_decls if td.get("kind") == "variant"}
        _variant_groups: Dict[str, List[str]] = {}
        for nm in _vorder:
            grp = [m for m in _vorder
                   if m == nm or (m in _reach_map[nm] and nm in _reach_map.get(m, set()))]
            _variant_groups[nm] = grp
        _emitted_variants: Set[str] = set()

        while i < n:
            td = type_decls[i]
            if td.get("kind") == "variant":
                # sum-types: `type color = Red | Green | Blue` / `type shape = Circle int | …`
                name = td["name"]
                group = _variant_groups.get(name, [name])
                if len(group) > 1:
                    # mutually-recursive group → one `with`-joined block
                    if name in _emitted_variants:
                        i += 1
                        continue
                    out.append(f"  type {_fmt_variant(_td_by_name[group[0]])}")
                    for member in group[1:]:
                        out.append(f"  with {_fmt_variant(_td_by_name[member])}")
                    out.append("")
                    _emitted_variants.update(group)
                    i += 1
                    continue
                out.append(f"  type {_fmt_variant(td)}")
                out.append("")
                i += 1
                continue
            if td["kind"] == "record":
                type_name = td["name"].lower()
                declared_types.add(type_name)
                self._record_types[td["name"]] = {
                    "whyml_name": type_name,
                    "fields": [f["name"] for f in td["fields"]],
                    "field_types": {f["name"]: f.get("type", "int") for f in td["fields"]},
                    "defaults": td.get("field_defaults", {}),
                    # base_op.md Tier A — parametrized construction C(a, b)
                    "init_params": td.get("init_params", []),
                    "init_body": td.get("init_body", []),
                }
                # Class-body integer constants (e.g. `CAP = 64`) — resolved to
                # literals when referenced as `self.CONST` in a method/contract.
                consts = td.get("constants", {})
                if consts:
                    self._class_constants[type_name] = dict(consts)
                field_strs = []
                fields = td["fields"]
                nf = len(fields)
                j = 0
                while j < nf:
                    f = fields[j]
                    prefix = "mutable " if f.get("mutable") else ""
                    ftype = f['type']
                    # Map Python-level type tags to WhyML types.
                    # `set`/`dict`/`frozenset` → `map int (option int)`
                    # (body-set/body-dict model). `list`/`tuple` →
                    # `array int`. Everything else collapses to `int`.
                    if ftype in ("set", "dict", "frozenset"):
                        ftype = "map int (option int)"
                    elif ftype in ("list", "tuple"):
                        ftype = "array int"
                    elif ftype == "string":
                        ftype = "int"
                    elif ftype != "int" and not ftype.startswith(("array ", "map ", "ref ")):
                        # Unrecognised tag (user-defined class etc.) —
                        # fall back to int rather than emitting an
                        # unbound type symbol.
                        ftype = "int"
                    field_strs.append(
                        f"{prefix}{self._field_label(type_name, f['name'])}: {ftype}")
                    j += 1
                out.append(f"  type {type_name} = {{ {'; '.join(field_strs)} }}")
                class_invs = td.get("class_invariants", [])
                if class_invs:
                    self._in_spec = True
                    self._emit_record_ctx = type_name
                    n_inv = len(class_invs)
                    i_inv = 0
                    while i_inv < n_inv:
                        inv = class_invs[i_inv]
                        inv_str = self._expr_to_whyml(inv, set(), invariant_ctx=True)
                        out.append(f"    invariant {{ {inv_str} }}")
                        i_inv += 1
                    self._emit_record_ctx = None
                    self._in_spec = False
                    defaults = td.get("field_defaults", {})
                    field_names = [f["name"] for f in td["fields"]]
                    field_types = {f["name"]: f.get("type", "int") for f in td["fields"]}
                    # Pin array-field lengths from `\length(self.f) == N`
                    # invariants so the `by` witness builds an array of the
                    # right size.
                    array_lengths = self._extract_array_lengths(class_invs)
                    witness_vals = {fn: defaults.get(fn, 0) for fn in field_names}
                    if not self._check_witness_vals(witness_vals, class_invs, field_names):
                        combos = [
                            {fn: 0 for fn in field_names},
                            {fn: 1 for fn in field_names},
                            {fn: 10 for fn in field_names},
                        ]
                        nc = len(combos)
                        ic = 0
                        while ic < nc:
                            combo = combos[ic]
                            if self._check_witness_vals(combo, class_invs, field_names):
                                witness_vals = combo
                                break
                            ic += 1
                    # Qualify ambiguous field names in the witness too.
                    _q = lambda fn: self._field_label(type_name, fn)
                    out.append(f"    by {{ {self._build_witness_str([_q(fn) for fn in field_names], {_q(fn): v for fn, v in witness_vals.items()}, {_q(fn): t for fn, t in field_types.items()}, {_q(fn): l for fn, l in array_lengths.items()})} }}")
                out.append("")
                # UB-7.2 — hash/eq consistency. Module 5 marks classes
                # whose `__hash__` and `__eq__` are both defined.
                # `__hash__` and `__eq__` are dunders and Module 5
                # skips dunders for body emission, so we declare them
                # as abstract `val` functions here and emit the
                # consistency relationship.
                #
                # Default mode emits an *axiom* — the user is on the
                # hook to keep hash and eq consistent; the axiom
                # documents the assumption. Strict mode (CLI flag
                # `--strict-hash-eq-consistency`) emits a *goal* that
                # Why3 must discharge (typically via an external
                # `#@ proof rocq` citation).
                if td.get("has_hash") and td.get("has_eq"):
                    cls = td["name"].lower()
                    out.append(f"  (* UB-7.2 — hash/eq for {td['name']} *)")
                    out.append(f"  val function {cls}_hash_ (x: {cls}) : int")
                    out.append(f"  val function {cls}_eq_ (a: {cls}) (b: {cls}) : bool")
                    if getattr(self, "strict_hash_eq_consistency", False):
                        out.append(
                            f"  goal hash_eq_consistent_{cls}: forall a b: {cls}. "
                            f"{cls}_eq_ a b = True -> {cls}_hash_ a = {cls}_hash_ b")
                    else:
                        out.append(
                            f"  axiom hash_eq_consistent_{cls}: forall a b: {cls}. "
                            f"{cls}_eq_ a b = True -> {cls}_hash_ a = {cls}_hash_ b")
                    out.append("")
                elif td.get("is_unhashable"):
                    cls = td["name"].lower()
                    out.append(f"  (* UB-7.2 — class {td['name']} defines __eq__ "
                               f"without __hash__: unhashable, do not use as dict/set key *)")
                    out.append("")
            i += 1
        return out, declared_types

    def _emit_opaque_class_aliases(self, functions: List[Dict[str, Any]],
                                    out: List[str], declared_types: Set[str]) -> None:
        """Emit `type <cls> = int` aliases for classes used as `self_type`
        in methods but not declared as records."""
        for func in functions:
            if func.get("kind") == "method" and func.get("self_type"):
                st = func["self_type"].lower()
                if st not in declared_types:
                    declared_types.add(st)
                    out.append(f"  type {st} = int")
                    out.append("")

