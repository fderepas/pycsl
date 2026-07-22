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

## 2026-07-20 (12h run) — giants emit-ir substrate = CERTIFIED-BOUNDARY (heterogeneous Dict[str,Any] value model)
User-authorized the giants substrate build for `_is_emit_ir_expr`. Spike-by-building (bottom-up, net-count gate):
- helper `_emit_ir_args_recv_ir` WALLS HARD — reads `arg_ir` HETEROGENEOUSLY in one body (`.get("type")`→string,
  `.get("values")`→array, `[0]`→node) → no single WhyML type; emit fails L3-tc (`array int` vs `int`, expressions.mlw:711).
  Exactly the `generic-dict-str-and.md` Dict[str,Any] wall (F-B1 NO-GO). Needs the FULL heterogeneous `pyval` value
  model, not a bounded reader.
- dispatcher `_is_emit_ir_expr` INDEPENDENTLY walls — `getattr(self,"_current_self_type",None) in getattr(self,
  "_mutable_state_classes",set())` self-scalar getattr-default reflection (the same pattern that re-trusted
  `_handle_fstring_expr`/`_handle_ifexpr_expr`, expressions.py:788/902).
- NET: helper trusted (+1) + dispatcher (−1) = 0, never < 1022 → net-marker-positive → ABORTED, reverted.
**The giants front (and the Dict-of-Dict collector value-model layer) share ONE research-grade root: the faithful
heterogeneous `Dict[str,Any]`/`pyval` value model + its certificate.** That is a dedicated multi-session RESEARCH
build (no-more-int "long-term EXTREME RIGOR"), not a driver-loop single/multi-piece build. Leaving these giants
`\trusted` is an ASSUMPTION, not a soundness hole. FRONTIER AT RESEARCH-GRADE FLOOR for the driver loop.

## 2026-07-20 (10h run) — the MASKED-WHOLE-FILE-BLOCKER vein (NEW; +4 conv + 4 byte-inert emitter fixes)
KEY DISCOVERY: the prior run's `no_cheap_remaining` was MASKING cheap stubs. A stub can be trivial yet
ungateable because ANOTHER stub's emitted signature breaks the WHOLE FILE's whole-file proof (the gate is
whole-file, §10.10). The prior loop only PROBED conversions; it never FIXED the emitter, so it couldn't see
past the blocker. Fixing the byte-inert emitter bug unblocks the file's gate -> its cheap stubs convert.
Detect: sweep `for f in mirror/*.py; do pycsl $f --no-proof | grep -q 'L3-tc ✓' || echo FAIL; done`.
FIVE emitter bugs found; FOUR fixed byte-inert (corpus diff 0, ledger 3), each unblocking a file/class:
1. `option (seq string)` un-parenthesized (functions.py _compute_return_type) -> `option (seq τ)` parens guard
   (mirrors _emit_dict_map_type). Unblocked Module6_WhyMLTranspiler.py -> +1 (_wrap_with_no_exception_assert).
2. undeclared-union `Return_` exception (preamble.py _emit_union_return_exceptions): an IMPORTED trusted-stub
   fn's synthesized `_union_*` type_decl isn't merged into the emitting module -> dangling unbound type. FIX:
   skip Return_ for unions not in declared_types. Unblocked audit_proof/pycsl/__init__ typecheck.
3. string-faithful lowering was gated behind @mutable_state; un-gate on declared-`string` return (ternary
   _handle_ifexpr_expr) + genuinely-string slice base (_collect_str_call_result_locals) -> +2 (BoolLit.pp,
   _indent_width) +1 sibling (_sanitize_type_name). Highest-leverage: a real no-more-int capability.
4. `self__py_expr_to_ir_1` unbound (abstract_ops.py): stmt_ir-bespoke handlers emit raw dispatcher refs that
   only get an abstract `val` when a non-stub method calls them; in an IMPORTED emitter class all methods are
   bodyless -> unbound. FIX: _register_referenced_self_dispatch_vals scans out + registers the missing vals.
   Unblocked ir_resolve/frontend.__init__ typecheck (but those stubs are dependency-stub-walled / proof-times-out).
