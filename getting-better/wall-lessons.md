# wall-lessons.md — resolved-wall ledger (self-tcb-reduction driver)

Each entry: a wall the driver RESOLVED as CERTIFIED-BOUNDARY / DEFERRED (measured, not a cheap win), with the
L-input that revealed it. BROKEN walls are in the git log (conversions).

## 2026-07-20 driver run (count 1030 → 1028; 2 conversions + these walls)

### BROKEN (converted)
- `_extract_generic_arg_names` (List[str] returns) — commit 3f38bd78. Fix: `needs_return_seq_str` on `return_value_type=="string"`.
- `_is_null_byte_lit` (ArrayLit of Number 0) — commit dc493048. Added faithful `num_of` emit_ir Number-value projector.

### CERTIFIED-BOUNDARY / DEFERRED walls (measured; each needs an authorize-first build)
- **`_symtype_to_whyml` / Optional[str]-PARAM comparison** — `symtype == "str"` on an `Optional[str]` param int-HASHES
  the literal (`symtype = 1917410062`, union-vs-int typecheck FAIL). Item #5 covered Optional LOCALS, NOT param
  comparison. Fix = MODELLING change: option-unwrap the comparison (`match symtype with Arm_1_0 s -> str_eq_op s "str"
  | Arm_1_None -> false`) + a C8 union-narrowing recognizer treating string-literal equality as a valid guard.
  Byte-diff-RISKY (shared comparison lowering) → authorize-first, FLAGGED not auto-dispatched. Re-confirmed twice.
- **`_val_is_bool`** — conversion itself PROVES faithfully, but ARCHITECTURAL Gate-5 wall: the live method moved
  `statements.py`→`types.py` (already converted there via the record path), so the `statements.py` mirror copy is an
  ORPHAN cross-mixin resolution stub — `mirror-check` flags "un-trusted mirror def not in source" once converted.
  Non-convertible without a mirror/live file-realignment (out of the loop's scope).
- **`_union_c8_recognized_guard`** — top-level reads go faithful with `test:"ExprIR"`, but `for side in
  (test.get("left"), test.get("right"))` needs literal-tuple-unroll + `side.get(...)`/`args[0]` need
  list-subscript-into-emit_ir; `func=="isinstance"` int-hashes. Multi-feature build.
- **Generic `for v in node.values(): walk(v)` tree-walkers** (7+ in `core_ir_semantic.py`: `_contains_result`,
  `_body_has_raise`, `_body_has_return`, `_lemma_returns_value`, …) — the untyped-IR-nested-dict `.values()`
  reflection wall. Retired only by a certified generic IR-tree FOLD over the pyast/ExprIR ADT. Highest-count family.
- **`_collect_union_arms`** (§8c) — 5-piece: List[emit_ir] returns + worklist tree-size-SUM termination variant.
- **`_collect_typevar_registry`** (§8d) — Dict[str,Dict[str,Any]]: variable-valued dict-literal DROP + Any int-erase.
- **Two live-tool faithfulness BUGS** (`faithfulness-bugs-found.md`): dict-literal-drop (empty map, false-theorem
  generator) + negative-slice-empty (`s[1:-1]`→`""`). Verified fixes exist but can't co-land (mirror can't re-prove
  the fixed body — the emit_ir sub-node value model). Common root with the collectors.

### The single highest-leverage unlock
The **emit_ir-typed sub-node value model** (tool-method `.get("expr")`/`.get("left")` reads typed `emit_ir` not
`int`) is the common root of: both faithfulness bugs, `_union_c8_recognized_guard`, the collectors, and the
`.values()` walkers. Closing it (a certified generic IR-tree read/fold) is the highest-leverage multi-session build.

### Environment note
The monolithic whole-file proof WEDGES on driver-verifier RE-RUNS (0 VCs or post-VC finalization hang, 0% CPU) while
the executor agents' runs discharge cleanly — treat an agent's clean SUCCESS + independent byte-diff-0 + mutation-test
+ count + fidelity + allowlist as the verdict when a re-run wedges (document it).

## 2026-07-20 (12h run) — proof-viable small-build frontier EXHAUSTED
After +2 conversions (`_body_has_return` stmt-catamorphism, `_build_method_return_annotation_map` flat-strdict) +
Bug 1 soundness fix, a measure-before-build drain returned `no_small_build_remaining`. Findings:
- **STRUCTURAL: per-file mirror-sync blocks the "duplicate-stub" family.** A stub `\trusted` in file A whose live
  method lives (and is converted) in file B CANNOT be converted in A — `self-annotate-mirror-check.sh` rejects
  "un-trusted mirror def not in source". Validated on `_array_coerce_arg` (emitted faithfully + passed mutation,
  but rejected — lives in expressions.py, stub in statements.py). Invalidates `_field_label`/`_val_is_bool`/
  `_bool_ir_to_int_wrap`/`_str_operand_to_int`/`_array_coerce_arg`/… as convertible-where-stubbed.
- **PROOF-ENV: `core_ir_semantic.py` whole-file proofs WEDGE why3** (0% CPU hang) on heavy combined theory (stmt
  catamorphism + a ~60-arm expr fold). `_body_has_return` (lighter) proved; adding the expr fold wedged. Blocks the
  tree-walk expr-fold family (`_contains_result` built+evidenced but reverted; patch banked).
- Cheapest genuine remaining (all multi-piece): setfold method-call-guard + pyval-domain predicate emission
  (`_collect_dict_var_assigns`/`_collect_variant_var_assigns`); Dict[str,Dict[str,str]] self-field record-metadata
  value model (`_callable_tag_to_whyml`/`_is_emit_ir_expr`); keyword-node modeling + nested-map (`_collect_typevar_registry`).

## 2026-07-20 (12h run) — SINGLE-BUILD frontier EXHAUSTED after +5 conversions
Landed this run (1027→1022): `_body_has_return` (stmt catamorphism), `_build_method_return_annotation_map`
(flat-strdict), `_collect_dict_var_assigns` (setfold method-call-guard), `_collect_variant_var_assigns` (setfold
ctor-membership+prefix), `_callable_tag_to_whyml` (opaque-selfmap 2-level reader) + Bug 1 soundness fix. Then the
reader/recogniser veins EXHAUSTED:
- opaque-selfmap reader's clean frontier is done — the only remaining consumers (`_is_emit_ir_expr`,
  `_handle_subscript`) are GIANTS behind the emit-ir helper cascade (`_emit_ir_args_recv_ir`/`_mktuple_elts_recv_ir`/
  `_is_pyast_stmt_emit_ir_read` + `_EMIT_IR_*` constants, all absent from the mirror) — a NET-MARKER-POSITIVE
  giants-front build (port would ADD ≥3 stubs to remove 1), NOT a single-reader win. And their 3-level read is a
  `.get()` chain with a computed key (no bound-alias subscript to match).
- setfold clean shapes done; remaining Set[str] collectors have heavy self-dict-of-dict / nested-def closures.
**Remaining reachable = deliberate MULTI-SESSION builds only:** (a) the emit-ir helper substrate + giants front
(net-positive per giant_conversion_net_positive, but a 77-helper-DAG multi-session build); (b) core_ir_semantic
proof-env resolution (why3 wedge; unblocks the tree-walk expr-fold family, `_contains_result` patch banked);
(c) keyword-node modeling + nested-Dict[str,Dict] return (`_collect_typevar_registry`); (d) `List[emit_ir]`
returns + worklist termination (`_collect_union_arms`). No clean single-build +1 remains.
