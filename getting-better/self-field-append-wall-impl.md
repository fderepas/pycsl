# self-field-append-wall-impl.md — implementation plan (spike-first; emission-refutation exit)

Synthesized from `self-field-append-wall.md` + `-response.md` (Gate R **CONFIRM**, 2 REFINE). The MODELING is proven
(fable `setenv_faithful.mlw`: `self._env_keys <- snoc (old self._env_keys) key` Valid, axiom-free). The M1 blast
fear is REFUTED (the facade is in NO green corpus proof). The impl make-or-break is the EMISSION: a `seq pyval`
self-field + faithful append + the fieldless-mirror retrofit, kept byte-inert by GATING.

## Design (per the fable REFINE)
- **GATE the faithful write-back on the `seq pyval` self-field case.** `self._field.append(x)` where `_field` is a
  pyval-seq self-field → `self.<field> <- snoc (old self.<field>) (<pyval-wrap x>)`. The homogeneous `array int`
  self-field appends (proc/iomod/hlib corpus) keep the CURRENT shadow-local lowering → **byte-inert** (no M1). Only
  the NEW pyval-seq-field case (the IREmitter collectors) gets the faithful write-back.
- **Retrofit the fieldless IREmitter mirror** with the needed `seq pyval` field(s) (`_final_registry` etc.) as a
  modeled record field + class invariant (the `@mutable_state` stateful-record shape), gated on a new
  `_uses_pyval_seq_field` signal → corpus + every other mirror byte-identical.
- Reuse **Phase2f** (`seq pyval` element soundness) + Why3-intrinsic `seq.Seq`/`snoc` — NO new axiom, ledger 3.

## Gate S — EMISSION make-or-break SPIKE FIRST (refutation exit)
1. Re-prove the fable model (`why3 prove -P z3 getting-better/setenv_faithful.mlw`) — reproduce Valid + axiom-free.
2. Retrofit a `seq pyval` self-field into the mirror record + emit the faithful append for a MINIMAL fixture (a
   method that appends a `{str-lit, str-var}` pyval dict to a self-field and reads it back). `pycsl <fixture>
   --keep-mlw`. Does the emitted append lower to a REAL `self.<field> <- snoc (old self.<field>) (PMap …)`
   (write-back, NOT a shadow-local), and does the file TYPECHECK + the fixture PROVE (append→read-back faithful,
   evil-twin non-vacuous)?
   - PASS → build K1 fully + K2 (converge + convert).
   - REFUTE (the fieldless-mirror seq-field retrofit won't type / forces a byte-diff on the corpus / a class-invariant
     won't discharge / the append can't gate byte-inertly) → REVERT ALL, record CERTIFIED-BOUNDARY (§ GATE-S OUTCOME)
     with the exact Why3/emit error. Do NOT grind.

## Build (only if Gate S PASSES)
- **K1 — seq-pyval self-field + faithful append emission + fixture:** the `_uses_pyval_seq_field` gate; the record
  field declaration + class invariant; the append write-back emission (statements.py ~2980/:1404 — the shadow-local
  site — gated to the pyval-seq case); a reference fixture `test-suite/corpus/pycsl-reference/0920_pyval_seq_field_
  append.<ext>` (git add -f) proving append→read-back faithfully (non-vacuous; evil-twin). Gate: fixture proves,
  corpus byte-diff 0 (gated ⇒ homogeneous appends unchanged), ledger 3. Count unchanged (infra; fixture = witness).
- **K2 — converge + convert `_collect_final_registry`:** R1 (nested `for cstmt in stmt.body` over a pyast_stmt
  LOCAL — `stmt_body` projector + propagate `_pyast_stmt_locals`) + R2 (`ast.walk(cstmt)` opaque `ast_walk:
  pyast_stmt->psl` val + loop recognition) + the K1 self-field-append + `Dict[str,PyVal]` annotation. Port verbatim,
  convert. Gate: `--fun pycsltojsonemitter___collect_final_registry` all-VCs-Valid (whole-file wedges on heavy
  Module5 → --fun authoritative per ENV note) + L3-tc ✓, fidelity 52/52 verbatim, count DOWN (1015→1014), byte-diff
  0, mutation test, ledger 3.