VEIN NOW EXHAUSTED for cheap wins: unblocked files' remaining stubs are all value-model-walled (@property
vacuous, Set[str]-membership int-hash, heterogeneous-dict, collection option-int, whole-file-proof-timeout).
LESSON: masked blockers CHAIN (fix one -> next surfaces) and BOTTOM OUT at the value model. But the vein is
REAL and was invisible to the probe-only base loop — always sweep whole-file-typecheck FIRST at a claimed floor.
The 5th blocker (stmt_control_flow `{"pattern":str,"ctor":var,"captures":[list]}`) = the heterogeneous
Dict[str,Any] value-model wall = CERTIFIED-BOUNDARY (research build, now escalated: pyval-value-model-wall.md).
Also: Set[str]/frozenset membership int-hashes the string (str_hash_op) — a SEPARATE collection value-model
wall from the ternary/slice/len string capability; candidates are in the ledger file (off-limits) or compound-blocked.

## 2026-07-21 (10h run #2) — the "reflection wall" is MODELLABLE + the fixture-witness deadlock-break
Two campaign-level lessons from converting `_collect_final_registry` + `_collect_type_params` (count 1015→1013)
via the self-field-append subsystem (K1) + the tparam reflection-node ADT (L1) + the pyval value-model recognizers (L4a):

1. **AST reflection is a node-kind ADT, NOT an unmodellable wall.** `type(tp).__name__` / `isinstance(node, ast.X)` /
   `getattr(node, attr)` / `node.bases` over a Python AST node lower FAITHFULLY to a node-kind discriminant + typed
   projectors — the pyast_stmt/emit_ir precedent extended to new node kinds. L1 built the `tparam` node ADT
   (`tp_kind_of`/`tp_name`/`tp_bound`, Phase2h cert axiom-free); 7b built ClassDef-**bases** reflection
   (`is_classdef_of`/`bases_of`/`is_sub`/`svalue_of` + a faithful class-string-set-constant membership
   `str_eq_op (name_of (svalue_of b)) "Generic"`). Prior runs mis-classified `type().__name__` as the dropped
   generic reflection — it is a KIND DISCRIMINANT over PEP-695 nodes. Each new node kind = a bounded ADT-emission
   build (L1-scale); the collectors need SEVERAL (tparam, bases, ast.walk, Subscript, multi-arg call.args).

2. **The session-scale co-land deadlock breaks via the FIXTURE-WITNESS pattern.** A Module5 collector needs ~7
   value-model recognizers co-landed AT ONCE (each converts 0 alone → non-vacuity forbids committing a subset →
   they kept getting spike-proven-then-REVERTED across K4/K6/K7). FIX: commit the SHARED recognizers as infra with a
   reference FIXTURE as the non-vacuity witness (the L1/pyval-I1 precedent — an ADT/recognizer + a fixture that
   exercises it commits WITHOUT a stub conversion). L4a committed the 5 pyval recognizers (local seq-pyval / map-pyval
   field / chained .get / or-default / pyval return) + fixture 0922; L4b then only needed the node-reflection (7a/7b)
   + the conversion. This turns an all-or-nothing session-scale build into committable increments.

3. **Self-field .append facade (Bug 3):** `self._field.append(x)` emitted a shadow-local Array.make never written back.
   FIX (K1): gate the faithful `self.<f> <- Seq.snoc (old self.<f>) (pyval)` write-back on the seq-pyval field case →
   byte-inert (homogeneous array-int corpus appends unchanged). The M1 blast fear was UNFOUNDED (the facade was in no
   green corpus proof — fable-verified).

## 2026-07-21 (10h run #3) — value-model capability PLATEAU (3 infra, 0 conversions)
Run #3 built THREE committed value-model capabilities (all byte-inert, axiom-free, fixture-witnessed, count-neutral)
but converted ZERO stubs — the frontier is session-scale everywhere:
- Set[str] value model (f375baa9, set.SetApp executable + Fset spec, fixture 0923).
- const-reflection (f3888a7f, is_constant/is_num_or_float/num_of over existing emit_ir leaves, fixture 0924).
- List[RecordType] class-field emission (614fd814, `self.f: List[<rec>]`→`array <rec>`, fixture 0925).
Both redirect targets bottomed out at SESSION-SCALE emitter retrofits:
- pure_ast parser primitives (highest-count file, 262 stubs): CERTIFIED-BOUNDARY — converting even `cur` needs
  `@mutable_state` on the mirror `_Parser` = a +283-line stateful-mirror retrofit (flips the global emit_ir-theory
  gate + file-wide field-qualification); field-projecting primitives additionally wall on `*vals` varargs-membership.
