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

        # UnixFs.Dir — directory-scan reflection. The bounded scan over the 16
        # root-directory slots returns a non-negative inode IFF some live slot
        # decodes to `name`. INDUCTIVE over the slot loop (SMT times out:
        # gap-9, 14.6M/11.6M/18.8M steps). Cross-validated by
        # unix-filesystem/UnixInodeFileSystem.proofs/{rocq,lean}/UnixDirScan.{v,lean}
        # (UnixFs.Dir.scan_reflects_present): induction on the prefix length +
        # per-slot case split. Rocq: Closed under the global context (0 axioms);
        # Lean: axioms subseteq {propext, Quot.sound}. The slot_inode>=0 side
        # condition (decoded inode from unsigned bytes) is an EXPLICIT antecedent
        # `(forall j. 0 <= j < 16 -> slot_inode disk blk j >= 0)`, mirroring the
        # section-discharged `slot_inode_nonneg` / `hnn` hypothesis of both proofs
        # — keeping the axiom faithful (NOT over-strong). In WhyML it is
        # discharged by the companion `UnixFs.Dir.slot_inode_nonneg` axiom below
        # (the unsigned-byte fact), so callers cite both.
        "UnixFs.Dir.scan_reflects_present":
            "forall disk : array int. forall blk : int. forall name : string. "
            "( forall j : int. 0 <= j < 16 -> slot_inode disk blk j >= 0 ) -> "
            "( ( dir_lookup disk blk name >= 0 ) "
            "<-> "
            "( exists k : int. 0 <= k < 16 "
            "/\\ slot_inode disk blk k <> 0 "
            "/\\ slot_inode disk blk k < 32 "
            "/\\ slot_name disk blk k = name ) )",

        # UnixFs.Dir.slot_inode_nonneg — the unsigned-byte fact: a decoded
        # directory-slot inode number is always non-negative (it is read from
        # unsigned disk bytes via `_unpack_direntry`'s uint fields). This is the
        # `slot_inode_nonneg` / `hnn` HYPOTHESIS of the scan_reflects_present
        # proofs (UnixDirScan.{v,lean}), surfaced as an explicit named fact so it
        # discharges the `forall j. slot_inode disk blk j >= 0` antecedent of
        # scan_reflects_present without a per-call class invariant. Same trust
        # class as the scan axiom (a faithful property of the abstract decode);
        # the proofs CARRY it as an assumption, so it is genuinely part of this
        # family's TCB, named here rather than smuggled into the IFF.
        "UnixFs.Dir.slot_inode_nonneg":
            "forall disk : array int. forall blk : int. forall k : int. "
            "slot_inode disk blk k >= 0",

        # UnixFs.Dir.remove_reflects_absent (gap-11) — the ABSENCE twin of
        # scan_reflects_present. After the live entry at slot s is zeroed
        # (remove-witness: slot_inode disk blk s = 0) and provided `name` lived
        # only at s (uniqueness: every OTHER slot decoding to `name` is dead),
        # the bounded 16-slot scan finds no match, so dir_lookup < 0. This is the
        # `<-`/absence half of scan_reflects_present's IFF specialised to an empty
        # matches-set; the remove-witness and uniqueness are explicit HYPOTHESES
        # (NOT assertions), exactly the gap-9 trust class. Cross-validated by
        # unix-filesystem/UnixInodeFileSystem.proofs/{rocq,lean}/UnixDirScanAbsent.{v,lean}
        # (theorem remove_reflects_absent): same scan_reflects_prefix induction.
        # Rocq: Closed under the global context (0 axioms); Lean: axioms subseteq
        # {propext, Quot.sound}. The `forall j. slot_inode disk blk j >= 0`
        # antecedent is discharged at the call site by slot_inode_nonneg (above);
        # the `0 <= s < 16` antecedent is carried for call-site symmetry (vacuous
        # in both proofs — the witness alone empties the matches-set). Reuses the
        # SAME abstract slot_inode/slot_name/dir_lookup symbols (no new
        # _AXIOM_FUNCTIONS entry needed).
        "UnixFs.Dir.remove_reflects_absent":
            "forall disk : array int. forall blk : int. forall name : string. "
            "forall s : int. "
            "( forall j : int. slot_inode disk blk j >= 0 ) -> "
            "( 0 <= s < 16 ) -> "
            "( slot_inode disk blk s = 0 ) -> "
            "( forall k : int. 0 <= k < 16 -> k <> s -> "
            "    slot_name disk blk k = name -> slot_inode disk blk k = 0 ) -> "
            "dir_lookup disk blk name < 0",
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
        # UnixFs.Dir: the directory-scan reflection axiom's backing symbols.
        # `slot_inode`/`slot_name` are the abstract per-slot decode (disk, blk,
        # k) -> inode / name; `dir_lookup` is the logic model of the bounded
        # scan result. All three are `val function` (program + logic) so the os
        # model's `_dir_lookup` can BIND its result to `dir_lookup` and its
        # name_present predicate to the `slot_inode`/`slot_name` existential —
        # the load-bearing risk-2 binding that makes the cited ensures
        # constrain the REAL scan. Abstract-ops dedup skips these here.
        "UnixFs.Dir.": [
            "val function slot_inode (disk: array int) (blk: int) (k: int) : int",
            "val function slot_name  (disk: array int) (blk: int) (k: int) : string",
            "val function dir_lookup (disk: array int) (blk: int) (name: string) : int",
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
        # gap-9: an axiom-backing logic function with an `array int` parameter
        # (`dir_lookup`/`slot_inode`/`slot_name`) may be applied in a CONTRACT
        # without its qualname being cited in THIS module (the importer/driver
        # case: the os wrappers' `dir_lookup(disk, 5, name) >= 0` presence view,
        # propagated from a trusted stub). Force `use array.Array` so the emitted
        # `val function dir_lookup (disk: array int) …` decl typechecks.
        if not axiom_needs_array:
            array_fn_names: Set[str] = set()
            for _decls in self._AXIOM_FUNCTIONS.values():
                for _d in _decls:
                    if "array int" in _d or "array " in _d:
                        _p = _d.split()
                        if len(_p) >= 3 and _p[0] == "val" and _p[1] == "function":
                            array_fn_names.add(_p[2])
                        elif len(_p) >= 2 and _p[0] == "function":
                            array_fn_names.add(_p[1])

            def _refs_array_fn(node: Any) -> bool:
                if isinstance(node, dict):
                    if node.get("type") == "Call" and node.get("func") in array_fn_names:
                        return True
                    return any(_refs_array_fn(v) for v in node.values())
                if isinstance(node, list):
                    return any(_refs_array_fn(v) for v in node)
                return False

            for func in functions:
                contracts = func.get("contracts", {}) or {}
                if any(_refs_array_fn(contracts.get(k, []))
                       for k in ("requires", "ensures", "assigns")):
                    axiom_needs_array = True
                    break
        # 07-1311 Q4: collection-typed quantifier binders (in contracts) need their
        # theory even with no array/map locals — `\forall a: list;` → array.Array,
        # `\forall m: dict;` → map.Map. Scan the whole function IR (contracts + body).
        _coll_binders: Set[str] = set()
        for func in functions:
            _coll_binders |= IRScanner.collection_binder_kinds(func)
        _binder_needs_array = bool(_coll_binders & {"list", "bytes", "bytearray"})
        _binder_needs_map = "dict" in _coll_binders
        if self._value_semantic:
            needs_array = (
                has_list_param
                or any(IRScanner.uses_for(body) for body in all_bodies)
                or any(IRScanner.uses_subscript(body) for body in all_bodies)
                or any(IRScanner.uses_arrayset(body) for body in all_bodies)
                or any(IRScanner.uses_array_lit(body) for body in all_bodies)
                or any(IRScanner.uses_ghost_type(body, {"array"}) for body in all_bodies)
                or axiom_needs_array
                or _binder_needs_array
            )
        else:
            needs_array = False
        needs_minmax = any(IRScanner.uses_minmax(body) for body in all_bodies)
        needs_continue = any(IRScanner.uses_continue(body) for body in all_bodies)
        needs_break = any(IRScanner.uses_break(body) for body in all_bodies)
        needs_return_exc = False
        needs_return_void = False
        needs_return_seq = False
        needs_return_str = False
        tuple_return_arities: Set[int] = set()
        n = len(functions)
        i = 0
        while i < n:
            func = functions[i]
            has_ret = IRScanner.has_in_loop_return(func["body"]) or IRScanner.has_early_return(func["body"])
            if has_ret:
                ret_type = IRScanner.find_return_type(func["body"])
                ann = func.get("return_annotation")
                if ret_type == "unit":
                    needs_return_void = True
                elif ret_type.startswith("(") and "," in ret_type:
                    # Tuple return — needs a dedicated Return_<arity> exception
                    # so the value carries through; the plain `exception Return int`
                    # would force `_coerce_to_int` to hash the whole tuple.
                    tuple_return_arities.add(ret_type.count(",") + 1)
                elif ret_type == "array int" or ann in ("list", "bytes", "bytearray"):
                    # return-arr.md: an array-returning function with early/in-loop returns.
                    # Why3 forbids a mutable `array int` exception payload, so carry the value
                    # through an IMMUTABLE `seq int` and materialize at the catch. (The array-ness
                    # often comes from the `-> list` annotation, not find_return_type.)
                    needs_return_seq = True
                elif ret_type == "string" or ann == "str":
                    # 10-1732-gap Gap 1: a faithful `string`-returning function with an
                    # early/in-loop return carries a `string` payload — the generic
                    # `exception Return int` would mis-type it. Mirror the Return_seq
                    # machinery with a dedicated `exception Return_str string`. (The
                    # string-ness usually comes from the `-> str` annotation, since
                    # find_return_type reports `int` for a string body.) Structured so a
                    # later `Return_<T>` generalization (real/record) slots in here.
                    needs_return_str = True
                else:
                    needs_return_exc = True
            i += 1
        needs_string = (
            any(IRScanner.uses_ghost_type(body, {"string"}) for body in all_bodies)
            # strings-plan Stage 1: a runtime `str` param/local/return also needs string.String
            or any("str" in f.get("symbol_table", {}).values() for f in functions)
            or any(f.get("return_annotation") == "str" for f in functions)
        )
        # 10-2300-spec-5: the `ord`/`chr` char<->int bridge needs `use string.Char`
        # (a sibling module of the already-used `string.String`, same trusted
        # `string.mlw`). Emitted ONLY when an `ord(...)`/`chr(...)` call is present —
        # absent from the corpus, so existing emission stays byte-identical.
        needs_char = any(IRScanner.uses_ord_chr(body) for body in all_bodies)
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
        ) or any(f.get("seq_promoted_vars") for f in functions) \
          or needs_return_seq  # return-arr.md: Return_seq payload + materialize need seq.Seq
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
        # 07-1311 Q4: a `\forall m: dict;` binder needs `map.Map`/`option.Option` too.
        if _binder_needs_map:
            needs_body_dict = True
            needs_ghost_dict = True
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
            "needs_return_seq": needs_return_seq,
            "needs_return_str": needs_return_str,
            "needs_return_void": needs_return_void,
            "needs_body_dict": needs_body_dict,
            "tuple_return_arities": tuple_return_arities,
            "needs_string": needs_string,
            "needs_char": needs_char,
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
        if needs.get("needs_char"):
            # 10-2300-spec-5: the char<->int bridge (ord/chr). `string.Char` is a
            # sibling module in the SAME trusted `string.mlw` as `string.String`; it
            # provides `code`/`chr`/`get`/`.contents` and the round-trip axioms
            # `chr_code`/`code_chr` — no PyCSL-owned axiom, no TCB growth beyond the use.
            out.append("  use string.Char")
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
        if needs.get("needs_return_seq"):
            # return-arr.md: array-returning functions with early returns carry the value
            # through an IMMUTABLE seq (Why3 forbids a mutable array exception payload);
            # the catch materializes back to `array int`.
            out.append("")
            out.append("  exception Return_seq (Seq.seq int)")
        if needs.get("needs_return_str"):
            # 10-1732-gap Gap 1: a `string`-returning function with an early/in-loop
            # return carries an immutable `string` payload (parallel to Return_seq).
            out.append("")
            out.append("  exception Return_str string")
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

    def _inductive_refs_global_or_axiom_func(self, ir: Dict[str, Any]) -> bool:
        """gap-9: True iff some `#@ inductive` rule applies an axiom-backing
        logic function (`_axiom_logic_funcs`) or references a module-global
        object (by name). Gates the axioms/globals-before-inductive reorder so
        only the os family triggers it (all other inductive files keep the
        historical emission order → byte-identical)."""
        inds = ir.get("inductive_decls", [])
        if not inds:
            return False
        axiom_fns = getattr(self, "_axiom_logic_funcs", set())
        globals_names = {g["name"] for g in ir.get("module_globals", [])}
        if not axiom_fns and not globals_names:
            return False

        hit = False

        def _walk(node: Any) -> None:
            nonlocal hit
            if hit:
                return
            if isinstance(node, dict):
                if node.get("type") == "Call" and node.get("func") in axiom_fns:
                    hit = True
                    return
                if node.get("type") == "Var" and node.get("name") in globals_names:
                    hit = True
                    return
                if isinstance(node.get("object"), str) and node["object"] in globals_names:
                    hit = True
                    return
                for v in node.values():
                    _walk(v)
            elif isinstance(node, list):
                for v in node:
                    _walk(v)

        for ind in inds:
            for m in [ind] + ind.get("members", []):
                for (_rname, clause_ir) in m.get("rules", []):
                    _walk(clause_ir)
        return hit

    def _precompute_axiom_logic_funcs(self, ir: Dict[str, Any]) -> None:
        """Populate `self._axiom_logic_funcs` — the NAMES of `val function FOO`
        / `function FOO` symbols declared by the `_AXIOM_FUNCTIONS` decls for
        the qualnames this module CITES (`#@ proof`).

        A contract call to one of these (e.g. `dir_lookup(self.disk, 5, name)`
        in `_dir_lookup`'s ensures, or `slot_inode(disk, 5, k)` inside the
        `name_present` inductive rule) must lower to the raw logic application
        `(FOO args)` bound to THIS registry symbol — NOT an arity-suffixed
        abstract `FOO_3` (a fresh, axiom-unconstrained symbol). That raw binding
        is what makes the cited axiom constrain the REAL scan — the risk-2
        load-bearing binding (see `_handle_call_expr`). Idempotent; safe to call
        before inductive emission AND again from `_emit_preamble_axioms`.
        """
        self._axiom_logic_funcs: Set[str] = set()
        # (a) qualnames this module CITES (`#@ proof`).
        seen: Set[str] = set()
        for func in ir.get("functions", []):
            for entry in func.get("proof", []):
                seen.add(entry["qualname"])

        def _names_of(decls: List[str]) -> Set[str]:
            out: Set[str] = set()
            for d in decls:
                parts = d.split()
                if len(parts) >= 3 and parts[0] == "val" and parts[1] == "function":
                    out.add(parts[2])
                elif len(parts) >= 2 and parts[0] == "function":
                    out.add(parts[1])
            return out

        cited_fn_names: Set[str] = set()
        for qn in sorted(seen):
            for prefix, fn_decls in self._AXIOM_FUNCTIONS.items():
                if qn.startswith(prefix):
                    cited_fn_names |= _names_of(fn_decls)

        # (b) axiom-function names APPLIED by an `#@ inductive` rule, even when
        # the citation was stripped from injected trusted stubs (gap-9: the
        # importer drops the heavy UnixFs.Dir scan axiom but still emits the
        # `name_present` inductive, which references slot_inode/slot_name). Those
        # symbols must still bind to the registry `val function` (raw `(f args)`)
        # AND get their decls emitted (see `_inductive_referenced_axiom_decls`).
        all_fn_names: Set[str] = set()
        for fn_decls in self._AXIOM_FUNCTIONS.values():
            all_fn_names |= _names_of(fn_decls)
        ind_applied: Set[str] = set()

        def _walk(node: Any) -> None:
            if isinstance(node, dict):
                if node.get("type") == "Call" and node.get("func") in all_fn_names:
                    ind_applied.add(node["func"])
                for v in node.values():
                    _walk(v)
            elif isinstance(node, list):
                for v in node:
                    _walk(v)

        for ind in ir.get("inductive_decls", []):
            for m in [ind] + ind.get("members", []):
                for (_rname, clause_ir) in m.get("rules", []):
                    _walk(clause_ir)
        # Also any axiom-function NAME applied in a function's contract
        # (`_dir_lookup`'s `\result == dir_lookup(...)`, the syscalls'
        # `name_present(...)` arguments) — so `dir_lookup`/`slot_*` bind to the
        # registry symbol AND get declared even when the citation was stripped.
        for func in ir.get("functions", []):
            contracts = func.get("contracts", {}) or {}
            for key in ("requires", "ensures", "assigns"):
                _walk(contracts.get(key, []))

        self._axiom_logic_funcs = cited_fn_names | ind_applied

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
        # A decl already emitted EARLY (before an inductive block that references
        # it — `_emit_inductive_decls`) must not be re-declared here.
        already = set(getattr(self, "_axiom_emitted_decls", set()))
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
        declared_fns: Set[str] = set(already)
        for qn in sorted(seen_qualnames):
            for prefix, fn_decls in self._AXIOM_FUNCTIONS.items():
                if qn.startswith(prefix):
                    for fn_decl in fn_decls:
                        if fn_decl not in declared_fns:
                            out.append(f"  {fn_decl}")
                            declared_fns.add(fn_decl)
        self._axiom_emitted_decls = set(declared_fns)
        self._precompute_axiom_logic_funcs(ir)
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

    def _collect_critical_mutexes(self) -> List[str]:
        """Every mutex acquired by a `#@ critical`/`#@ acquires` section anywhere in
        the program, sorted (deterministic — the repo forbids hash-order emission).

        Used to declare the abstract diverging `acquire_<mutex>` operation per mutex:
        a lock-acquire can block forever (deadlock/contention), so it is faithfully
        modelled as a call that *may* diverge. This is what lets a worker carrying a
        `#@ \\diverges` effect type-check — its body genuinely can fail to terminate."""
        mutexes: Set[str] = set()

        def walk(stmts: Any) -> None:
            if not isinstance(stmts, list):
                return
            for s in stmts:
                if not isinstance(s, dict):
                    continue
                if s.get("stmt") == "CriticalSection" and s.get("mutex"):
                    mutexes.add(s["mutex"])
                for v in s.values():
                    if isinstance(v, list):
                        walk(v)
                    elif isinstance(v, dict):
                        walk([v])

        for func in self.ir.get("functions", []):
            walk(func.get("body", []))
        return sorted(mutexes)

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
            # A logic `predicate` cannot dereference a program mutable `ref`
            # (WhyML forbids logic from seeing mutable program state). So each
            # mutex invariant is lowered as a predicate PARAMETERIZED by the
            # plain (un-deref'd) values of the shared vars it references, and
            # every PROGRAM-context use applies it to the dereferenced refs.
            sorted_mi = sorted(mutex_invariants_ir.items())
            n = len(sorted_mi)
            i = 0
            while i < n:
                mutex, inv_ir = sorted_mi[i]
                safe_mutex = safe_mutex_name(mutex)
                self._in_spec = True
                inv_str = self._expr_to_whyml(inv_ir, set())
                self._in_spec = False
                params = self._mutex_inv_params(mutex, inv_str)
                if params:
                    sig = " ".join(whyml_ident(v) for v in params)
                    inv_bare = inv_str
                    for v in params:
                        inv_bare = inv_bare.replace(f"!{whyml_ident(v)}", whyml_ident(v))
                    out.append(
                        f"  predicate {safe_mutex}_inv ({sig} : int) = {inv_bare}"
                    )
                else:
                    out.append(f"  predicate {safe_mutex}_inv = {inv_str}")
                i += 1
            out.append("")
            sorted_mi2 = sorted(mutex_invariants_ir.items())
            n2 = len(sorted_mi2)
            i2 = 0
            while i2 < n2:
                mutex2, inv_ir2 = sorted_mi2[i2]
                safe_mutex2 = safe_mutex_name(mutex2)
                self._in_spec = True
                inv_str2 = self._expr_to_whyml(inv_ir2, set())
                self._in_spec = False
                app = self._mutex_inv_application(mutex2, inv_str2)
                out.append(f"  let _check_initial_{safe_mutex2} () : unit =")
                out.append(f"    assert {{ {app} }}")
                out.append("")
                i2 += 1
        # Faithful concurrency: acquiring a lock can block forever
        # (deadlock/contention), so the acquire is modelled as an ABSTRACT
        # operation that MAY diverge. A worker whose body enters a critical
        # section therefore genuinely *may* fail to terminate, which justifies
        # the `#@ \diverges` effect the worker declares (`functions.py:~286`).
        # Without this, why3 sees a provably-terminating body and rejects the
        # effect ("this expression does not diverge"). One `val` per mutex,
        # sorted (no hash-order). Only emitted for programs with a critical
        # section, so non-concurrency `.mlw` is byte-identical.
        acquire_mutexes = self._collect_critical_mutexes()
        if acquire_mutexes:
            out.append("  (* lock-acquire may block forever — modelled as diverging *)")
            for mutex in acquire_mutexes:
                safe_mutex = safe_mutex_name(mutex)
                out.append(f"  val acquire_{safe_mutex} () : unit")
                out.append("    diverges")
                out.append("")
        return out

    def _mutex_inv_params(self, mutex: str, inv_str: str) -> List[str]:
        """The shared vars (sorted, deterministic) protected by `mutex` whose
        deref `!name` actually occurs in the lowered invariant `inv_str` — these
        become the parameterized predicate's `int` arguments."""
        names = sorted(
            sv["name"]
            for sv in self.ir.get("shared_vars", [])
            if sv.get("mutex") == mutex
        )
        return [v for v in names if f"!{whyml_ident(v)}" in inv_str]

    def _mutex_inv_application(self, mutex: str, inv_str: str) -> str:
        """Program-context application of `{mutex}_inv`: applied to the
        dereferenced shared refs it is parameterized by (or bare if none)."""
        safe_mutex = safe_mutex_name(mutex)
        params = self._mutex_inv_params(mutex, inv_str)
        if not params:
            return f"{safe_mutex}_inv"
        args = " ".join(f"!{whyml_ident(v)}" for v in params)
        return f"{safe_mutex}_inv {args}"

    def _inductive_referenced_axiom_decls(
            self, inductive_decls: List[Dict[str, Any]]) -> List[str]:
        """Return the `_AXIOM_FUNCTIONS` `val function` decls (registry order)
        applied by any inductive rule, so they can be emitted BEFORE the
        `inductive` block (the rule references them). Empty unless an inductive
        rule actually applies an axiom logic func → existing files unchanged."""
        # `_axiom_logic_funcs` already holds every axiom-function NAME applied by
        # an inductive rule OR a function contract (populated in
        # `_precompute_axiom_logic_funcs`). Emit the matching `val function`
        # decls — minus any the axiom block already emits (cited qualnames) so
        # there is no double declaration.
        used = set(getattr(self, "_axiom_logic_funcs", set()))
        already_names: Set[str] = set()
        for d in getattr(self, "_axiom_emitted_decls", set()):
            parts = d.split()
            if len(parts) >= 3 and parts[0] == "val" and parts[1] == "function":
                already_names.add(parts[2])
            elif len(parts) >= 2 and parts[0] == "function":
                already_names.add(parts[1])
        used -= already_names
        if not used:
            return []
        # Collect the `val function` decls (registry order) whose symbol name is
        # actually applied by a rule — across ALL `_AXIOM_FUNCTIONS`, NOT just
        # cited qualnames. gap-9: the importer strips the heavy scan-axiom
        # citation from injected stubs (avoiding an E-matching OOM), but the
        # `name_present` inductive STILL needs `slot_inode`/`slot_name` declared.
        result: List[str] = []
        for prefix, fn_decls in self._AXIOM_FUNCTIONS.items():
            for d in fn_decls:
                parts = d.split()
                nm = (parts[2] if len(parts) >= 3 and parts[0] == "val"
                      and parts[1] == "function"
                      else (parts[1] if len(parts) >= 2
                            and parts[0] == "function" else None))
                if nm in used and d not in result:
                    result.append(d)
        return result

    def _emit_uncited_axiom_func_decls(self) -> List[str]:
        """Emit `val function` decls for axiom-backing logic symbols that are
        REFERENCED by a contract (in `self._axiom_logic_funcs`) but NOT already
        declared by the axiom block (`_axiom_emitted_decls`) or the early
        inductive emission. gap-9 importer case: a stripped UnixFs.Dir citation
        leaves no axiom block, yet `dir_lookup(disk, 5, name) >= 0` appears in
        the syscall/wrapper contracts. Empty unless such a referenced-but-
        undeclared symbol exists → existing files byte-identical."""
        wanted = set(getattr(self, "_axiom_logic_funcs", set()))
        if not wanted:
            return []
        already: Set[str] = set()
        for d in getattr(self, "_axiom_emitted_decls", set()):
            parts = d.split()
            if len(parts) >= 3 and parts[0] == "val" and parts[1] == "function":
                already.add(parts[2])
            elif len(parts) >= 2 and parts[0] == "function":
                already.add(parts[1])
        wanted -= already
        if not wanted:
            return []
        out: List[str] = []
        for prefix, fn_decls in self._AXIOM_FUNCTIONS.items():
            for d in fn_decls:
                parts = d.split()
                nm = (parts[2] if len(parts) >= 3 and parts[0] == "val"
                      and parts[1] == "function"
                      else (parts[1] if len(parts) >= 2
                            and parts[0] == "function" else None))
                if nm in wanted:
                    out.append(f"  {d}")
                    self._axiom_emitted_decls = getattr(
                        self, "_axiom_emitted_decls", set()) | {d}
                    wanted.discard(nm)
        if out:
            out.append("")
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
        # Collection params lower to their value-semantic Why3 type, matching the
        # rule-body lowering (a `disk: list` binder appears as `array int` in the
        # forall) — without this the header emits the unbound source type `list`.
        # A multi-word type (e.g. `array int`) must be parenthesised in the
        # space-separated Why3 inductive arg-type list.
        collections = {
            "list": "(array int)", "tuple": "(array int)",
            "bytes": "(array int)", "bytearray": "(array int)",
            "dict": "(map int (option int))",
        }
        types = []
        for part in inner.split(","):
            ty = part.split(":")[-1].strip() if ":" in part else "int"
            if ty in scalars:
                types.append(scalars[ty])
            elif ty in collections:
                types.append(collections[ty])
            else:
                types.append(whyml_ident(ty.lower()))
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
        # If any inductive rule applies an axiom-backing logic function
        # (`slot_inode`/`slot_name`/… for the `name_present` existential), that
        # `val function` decl must be in scope BEFORE the `inductive` block.
        # Emit (and record as already-emitted) exactly those decls here; the
        # later `_emit_preamble_axioms` skips them via `_axiom_emitted_decls`.
        # Gated on the inductive actually referencing one → other files (gcd,
        # struct, perm) emit byte-identically.
        early = self._inductive_referenced_axiom_decls(inductive_decls)
        if early:
            for d in early:
                out.append(f"  {d}")
                self._axiom_emitted_decls = getattr(
                    self, "_axiom_emitted_decls", set()) | {d}
            out.append("")
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

    def _emit_module_globals(self) -> List[str]:
        """inline.md Phase 1: emit each module-level global object instance `g = C(...)`
        as a Why3 mutable-record binding `let g : c = <constructor literal>`. The
        constructor `value` (a `Call` IR) reuses the record-construction lowering
        (`_call_record_constructor`); the record type `c` already carries the class
        invariant + `by` witness, which Why3 checks against the literal. Empty for
        modules with no object globals → byte-identical."""
        globals_ir = self.ir.get("module_globals", [])
        if not globals_ir:
            return []
        out: List[str] = []
        prev_spec = self._in_spec
        self._in_spec = True
        for g in globals_ir:
            rec = self._record_types.get(g["class"])
            if rec is None:
                continue   # not a known record class — skip (defensive)
            lit = self._expr_to_whyml(g["value"], set())
            out.append(f"  let {whyml_ident(g['name'])} : {rec['whyml_name']} = {lit}")
        self._in_spec = prev_spec
        out.append("")
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
            # 07-0647-spec S1.1: the Why3 type name must be a legal, non-reserved
            # identifier — `whyml_ident` lowercases AND mangles reserved words
            # (`Match` → `py_match`, avoiding the `match` keyword), vs a raw `.lower()`.
            tn = whyml_ident(vtd["name"].lower())
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
                # 07-0647-spec S1.1: reserved-word-safe Why3 type name (see variant above).
                type_name = whyml_ident(td["name"].lower())
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
                    elif ftype in ("string", "str"):
                        # 07-2333-rev2 TP-3 (Gap 6): a `str`-annotated field is a faithful
                        # Why3 `string` (was collapsed to `int`) — the class counterpart of
                        # the TP-1 str local / str param lowering.
                        ftype = "string"
                    elif ftype != "int" and not ftype.startswith(("array ", "map ", "ref ", "string")):
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
                    # L0′ (challenging-the-plan §4.1): set the self-type so a `self.<field>[i]` access
                    # in the invariant resolves the field's array type (`_field_type_of` keys on
                    # `_current_self_type`) and lowers to `Array.get`, not the unbound `subscript_get`.
                    _prev_self = getattr(self, "_current_self_type", None)
                    self._current_self_type = type_name
                    n_inv = len(class_invs)
                    i_inv = 0
                    while i_inv < n_inv:
                        inv = class_invs[i_inv]
                        inv_str = self._expr_to_whyml(inv, set(), invariant_ctx=True)
                        out.append(f"    invariant {{ {inv_str} }}")
                        i_inv += 1
                    self._current_self_type = _prev_self
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