## Gate battery (per increment — driver-verifier FRESH)
Fidelity ∧ (whole-file proof OR --fun+wedge-note) ∧ byte-diff-0 (gated ⇒ corpus-inert; NOT M1 since gated) ∧
ledger==3 (Print Assumptions/#print axioms; reuse Phase2f) ∧ count strictly down ∧ non-vacuity (MUTATION TEST;
FIELD ACTUALLY WRITTEN BACK — grep the emitted `self.<field> <- snoc`, NOT a shadow-local; Bug-3 anti-facade).

## Honest costed scope
K1 (seq-field retrofit + append emission + fixture) is the foundation. K2 converts the first cascade collector +
banks R1/R2 (reusable for _collect_class_fields, _collect_type_params). Then the synthesize_* collectors (need
multi-arg projection + type_decls.append — a follow-on). Refutation exit at Gate S if the fieldless-mirror retrofit
walls. Corpus repair of proc argv / iomod fileio int-erasure is OPTIONAL (only to OBSERVE the effect on a green
pipeline — not required for the gated, byte-inert build).

## K1 + K2 + K3 OUTCOME (2026-07-21)
- K1 (commit 9eede7d7): faithful seq-pyval SELF-FIELD append emission (Bug 3 fix, gated on List[Dict[str,PyVal]]
  self-field, byte-inert, axiom-free reuse Phase2f). Fixture 0920. Real `self.<f> <- Seq.snoc … (pyval)` write-back.
- K2 (commit 2abd3b29): CONVERTED `_collect_final_registry` (count 1015→1014) — K1 self-field-append + R1 nested-body
  projector (`stmt_body: pyast_stmt->psl`) + R2 ast.walk projector (`ast_walk: pyast_stmt->psl`) + `.name` string-
  typing. --fun SUCCESS (whole-file wedges), byte-diff 0, ledger 3, mutation+anti-facade PASS.
- K3: BOTH REFUTE (measured, reverted clean):
  - `_collect_class_fields`: its `fields: List[Dict[str,PyVal]]` is a LOCAL returned in a tuple; pyval-seq is gated to
    SELF-FIELDS (K1) + @dataclass class-body fields only → a local/return-position List[Dict[str,PyVal]] INT-ERASES to
    `array int` (append = shadow-local facade). MISSING = LOCAL/RETURN-POSITION seq-pyval capability (append-to-local
    write-back + tuple-return carriage — the K1 analogue for locals). STACKED residuals behind it: isinstance+int()
    constant reflection, Set[str] local with .add/in, 5 mirror-absent helpers (_m5_get_list_elem_type,
    _is_dataclass_decorated, _m5_get_option_field_inner, _cf6_is_cases_list_of_dict, _m5_get_field_key_type).
  - `_collect_type_params`: `type(tp).__name__` TYPE-NAME REFLECTION over unmodeled PEP-695 type_params nodes — a
    SEPARATE wall (functions.py:2009 drops type().__name__). Not ground.
NEXT shared leverage node = LOCAL/RETURN-POSITION seq-pyval (unblocks the append-to-local piece of _collect_class_
fields + the synthesize_* collectors' type_decls.append). But each collector remains a CONJUNCTION (reflection /
multi-arg / Set[str]) — must co-land the capability with a converging target (no dead infra).