- _collect_class_fields: tuple-return-pyval (R7, proven bounded) + annotation-reflection helpers (type().__name__/
  getattr on emit_ir annotation nodes) + frozenset-tuple membership — receding conjunction.
LESSON: the value-model capability-building has out-run its conversion consumers. The remaining ~1013 stubs are
dominated by stubs needing SESSION-SCALE emitter subsystems, NOT incremental recognizers. The highest-count unlock
candidates: (1) the @mutable_state stateful-MIRROR retrofit (unblocks the parser + stateful-class stubs, but +283
lines/file, risky, parser payoff capped ~3 by varargs); (2) the recursive `.values()`/`_walk_dicts` dict-generic
tree-walker model (the frontier-exhaustion-map's "85 Dict[str,Any] walkers" dominant hard class — potentially
high-count); (3) accept the plateau (extensive infra banked for a future co-land). Count 1013 held.

## 2026-07-21/22 (run #4) — the plateau was a SURVEY ARTIFACT; W8 token-cursor opened
### (a) TWO SELF-INFLICTED REGRESSIONS + a new MANDATORY gate
Run #3's shared-lowering commits (Tier-5 `pyval` ADT, Set[str]/StrSet) passed corpus byte-diff-0, their own
fixtures, AND mirror-check — while BREAKING TWO MIRROR FILES: (A) `ir_resolve.py` "Symbol PStr is already defined"
(the Tier-5 `pyval` collided with the older pydict generic-fold `pyval`; fixed by renaming Tier-5 → `hval`/`H*` —
and the fix had to include the internal `"pyval"` value-type SENTINEL, not just literal emission sites); (B)
`stmt_control_flow.py` — two CONVERTED bodies type-broken (StrSet in an int slot; nested heterogeneous dict not
pyval-gated). 41 stubs were gated behind them.
=> **MANDATORY GATE (new): any change to SHARED EMITTER LOWERING must re-run the MIRROR-WIDE L3-tc sweep**
(`for f in mirror/*.py: pycsl $f --no-proof | grep -q 'L3-tc ✓' || FAIL`) before committing. Corpus byte-diff covers
the CORPUS; mirror-check compares BODIES not emissions; a fixture only exercises the new path. The MIRROR files are
where shared-lowering changes bite. Also: **re-pin the byte-diff baseline after any M1 sanctioned reset** — it went
stale TWICE this run (after capability (i) changed 8 corpus files) and produced spurious diffs both times.

### (b) THE PLATEAU WAS A SURVEY ARTIFACT (count hygiene + the real vein)
Ledger: raw grep 1013 → 964 real function stubs (49 are docstring mentions) → **929 PORTABLE** (35 are cross-mixin
PHANTOM forward-decls whose real body lives at a sibling mixin). Census over the 929: **439 (47%) hit NO known wall**,
and **292 of those sit in THREE files behind ONE shared W8 token-cursor gate** (pure_ast 202, Module2_Parser 76,
proof2why3/parser 14). Runs #1-#3 concentrated on Module5_IREmitter + a pure_ast sub-slice and concluded
"session-scale everywhere" — that verdict was drawn from the wrong sample.

### (c) ROUND-2's W8 BOUNDARY WAS MIS-DIAGNOSED (the +283-line blast radius)
Round 2 CERTIFIED-BOUNDARY'd the token cursor because a record-typed self-field required `@mutable_state`, which
"cost +283 mlw lines". MEASURED in round 3: the record field and the emit_ir ADT theory are **fully separable** —
the +283 was the THEORY dragged in by the COARSE `@mutable_state` gate disjunct. Deferring the theory when only the
coarse disjunct fires (splice it back iff the emitted text references a symbol the theory declares — anti-drift,
conservative-safe) gives **−277 lines (303 → 26)** on the probe. Capability (i) landed (85679c71, fixture 0926) as a
clean M1 reset (8 corpus files × exactly −277/+0, all re-proved). LESSON: a "blast radius" attributed to a FEATURE
may belong to its GATE — measure the delta with the gate split before declaring the boundary.

