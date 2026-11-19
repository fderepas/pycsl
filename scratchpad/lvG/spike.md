# lvG §0 make-or-break spike S1 — `List["ExprIR"]` return lowering (vm-irnode-wall-impl.md §0)

Base: run5-int37 0ce6ece57. Spike tree: detached worktree /home/fabrice/git/pycsl-lvG-spike (scratch only, no commit).

## The spike patch (2 live lines + 1 recognizer arm)

- `src/pycsl/frontend/ir_resolve.py` (`_resolve_same_file_node_spec_records`, NOT mirrored): the forward-ref ELEMENT
  spelling `List["ExprIR"]` (a real `Subscript` whose slice is the string Constant `"ExprIR"` / `"StmtIR"` / `"IRNode"` /
  `"ContractExprIR"`) records `return_annotation = "list"`, `return_value_type = "emit_ir"` exactly as the quoted
  `-> "List[ExprIR]"` spelling already did.
- `src/pycsl/module6_whyml/functions.py::_compute_return_type` (mirror twin VERIFIED -> re-port + functions.py
  whole-file proof OWED when wired): the existing `ann == "list" and return_value_type == "emit_ir"` -> `array emit_ir`
  branch, gated `_uses_pyast_parser()`, also fires for a method of a `@mutable_state` class.
- The return site needs nothing: `stmt_control_flow.py`'s RECORD-ELEMENT bridge already emits
  `(materialize_emit_ir !out)` for a declared `array emit_ir`, and `_emit_function` declares the bridge val.

## p13 re-run (QUICK, `scratchpad/lvG/spike/p13.sh`)

| tag | what | L3 |
|---|---|---|
| p13s1 / p13s1d | `_csl_list_to_ir` verbatim + `List["ExprIR"]` param/return (+ the raises / \diverges of `_csl_to_ir`) | ✗ — return now `: array emit_ir`, tail `(materialize_emit_ir !out)` (the p13 `seq emit_ir` vs `seq int` error is GONE); next error `this expression depends on variable _pyobj_state, which is left out in the specification` = the `getattr(c, "act_name", None)` reflection read |
| p13s1b | same minus the honest raises contract | ✗ `raises unlisted exception PyCSLIRError` (contract, not model) |
| p13s1c | p13s1d with the 3 `act_name` lines removed (SCRATCH isolation only) | **✓** |

So the RETURN half is clean; the verbatim `_csl_list_to_ir` is blocked by two non-return links: the
`getattr(c, "act_name", None)` reflection residue (reads `_pyobj_state`) and the `d["act_name"] = an` store, which §1
(route #566) now REFUSES outside the mirror (and in the mirror lowers to the unmodelled no-op). Recorded, as the plan
predicted (§2: "_csl_list_to_ir will NOT convert verbatim").

Second consumer (QUICK, `s044b`): `_ContractParser._parse_expr_list` (s044, census need MIRROR-RETYPE +
cap-vm-unerase-list) with `-> List["ExprIR"]`: L3 ✓, `: array emit_ir`, `(materialize_emit_ir !exprs)`.
`_encode_callable_annotation` (s083): L3 ✗ on `iter_length (args_of ..)` / tuple-unpack of `args_of` — a different wall.

## Corpus byte-diff

No corpus program and no mirror returns `List["ExprIR"]` today (grep over test-suite/corpus/pycsl-reference,
python-reference and src/self-annotate/src: 0 hits), so the spike is inert by construction outside the mirror method
it is aimed at. The queued spike-tree sweep was dropped for queue time (the heavy queue held every NORMAL slot for
hours); the corpus byte-diff of the S1 wiring is the §2 sweep, whose only corpus-visible change IS S1 (the s044
conversion is mirror-only): root 2932 -> 2938 0 MOVED / 0 GONE / 0 APPEARED (+6 new sources = §1 controls), python-reference 2185 0 / 0 / 0 (sweep bd-g3 vs bd-base at 0ce6ece57) -- the S1 gate "0 MOVED" holds.

## Later probes on the same wiring (§3 spike, QUICK, scratch only)

- s013 `run_ir_semantic_checks` port-as-is: REFUSED `PYCSL-R325-OPAQUE-INT-FALLBACK` (`trusted_funcs = set(ir.get(..) or [])`,
  cap-R325-call-set-ctor) -- the census's first link. With that one line replaced by `set()` (scratch isolation): L3 ✗
  `This expression has type int, but is expected to have type pyval` at `_check_span !func stage` -- the erased `func`
  entry fed to callees whose verified signatures take the pyval carrier (`Dict[str, PyVal]`). A `FunctionView` record
  would have to match 18 callee interfaces typed two different ways: the "a retype rewrites the interface every caller
  was verified against" wall. R3 STOPPED for core_ir_semantic.
- s137 `_fresh_globals_facts`: L3 ✗ `array int` vs `int` (preamble.mlw:573). s140 `sort_functions_by_scc`: REFUSED
  growable-list (`sorted_names.append` on a non-growable local). Different walls; no FunctionView chain reachable.
- `_csl_in` with the live CSLIn retype (`element/collection: "ExprIR"`) on the §1 tree: REFUSED
  PYCSL-R567-EMITIR-ATTR-ON-NONIR at `dv.kind` (DictView is record-modelled) -- the misprojection is now caught, as the
  plan intends; the retype alone converts nothing, so it is NOT landed.

## Verdict

**PASS (with a REFINE note).** The make-or-break question -- can a `List["ExprIR"]` mirror return lower to
`array emit_ir` + `materialize_emit_ir` -- is answered yes, by an annotation-gated recognizer arm and one widened gate,
corpus-inert. It does NOT convert `_csl_list_to_ir` verbatim (as the plan predicted): its next links are the
`getattr(c, "act_name", None)` reflection read (`_pyobj_state` left out of the specification) and the
`d["act_name"] = an` store (route #566, refused outside the mirror). REFINE: the list half's next wall for s072 is the
reflection residue, not the return model. First consumer that converts: s044 `_parse_expr_list` (§2).

## §2 landing (lvG, the commit after the §1 commits)

- Wiring: `ir_resolve.py` recognizer arm (not mirrored) + `functions.py::_compute_return_type` gate (mirror twin VERIFIED:
  re-ported verbatim; `--fun functionemissionmixin___compute_return_type` 1088 Valid / 0 non-Valid).
- Conversion s044 `_ContractParser._parse_expr_list` (Module2_Parser mirror): `\trusted` removed, live body verbatim,
  mirror signature `-> List["ExprIR"]`, contract `ensures self.i >= \old(self.i)` / `assigns self.i`, the
  `_parse_act_names` loop annotations. `--fun` is unusable on this file at the base (the --fun trusted-sibling `val`s keep
  their `variant` clause -> Why3 "unexpected 'variant' clause"; same for the already-verified `_parse_act_names`), so the
  gate is the WHOLE-FILE proof (LOW): 884 Valid / 0 non-Valid, 1572 s; mutant (`ensures self.i > \old(self.i) + 1000`):
  FAILED, exactly 1 unproven goal = `_contractparser___parse_expr_list'vc` postcondition (883 Valid).
- Corpus: root 0 / 0 / 0 (+6), pyref 0 / 0 / 0. Mirror vs base: MOVED exactly frontend__Module2_Parser (the conversion +
  the `materialize_emit_ir` val) and module6_whyml__functions (the re-ported gate); pycsl.mlw and
  Module6_WhyMLTranspiler.mlw were GONE in the loaded sweep (900 s per-file timeout) and re-emitted standalone
  BYTE-IDENTICAL to base. OWED: module6_whyml/functions.py whole-file proof (driver battery).