## K4 OUTCOME (2026-07-21) — CAPABILITY BUILT + Gate-S PROVEN, but NO BOUNDED CO-TARGET → REVERTED (dead infra)
- **Gate S SPIKE: PASS.** Built the LOCAL/RETURN-POSITION seq-pyval capability (the K1 analogue for locals):
  - Module5 already captures `return_value_type == "pyval"` for a `-> List[Dict[str, PyVal]]`/`-> List[PyVal]`
    return (via `_m5_get_list_elem_type`, K1's dict-value-type branch). The local annotation itself is LOST
    (`fields: List[Dict[str,PyVal]] = []` → IR `Assign target=fields value=ArrayLit[]`, no local_var_types), so the
    RETURN annotation is the byte-inert gate signal.
  - 4 edits: (1) functions.py `_compute_return_type` — `return_value_type == "pyval"` → return type `seq pyval`;
    (2) functions.py `_emit_function` — `_pyval_seq_locals = {_returned_var_name}` when the fn returns pyval;
    (3) statements.py append site — `local.append({dict})` on a `_pyval_seq_locals` local → `local := Seq.snoc
    !local (<_pyval_wrap dict>)` (real pyval write-back, NOT `Seq.snoc !local 0`); (4) stmt_control_flow return
    site — `return local` emits `!local` directly (no `materialize` seq→array int bridge); (5) preamble.py
    `_uses_pyval` fires on a pyval return so `type pyval` is in scope.
  - EMISSION VERIFIED on scratchpad/k4_probe.py: `let collector__build (…) : seq pyval = let fields = ref Seq.empty
    in fields := Seq.snoc !fields (PMap (map_update_some (map_update_some (const (None: option pyval)) "pattern"
    (PStr "Constructor")) "name" (PStr name))); !fields` — string var `name` projects faithfully as `PStr name`,
    return is `seq pyval` (no int-erasure, no materialize). TYPECHECKS (L3-tc ✓).
  - SPIKE ORACLE (scratchpad/k4_spike.mlw, verbatim the emitted shape + build→read-back driver + 2 evil twins):
    GOOD `collector__build'vc` + `test_build_readback'vc` **Valid** (Z3 0.05/0.06s; Alt-Ergo Valid too) — the tail
    reads back `PStr nm` faithfully. EvilWrongTail (wrong tail literal) and EvilNoOp (empty-seq facade) **never
    Valid** (both provers Timeout) — non-vacuous. Axiom-free (reuses Phase2f_PyVal + intrinsic seq.Seq/snoc), ledger 3.
- **NON-VACUITY: NO CONVERTING CO-TARGET within bounded reach → REVERTED ALL (dead infra).** Exhaustive scan of the
  LIVE emitter: the ONLY methods that build a genuine heterogeneous `List[Dict[str, PyVal]]` and RETURN it are the
  two collectors K3 already refuted, and both are exactly the task-excluded cases (read directly from source, not
  predicted):
  - `_collect_type_params` (M5:1871): `out.append({"name": name, "bound": bound, "kind": kind}); return out` — a
    DIRECT-return pyval list (K4 handles the return/append), BUT the dict values come from `type(tp).__name__`
    (TYPE-NAME REFLECTION over unmodeled PEP-695 type_param nodes) + `getattr(tp, name/bound)` + `isinstance(bnode,
    ast.Name/Attribute)` + the legacy `Generic[T]` branch (`node.bases`, `_extract_generic_arg_names`, registry
    lookup). A REFLECTION wall — explicitly out of scope.
  - `_collect_class_fields` (M5:2481): `fields.append({"name":str,"type":str,"mutable":bool})` returned in a TUPLE
    `(fields, field_defaults)`. Even granting K4's tuple-return carriage, the residual is STILL isinstance+`int()`
    constant reflection + a `Set[str]` local with `.add`/`in` + the `ast.walk(__init__)` — a 3+-piece conjunction.
  - Every OTHER `-> List[Dict[str, Any]]` builder (`_csl_list_to_ir`, `_comprehension_generators_to_ir`,
    `_py_stmts_to_ir`, `_synthesize_overload_guard`) appends IR-NODE dicts (`{"type"/"stmt": …}` = emit_ir), NOT
    heterogeneous pyval dicts — handled by the emit_ir machinery, not pyval. The `_synthesize_*` methods build a
    pyval-list LOCAL but STORE it into `program_ir["type_decls"].append({…, "fields": fields})` (return None) behind
    a TypedDict/NamedTuple AST-walk + program_ir-mutation wall — multi-piece.
- **VERDICT: local/return-position seq-pyval is a genuine, proven, byte-inert capability with NO bounded conversion
  co-target.** The pyval-list builders are all ≥2-more-capability conjunctions rooted in AST/type REFLECTION
  (type().__name__, isinstance+int(), TypedDict/NamedTuple walking) — the same reflection floor the
  frontier-exhaustion map records. Reverted all 4 emitter edits (git checkout, src clean = HEAD), no fixture added,
  count stays 1014, ledger 3. Do NOT rebuild K4 alone; it needs a reflection-modeling capability co-built first
  (authorize a multi-piece build), or a NEW mirror method authored to return a clean pyval list (contrived, not a
  real TCB cut).

## §K5 — `_collect_type_params` — Gate-S CONFIRM (tparam-node ADT models the reflection), but REFINE (legacy `Generic[T]` branch walls on opaque `self.program_ir` generic-dict) → REVERTED (2026-07-21)

- **Gate S SPIKE: PASS (K3's `type(tp).__name__` reflection-wall verdict REFUTED for the node-kind case).** Hand oracle
  `scratchpad/k5_spike.mlw` proves a minimal `tparam` ADT models the PEP-695 reflection FAITHFULLY + AXIOM-FREE:
  - `type tparam = TPTypeVar string emit_ir | TPParamSpec string | TPTypeVarTuple string` (name; bound sub-node is a
    BOUNDED `emit_ir` child, TypeVar only — NOT an unbounded new carrier); `tp_kind_of`/`tp_name`/`tp_bound_node`
    DEFINITIONAL projectors; `is_typevar/paramspec/typevartuple <-> tp_kind_of = "K"` faithfulness lemmas.
    `type(tp).__name__` → `tp_kind_of` is a NODE-KIND DISCRIMINANT (the pyast_stmt/emit_ir precedent), NOT reflection.
  - Bound isinstance dispatch reuses the EXISTING `is_var`/`is_attribute`/`name_of` (bnode.id / bnode.attr both →
    `name_of`), producing `option string` carried in the K4 3-key pyval entry `{"name","bound","kind"}`.
  - ORACLE: `TParamGoodFaithful` — ALL VCs **Valid** (Z3, 0.01-0.03s): concrete `TPTypeVar "T" (IrVar "int")` →
    kind="TypeVar", name="T", bound=PStr "int", entry reads back faithfully; `TPParamSpec "P"` → bound=PNone,
    kind="ParamSpec"; attribute bound `mod.Base` → PStr "Base". Evil twins `TParamEvilWrongKind` (ParamSpec-as-TypeVar),
    `TParamEvilWrongBound` (int-erased "wrong" bound), `TParamEvilDropped` (empty-seq facade) all **Unknown / not Valid**
    (non-vacuous). Axiom-free (ADT + definitional projectors + intrinsic seq/map + the reused `map_update_some`;
    `type_params_of` would be an opaque `val function` like `class_body_ast` — NO new cert, ledger stays 3).
- **REFINE (do not grind): the legacy `Generic[T]` branch is a DISTINCT, HARDER wall — opaque `self.program_ir`
  generic-dict, NOT the tparam ADT.** The method is all-or-nothing (whole body ported+proven), and its second half —
  `if not out and isinstance(node, ast.ClassDef): for b in node.bases: ... registry = self.program_ir.get("typevar_
  registry") or {}; info = registry.get(nm, {}); out.append({"bound": info.get("bound"), ...})` — depends on
  `self.program_ir` (the mirror's FIRST program_ir read; `_collect_type_params` is stubbed so no prior read exists).
  PROBE `scratchpad/k5_legacy_probe.py` (the 3-statement registry lookup, tool-emitted, NOT predicted): the tool
  INT-ERASES the whole chain — `type probe = int`, `let registry = ref 0`, abstract `val self_program_ir_get_1 (x0:int)
  : int` / `val registry_get_2 (x0 x1:int):int` / `val info_get_1 (x0:int):int`, and **L3-tc FAILS** (`info_get_1` : int
  returned where `option string` expected). This is the `Dict[str,Any]` generic-dict + opaque-self-state value model
  (the census's "85 Dict[str,Any] value-typing, likely harder than the ADT" class), NOT reflection. An opaque fused
  `registry_bound_lookup : string -> option string` reader would be a bespoke recognizer for this exact 3-statement
  idiom (Gate C facade reject); faithfully each statement lowers independently (registry:map, info:map, return:option),
  which is the full generic-dict/self-state build.
- **VERDICT: Gate S CONFIRMS the tparam-node ADT (the reflection is modellable — K5's core question answered YES), but
  the tparam ADT ALONE cannot convert `_collect_type_params`; the legacy branch adds a generic-dict/self-state
  conjunction that is a separate multi-session authorize-first build.** Building the tparam ADT now = DEAD INFRA
  (non-vacuity rule → REVERT). Made NO src edits (spike + probe are scratchpad-only); `_collect_type_params` stays the
  `\trusted` stub, count unchanged, ledger 3. NEXT: `_collect_type_params` converts once the generic-dict/self-state
  program_ir value model lands (co-build the tparam ADT WITH it); the tparam ADT + K4 append are proven-ready to reuse.

## §K6 — `_collect_type_params` map-pyval self-field cascade — Gate-S map-pyval READ PASS, but legacy-branch CHAINED pyval-`.get` is a residual 4th piece → REVERTED (2026-07-21)

- **Gate S (NEW piece: map-pyval self-field READ): PASS — real `Map.get self.program_ir "k" : option pyval`, NOT
  int-erasure.** Spike `scratchpad/k6_spike.py` (`@mutable_state @dataclass` class, `program_ir: Dict[str, PyVal]`
  field, method reads `self.program_ir.get("typevar_registry")`). The field-value-type "pyval" was NOT honored by the
  RECORD FIELD emitter — a `Dict[str, PyVal]` dict field fell through to `map string (option int)` (int-erased facade,
  L3-tc FAIL: `.get` default `(PInt 0)` : pyval vs field `option int`). The FIX is a single byte-inert branch in
  `module6_whyml/preamble.py` (record dict-field type map, alongside the existing `_vt == "string"` / nested
  `map/seq/array` branches): `elif _vt == "pyval": ftype = f"map {_kt} (option pyval)"`. After it, emit is FAITHFUL:
  field `mutable program_ir: map string (option pyval)`, read `(match Map.get self.program_ir "typevar_registry"
  with | Some v_ -> v_ | None -> (PInt 0) end)` — a REAL `Map.get` projecting `option pyval`. The pyval theory is
  already pulled in by the existing `_uses_pyval` gate (fires on ANY type_decl field `value_type == "pyval"`, preamble
  §5003), so NO new cert, ledger stays 3. κ=string via the existing `field_key_types` path (native string key, no
  str_hash_op). K5's REFUTE conditions (won't type / fieldless-mirror / class-invariant / byte-gate) ALL fail to hold:
  the field types, the mirror carries it via an `__init__` AnnAssign (the K1/K2 `_collect_class_fields` static scan —
  the mirror is NOT fieldless), and "pyval" is a corpus-absent sentinel (byte-inert).
- **REFINE — the residual 4th piece: CHAINED `.get` on a pyval VALUE (`registry.get(nm)`, `info.get("bound")`).** The
  legacy `Generic[T]` branch does `registry = self.program_ir.get("typevar_registry") or {}; info = registry.get(nm,
  {}); out.append({"bound": info.get("bound"), ...})`. `registry`/`info` are `pyval`s (the PMap arm). Probe
  `scratchpad/k6_residual.py` (tool-emitted, NOT predicted): the chained `.get` on a pyval local INT-ERASES — the local
  is typed `ref ""` (string, NOT pyval), `registry.get(nm)` emits an OPAQUE `val registry_get_1 (…)` (NOT a
  `match registry with PMap m -> Map.get m nm | _ -> None`), `info.get("bound")` an opaque `info_get_str`, and L3-tc
  FAILS. Converting this needs the "pyval-as-map chained projection" capability — (a) type a local receiving a
  pyval-typed `.get` as `pyval`, (b) lower `.get` on a `pyval` local to a PMap match-projection (likely needing a
  class-invariant that the value IS a PMap). This is the multi-statement generic-dict/self-state build K5 already
  scoped as authorize-first, NOT a leaf spike.
- **VERDICT: Gate S PASSES on its narrow question (the map-pyval self-field READ is modellable + typechecks — the 1-line
  preamble branch is proven-ready), but `_collect_type_params` is ALL-OR-NOTHING (whole body ported+proven) and its
  legacy branch inescapably contains the chained pyval-`.get` 4th piece.** So the CONVERSION does NOT converge with
  pieces #1 (tparam ADT, K5) + #2 (K4 append) + #3 (map-pyval field READ) alone. Per non-vacuity (no dead infra) the
  1-line preamble branch was REVERTED (spikes scratchpad-only, no mirror edit); `_collect_type_params` stays `\trusted`,
  count unchanged **1014**, ledger 3. BANKED proven-ready for the co-build: the map-pyval field-READ branch (§K6, 1
  line), the tparam-node ADT (§K5), the K4 local/return seq-pyval (§K4). NEXT (authorize-first): build the
  pyval-as-map chained-`.get` projection, then co-land ALL four with `_collect_type_params`.