### (d) CARVE-OUT to the fixed contract shape: PARTIAL methods take a precondition
The fixed shape is `requires True / ensures True / assigns <frame>`. `proof2why3/parser._Parser.take` steps `self.pos`
UNGUARDED (it genuinely raises IndexError past the end), so `requires True` is UNPROVABLE and the stronger class
invariant `pos < len(toks)` would be a LIE. Faithful conversion used `#@ requires self.pos < \length(self.toks)` —
the method's REAL domain. CARVE-OUT (not a licence to weaken): a precondition is permitted ONLY when it states the
method's genuine partiality; it must never be a convenience narrowing to dodge an unproved goal, and the class
invariant must not be strengthened beyond what the live code actually maintains.

### (e) run #4 FINAL — W8 token-cursor wall BROKEN: 19 conversions (1013→994), 7 capabilities, ledger held at 3
The wall run #3 CERTIFIED-BOUNDARY'd at "~3 primitives / +283-line blast radius" yielded 19 conversions once the
gate/feature confusion was measured away. Capability chain, each spike-gated + fixture-witnessed + byte-diff-0:
(i) low-blast-radius record-element class field [85679c71, fx 0926] → W1 cur/advance/take [dde9b2c7,e3a5e803, fx 0927]
→ (iii) self-field array-read projection [826b4f56, fx 0928; 0 conversions, but its census found the true shape]
→ (vi) concrete same-class sibling call w/ record return [5de7bec4,a0db955c, fx 0929; 0 conversions, found (vii)]
→ (vii) tail-return bool→int + idempotence guard [3079a72a] → (ii) varargs-membership `seq_mem_str` + CONCRETE token
kinds [0b72b5c6,498429b8, fx 0930-0932] → (v) Optional[<record>] union arm + (iv) negative literal index
[edbc597d..c30f4bab, fx 0933-0934].
BEYOND THE COUNT (tool honesty): 2 abstract vals ELIMINATED (`get_OP` was an unconstrained int making token-kind
disjointness inexpressible; `kwlist` membership was `contains_check(str_hash_op …)` with NO ensures anywhere);
3 pre-existing VACUOUS union variants repaired (`Arm_*_None`-only, no record arm: ir_schema, struct_format,
p2w/parser); 1 pre-existing emitter bug fixed (vii).
FACADES REFUSED (Gate C, left \trusted): `_err`/`error`/`unsupported` + all `expect_*` — they raise in Python but
model as value-returning no-ops (the model FALLS THROUGH to advance() on the failure path) and the f-string payload
is dropped (mutation ⇒ byte-identical .mlw). Needs a faithful raise-model/payload capability. A bogus `Arm_3_0 int`
arm was also caught pre-landing by re-gating (v) on the emitted record type_decl set.
RESIDUALS (measured, honest): `accept_*`'s guard `self.at_op(v)` still abstracts to `ensures true` (sound
over-approximation — proven content is invariant-preservation + frame; needs concrete NON-record sibling lowering);
contract-side `None` lowers to int 0; `Optional[<record>]` mutable LOCAL still `ref 0`; negative index in a VARIABLE
keeps the old lowering. NEXT: raise-model/payload capability (unlocks expect_*), then the ~80-100-stub bulk
(grammar helpers, precedence-climbing binop chains, comma/dot accumulators, keyword→single-clause constructors).

## 2026-07-22 (run #5) — L3-tc PASS IS A WEAK SIGNAL: 91% of typecheck-passers were facades
A bulk auto-porting probe over **284** `\trusted` stubs (≤5-stmt live bodies, then a ≤12-stmt band) across 48 mirror
files measured the two-stage yield precisely:
  **34/284 passed L3-tc — but 31 of those 34 were Gate-C FACADES on inspection of the emitted WhyML.**
Only 3 survived the anti-facade filter. => **L3-tc (and even a green whole-file proof) is NOT evidence of a real
conversion.** The MUTATION TEST + emitted-WhyML inspection is the load-bearing gate; without it this drain would have
banked 31 fake count cuts. Canonical facade shapes seen: the nested visitor `def` VANISHES leaving
`let found = Array.make 1 0; walk body; found[0]` (a constant); `isinstance_op 0 0`; string keys as int-hash
(`subscript_get !func_ir 1878939832`); an opaque single-call delegate (`(_check_1 expr)`); record fields silently
dropped on return (`(const (None: option int))`).
ALSO BANNED AS VACUOUS (emit no body and no VC at all — a count cut would be fake): `__init__` (absorbed into the
record type decl), `@property`, dunders (`__enter__`/`__exit__`), and any stub emitted as a bodyless `val`.

### Blocker census after the drain (highest multiplicity first — the next capability queue)
A. **nested `def`/closure dropped — ~21 stubs** (the inner visitor vanishes ⇒ constant result). Gates the whole
   `core_ir_semantic` collector family (`_body_has_raise`, `_body_has_diverging_construct`, `_lemma_returns_value`,
   `_lemma_calls_trusted`) + `canonical.alpha_normalize`. HIGHEST-multiplicity missing capability.
B. **NODE-CTOR / pure_ast node reflection** — 163 in the 3 parsers + 7 facade-passers and most of a 56-stub
   `string→int` class outside them. Two measured gaps: class-construction→ADT-ctor lowering (the DICT-literal path
   `_lower_irnode_construction`/`_IRNODE_CTORS` already works; the CLASS-construction path does not), and the
   concrete-sibling-call capability being gated on a RECORD return so an ADT-returning sibling degrades to an
   opaque self-dropping `val`.
C. raise-model — 40 (every CALLER of `error`/`_err`/`expect_*` inherits fall-through-on-raise).
D. string keys/attrs int-hashed (5+); E. opaque single-call delegates (5); F. tuple return / heterogeneous list
   literal (~7); G. os/tempfile/subprocess (~8); H. lambda/yield `_Unparser` (21).

### TOOL BUG found (real, repeatedly hit): bare `dict` param lowers INCONSISTENTLY
A bare `dict` parameter emits `map string (option int)` when the function is a trusted `val`, but
`map int (option int)` when it is a defined `let`. Un-trusting ANY function that calls a `dict`-taking trusted val
therefore ill-types AT THE CALL SITE. Worked around per-stub by annotating `Dict[str, PyVal]` (faithful — the why3
`--json` records are string-keyed); the emitter-side key-type disagreement should be fixed at source.

---

## CERTIFIED-BOUNDARY — § self-dropping reflection (`isinstance_op 0 0` / `typeof_op <const>`)

**Verdict: REFUTED as a single wall.** Probed 2026-07-21/22, spike-first, ALL CHANGES REVERTED, tree clean, count
unchanged at **988**. The `isinstance_op 0 0` emission is a shared *symptom* with **at least four disjoint roots**;
the highest-multiplicity root turned out to be **already solved**, and the one root that was genuinely missing has
**zero convertible consumers** because every consumer is blocked further downstream.

### Gate-S measurement (why the fallback fires)
`_handle_isinstance` (module6_whyml/expressions.py) tries ~8 recognizers, every one of which is gated on the tested
VALUE being recognized as a modelled node — for a `Var` that means `_is_emit_ir_expr` finding the symbol-table type
in `("ExprIR","StmtIR","IRNode","ContractExprIR")`. When no recognizer fires it emits the constant
`val isinstance_op (x: int) (t: int) : bool` applied to `0 0`.
Measured emission for `exec_splice._is_constant_exec` (live body ported into the mirror):
```
let function _is_constant_exec (call: int) : int =
  ... (isinstance_op 0 0) && (isinstance_op 0 0) ... && ((get_id (get_func call)) = 935962043)
      ... && ((iter_length 0) = 1) ... && (isinstance_op 0 0) ... && ((typeof_op 0) = 1)
```
So the root is the **VALUE typing, not the class map**: `Name`/`Attribute`/`Subscript`/`Call`/`Tuple`/`Slice` are
ALREADY in `_AST_CLASS_TO_IR_KIND` with live `_KIND_DISCRIMINANT` entries. `iter_length 0` and `typeof_op 0` are
sibling self-droppers on the same root.

### The four disjoint roots behind the "9 short stubs"
| # | stub | root | first_blocker |
|---|---|---|---|
| 1 | `Module3_Weaver._target_dotted_path` | raw-expr param typing (`ast.AST`) | **unresolved class-qualified static self-recursion** |
| 2 | `exec_splice._is_constant_exec` / `_contains_exec` | `object` annotation — never reaches `param_ast_node_types` (only `ast.<X>` is captured) | annotation root + `getattr()` forms |
| 3 | `exec_splice.splice_constant_exec` | `NodeTransformer().visit(tree)` | opaque single-call delegate = **banned facade** |
| 4 | `Module3_Weaver.visit_With` / `_attach_loop_contracts` | **CSL-contract-class** dispatch (`isinstance(c, CriticalSection/Acquires/Releases/LoopInvariant)`) over a heterogeneous `CSLNode` list — NOT ast at all | needs a CSLNode variant ADT |
| 5 | `module_collect._module_const_int`, `Module5._is_decode_call` | `Any` annotation / IR-dict `.get("type")` | value-model roots, already charted |

### The root that IS already solved (this is the key negative result)
The campaign long ago committed to the abstraction map **α: raw pure_ast expr → `emit_ir`** — `ir_resolve.py`
`_PURE_AST_FIELD_TABLE` types a raw expr CHILD (`expr.value` of a raw `ast.Attribute`) as `"ExprIR"`, and the
`IrOther` catch-all makes α total. The existing mechanism for applying α to a *parameter* is to **retype the mirror
param to the string forward-ref `"ExprIR"`** — **37 params in `Module5_IREmitter.py` already do this**, and in that
file an `ast.expr` param ALREADY types `emit_ir` via the emitter-mirror path.
A census of every live function with an `ast.expr`/`ast.AST` param isinstance-dispatched against a modelled class
found **23 functions, all but one in `Module5_IREmitter.py`** — i.e. exactly where the mechanism already applies.
**19 of the 23 are already converted; the 4 that are not are blocked by unrelated roots** (`_array_init_size`:
BinOp/Mult/List; `_collect_union_arms`: node-LIST return + flattening recursion; `_classify_literal_value`:
`Tuple[str, Any, Dict]` return; `_normalize_literal_annotation`: 15-stmt literal walker).

### What was built, measured, and then reverted
A minimal, faithful, corpus-inert capability: type an abstract-pure_ast-base param (`ast.expr`/`ast.AST`) as
`emit_ir` when it is isinstance-dispatched against a modelled class (`_uses_pyast_expr` gate; no reference-corpus
program performs an isinstance against a pure_ast class, so it is corpus-inert by construction), plus the projector
coverage (`.id`/`.attr`→`name_of`, `.value`→the pre-existing UNIFIED `avalue_of`, which is the correct projector
because a raw `.value` is the IrAttr OBJECT child on an Attribute and the IrSub ARRAY child on a Subscript — the
bare `svalue_of` default would be WRONG on the Attribute branch), plus the emit_ir-theory and
ambiguous-field-qualification gates.
It WORKS at the discriminant level — measured before/after on `_target_dotted_path`:
```
- if (isinstance_op 0 0) ... (module3_Weaver__target_dotted_path_1 (get_value target)) ... (get_attr target)
+ if (is_sub target)     ... (module3_Weaver__target_dotted_path_1 (avalue_of target)) ... (name_of target)
+ if (is_attribute target) ... if (is_var target) -> Arm_0_0 (name_of target) | Arm_0_None
```
Both operands live, real ADT discriminants, real `Optional[str]` union arms. **Byte-diff of the
`Module5_IREmitter.py` mirror before/after = 0** (confirming the change is inert exactly where the existing
mechanism already covers).
**But it converts nothing.** Its only reachable consumer outside the emitter mirrors is `_target_dotted_path`, and
that hits the next wall:

### NEXT WALL (the real blocker, newly isolated)
**Class-qualified static-method self-recursion is not resolved.** `Module3_Weaver._target_dotted_path(target.value)`
inside `Module3_Weaver._target_dotted_path` does NOT bind to the enclosing method; it emits an unconstrained
abstract `val module3_Weaver__target_dotted_path_1 (x0: int) : int` with **collapsed-int params** — which then
ill-types against the now-`emit_ir` argument. Fixing it needs (a) call resolution for `<OwnClass>.<staticmethod>`
self-calls, AND (b) recursive-`let rec` emission with a structural `variant` (the `size` measure exists in the
emit_ir theory but there is no path to emit it as a program-function variant).
Gate-C note: leaving it as the abstract `val` would be a textbook facade (the recursion vanishes), so this stub is
**not convertible** until (a)+(b) land.

### Instruction to the next driver
Do NOT re-run this probe. The `isinstance_op 0 0` count is NOT a measure of one wall's multiplicity — the ~163
NODE-CTOR and ~19 `_union_c8_walk` stubs listed against it belong to blocker **B** (class-construction→ADT-ctor)
and to the heterogeneous IR-dict value model respectively, neither of which the reflection fix touches. The
remaining raw-expr surface is covered by the `"ExprIR"` retype convention; where that convention is not applied the
stub is blocked by a *different* root. The genuinely new, well-isolated capability requests from this run are:
1. class-qualified static-method **self-recursion resolution + `variant` emission** (blocks `_target_dotted_path`,
   `_collect_union_arms`, and every structural AST recursion);
2. a **CSLNode contract-class variant ADT** (blocks `visit_With`, `_attach_loop_contracts`, and the Weaver family);
3. capturing `object`/`Any` param annotations is NOT the answer — it is too broad to gate safely; annotate the LIVE
   source precisely instead (`ast.expr`), which is a faithful source improvement.

## § NODE-CTOR (blocker B) — run #6, 2026-07-22: capability BUILT, chain conversion CERTIFIED-BOUNDARY

### Census FIRST — the "163 stubs" figure is INFLATED ~3x
Measured by parsing every `\trusted` stub's LIVE body and asking whether it constructs a node CLASS
(`ast.walk` over `Call(func=Name)` against the module's own `ClassDef` set):

| file | `\trusted` stubs | actually NODE-CTOR | claimed |
|---|---|---|---|
| `frontend/pure_ast.py` | 240 | **6** | 106 |
| `frontend/Module2_Parser.py` | 75 | **48** | 46 |
| `proof2why3/parser.py` | 16 | **2** | 11 |
| **total** | 331 | **56** | 163 |

Of the 48 in `Module2_Parser`, only **20** are the expression chain that can target the `emit_ir` ADT; the other
~28 build *declaration* nodes (`Requires`/`Ensures`/`LoopInvariant`/…) for which no ADT sum exists at all. Of the
72 distinct CSL classes those 20 construct, ~10 (`CSLIn`, `CSLNotIn`, `DictView`, `ChainedSubscript`,
`NestedSubscript`, `GlobalFieldSubscript`, `FieldSubscript`, `SubscriptFieldAccess`, `MkTupleExpr`, `ProjExpr`)
have **no** `emit_ir` counterpart. Honest reachable set for this blocker: **tens, not 163.**

### Gate S — three gaps measured, all THREE fixed (emit before → after)
1. **class-construction ≠ ADT ctor.** `BinOp(left, op, right)` → `{ binop_left = …; binop_op = …; binop_right = … }`
   (a `binop` RECORD literal) → *"has type binop, but is expected to have type emit_ir"*.
   FIXED by `_call_irnode_constructor` (expressions.py): reuses the SHARED `_IRNODE_CTORS` table, binds the ctor
   payload **by name** off the class's positional `__init__` params, and DECLINES on any unbound slot.
   Now → `(IrBinOp !op !left !right)`.
2. **ADT-returning sibling call was opaque.** `self._parse_factor()` → `val self__parse_factor_0 (self) : emit_ir`
   with **no `requires`/`ensures` at all**. The concrete-sibling gate was `ret_type in <record types>`.
   FIXED (2 lines) by widening it to `("emit_ir", "int", "string")` — still under the `_record_array_fields`
   @mutable_state gate. Now → `(_contractparser___parse_factor self)`, and a SELF-recursive call binds too.
3. **varargs guard was RECEIVER-LESS.** `self.at_op("*","/")` → `val self_at_op_1 (x0: seq string) : int` — could
   not see `self`, so the loop guard had no relation whatsoever to the cursor. Same 2-line fix →
   `(_contractparser__at_op self (Seq.cons "*" …))`, against the real verified definition.

Supporting: `-> "ExprIR"` on a `pass`-bodied `\trusted` stub now yields `emit_ir` rather than `unit`
(functions.py, both return-type maps); `Return_emit_ir` is declared off the *annotation* as well as the
dict-literal body shape (preamble.py).

### The chain still does NOT convert — TERMINATION, not node construction
7 precedence levels (`_parse_implication`…`_parse_factor`) were converted verbatim, reached **L3-tc ✓**, emitted
genuinely faithful bodies (distinct concrete operator token sets, concrete `at_op`/`advance`/sibling calls, real
`IrBinOp` nodes) and PASSED a 2-way mutation test — but the whole-file proof went **SUCCESS (139 Valid, 0 unproven)
→ FAILED**, on exactly three sub-goal classes per method: *termination*, *type invariant*, *postcondition* of the
`while self.at_op(...)` loop. Reverted; count restored 1017.

**Root cause (certified).** `advance` increments the cursor only while `self.i < len(self.toks) - 1`, so the
measure `\length(self.toks) - self.i` stops decreasing at the last index. The loop really terminates only because
`_lex_contract` appends an EOF sentinel (`toks.append(_Tok("EOF", "", n))`) whose kind is never `"OP"`/`"NAME"`.
Stating that requires

    #@ class invariant self.toks[\length(self.toks) - 1].py_type == "EOF"

and **the contract grammar rejects it**: *"unexpected trailing input (got OP '.')"* — a `.field` projection off a
SELF-FIELD subscript is unparseable. The two sibling forms are asymmetric: `<name>[i].<field>`
(`SubscriptFieldAccess`) and `\result[i].<field>` both PARSE, but the former then lowers to an **unbound
`subscript_get`** in a class-invariant context. So neither spelling reaches a usable sentinel invariant.

### Instruction to the next driver
The node-construction and sibling-binding halves of blocker B are **DONE and banked** (witness fixture
`0935_class_construction_adt_ctor.py`, proved, mutation-tested). Do NOT re-spike them. The chain is now gated on a
single, narrow, well-isolated request:

> **`self.<array-of-record field>[idx].<subfield>` in a contract** — parse it (grammar), and lower it in a
> class-invariant/`ensures` context to the record projection off the array read (the machinery already exists for
> the `<name>[i].<field>` and `\result[i].<field>` forms; only the self-field form is missing end-to-end).

With that, the EOF-sentinel invariant becomes stateable, `at_op`'s postcondition can carry
`\result ==> self.i < \length(self.toks) - 1`, and the loop variant `\length(self.toks) - self.i` discharges — at
which point the ~8 loop-carrying precedence levels convert on the capability landed here. Do NOT attempt the
declaration-node half (~28 stubs) — it needs a CSLNode declaration ADT that does not exist.

### (f) run #5 — a TRUSTED stub's FALSE frame silently licenses unsound proofs
Converting the `Module2_Parser` precedence chain exposed five still-`\trusted` siblings (`_parse_impl_rhs`,
`_parse_or_rhs`, `_parse_and_rhs`, `_parse_membership`, `_parse_unary`) declaring `#@ assigns \nothing` while their
LIVE bodies call `advance` (which mutates `self.i`). The converted `while self.at_op(...)` loops would then have
proven TERMINATION off a FALSE premise. Fixed to `assigns self.i` + `ensures self.i >= \old(self.i)`.
VERIFIED SOUND (driver): the sole backtracking site `_try` (`saved = self.i; … except: self.i = saved`) has exactly
ONE call site (`self._try(self._parse_assigns_region)`), outside the chain — and the reset is `_try`'s own effect,
not the callee's, so per-method monotonicity holds. `_try` itself must NOT carry a monotone `ensures`.
**LESSON: a trusted stub's contract is an ASSUMPTION — an over-tight `assigns` is not "conservative", it is FALSE,
and every caller's proof inherits the lie. When converting a caller, re-read each trusted callee's frame against its
LIVE body before trusting the resulting proof.** (This is a distinct failure mode from the facade family: the body is
real, the proof is real, but the premise is fabricated.)

### (g) run #5 — two SMT/lowering facts worth remembering
- **Alt-Ergo cannot prove string disequality** (`"OP" <> "EOF"`); Z3 can. Best-of-N hides this, but a goal that
  needs string distinctness will look "hard" if Alt-Ergo is tried alone.
- **A Python `bool` lowers to `int`**, so the guard yields `o <> 0` and an `ensures \result == True ==> …` is
  VACUOUSLY USELESS. Write `\result != False ==> …` instead.
