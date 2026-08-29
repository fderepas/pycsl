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

### (h) run #5 — the out-param frame family collapses from 54 to 1 under measurement
The (f) audit flagged **54 "out-parameter mutation" stubs** (`assigns \nothing` while the live body mutates a
collection PARAMETER) but declined to judge them — it had not established PyCSL's by-reference semantics for
collection params. Four emit probes settle it, and the answer is **type-dependent**:
- **Dict param → BY REFERENCE.** Emits `d: ref (map string (option int))` with `writes { d }` derived from the
  declared `#@ assigns`. A *converted body* that writes it under `assigns \nothing` is **FAIL-CLOSED** — Why3
  rejects with *"This function has side effects, it cannot be used as pure"*. A *trusted stub* is not (no body is
  seen), so there the false frame is a real premise defect.
- **List param + subscript store** (`acc[0] = 7`) → `acc: array int`, same fail-closed behaviour.
- **List param + `.append`** → **NOT by reference**: lowered to a local copy `let acc = ref (snapshot acc)`. The
  caller's list is unchanged, so `assigns \nothing` is **TRUE OF THE MODEL**. No false premise — but the model
  DIVERGES from Python, where `list.append` on a parameter mutates the caller's list. Recorded below as a
  faithfulness bug; note the failure is *incompleteness* (the caller cannot prove the effect), not unsoundness.
Census under that measure (trusted ∧ `assigns \nothing` ∧ Dict-typed param ∧ live body mutates it): **9 candidates,
8 read-only, 1 real** — `_extract_happy_properties` (`contracts_map[line] = kept`), fixed in `99fe2e75`.
**LESSON: before mass-fixing a flagged family, probe the LOWERING for each type in it. "Mutates a param" is not one
defect class — it is three, with different verdicts, and only the by-reference one is a soundness defect.**

**Open faithfulness bug (live tool, affects all users, not just the mirror):** `param.append(x)` silently
snapshot-copies the parameter, so a caller can never observe the append. Either lower list params by reference
(matching dicts) or reject `.append` on a parameter — the current silent copy is a semantics divergence of exactly
the kind the no-more-int / faithful-semantics doctrine forbids.

### (i) run #5 — `check-self-annotate-sync.sh` is a PERMANENTLY-RED gate and carries no information
The driver's `L` fidelity plane names TWO gates. `bin/self-annotate-mirror-check.sh` is green (52/52) and is the one
the campaign has actually gated on. `bin/check-self-annotate-sync.sh` reports **115 DIVERGED** today — and **81 at
`70b0748f`, this run's starting commit**, so it has been red for many sessions. Its output is dominated by
differences the mirror introduces BY DESIGN or by normalization, not by drift:
- mirror-added type annotations (`def cur(self):` vs `def cur(self) -> _Tok:`) — required for lowering;
- quote-style normalization (`"OP"` vs `'OP'`) — it compares `ast.unparse` output against raw source;
- docstrings the mirror omits (27 of 115);
- and its `\trusted` detection is broken — it reports a `pass`-bodied trusted stub as an "un-trusted mirror body".
**LESSON: a gate that is always red is not a conservative gate, it is a DISABLED one — it can never fire a new
signal, and every actor learns to skip it. Fix it (normalize both sides, honour `\trusted`) or retire it from the
`L` plane explicitly; do not leave it in the battery as decoration.** Same structural defect as (f): something
stated as a constraint that in fact constrains nothing.

### (j) run #5 — the dead gate was hiding 14 REAL drifts; "converted" did not mean "verbatim"
Repairing `check-self-annotate-sync.sh` (lesson (i), commit `5aeb2279`) dropped it from 115
divergences to **14 real ones** — and every one is a genuine §10.4 violation: a feature edited a
VERIFIED emitter method and did not re-port its mirror in the same commit, so the mirror proof has
been discharging a **stale copy** of the live code. That is the campaign's own first-named dominant
failure ("mirror drift — a stub that verifies a stale copy"), running undetected for months because
the only gate that compares BODIES was red, and the gate everyone cited
(`self-annotate-mirror-check.sh`, green 52/52) compares only `(kind, qualname, n_params)`
SIGNATURES and cannot see a body change at all.

The 14 sort into four kinds, and only the first is what anyone would have guessed:
1. **Missing feature branches** (most) — live grew a branch the mirror never got. Five are this
   run's own `pyval` -> `hval` rename. Fix = port verbatim; free, no count change.
2. **A missing HELPER** — `_handle_var_expr` needs `_union_local_read_projection`, which does not
   exist in the mirror at all. Porting faithfully means adding it as a trusted stub: **count +1**.
   The honest reading is that the count was ALREADY overstated by this method — it was booked as
   converted while proving a body the emitter does not run.
3. **A TRUNCATED payload** — `_py_stmt_assign`'s mirror had quietly shortened a multi-line
   `PyCSLSemanticError` f-string to one clause. Semantically live for anyone reading the error.
4. **A HAND-REWRITE, not a port** — `_pattern_has_constructor`'s live body is
   `any(self._pattern_has_constructor(a) for a in pat.get('alternatives', []))`; the mirror is an
   index-counting `while` loop. Equivalent-looking, but the proof covers a body the emitter never
   executes. This is a DISTINCT facade family from the ones Gate C catches: the emitted `.mlw`
   changes under mutation (so it passes the anti-facade test) and the body is real — it is just
   not the LIVE body.
**LESSON: "converted" has silently meant three different things — ported, rewritten, and
truncated. Only the first supports the claim that proving the mirror proves the emitter. A count
of converted stubs is only as meaningful as the body-fidelity gate behind it, so NEVER let that
gate stay red; and when re-porting is blocked, record the stub as drifted rather than leaving a
green proof over a body the tool does not run.**

### (k) run #5 — a byte-diff sweep from a fresh worktree emitted ZERO files and still reported "diff 0"
`bin/byte-diff-sweep.sh` hard-codes `PY="$ROOT/.venv/bin/python3"`. A detached worktree created for
a baseline has no `.venv`, so every emit silently failed, the sweep wrote **0 files**, and
`diff -rq base head` compared two EMPTY directories and returned 0 — a perfect false green for the
single most important gate on any `src/pycsl` change. Fixed by symlinking the repo `.venv` into the
worktree; the real run then emitted 782 vs 782, diff 0.
**LESSON: a diff of 0 is meaningless without the population count. `byte-diff-sweep.sh` prints
`emitted N` — READ IT, and assert N matches the corpus size, on BOTH sides. Any gate whose pass
condition is "no differences found" must separately prove it looked at something.**

#### (j') the full body-fidelity census, once the gate worked
With `check-self-annotate-sync.sh` repaired, the mirror admits a COMPLETE census (not a sample):

| | count |
|---|---|
| un-`\trusted` mirror functions WITH a live counterpart — actually gated | **336** |
| …of which byte-faithful to live after the re-ports | **331** |
| …of which still divergent (enumerated in the `374279ac` commit message) | **5** |
| un-`\trusted` mirror functions with NO live counterpart — SKIPPED by the gate | **10** |
| `\trusted` stubs with no live counterpart (deliberately relocated across mixins) | 35 |

The 10 ungated ones were the real thing to check — an un-`\trusted` mirror body with no live
counterpart is not drift but FABRICATION, a proof over code the emitter does not contain. All 10
are the same documented one-line infra shim (`def mutable_state(cls): return cls`). So there is no
fabrication, and body-fidelity holds for **331 of 336** converted methods.
**LESSON: when a gate skips a case "by design", COUNT the skips and look at them — `if name not in
live: continue` is where a fabricated body would have hidden, and the census is what turns "skipped
by design" from an assumption into a checked fact.**

### (l) run #6 — the MUTATION TEST cannot see int-hash erasure; a body can pass it and still be vacuous
The campaign's anti-facade gate (Gate C) is: perturb a discriminant in the body, and the emitted
`.mlw` must change. `IRScanner.uses_string` PASSES that test and is nevertheless a total facade:

```python
def uses_string(obj):                    let irscanner__uses_string (obj: int) : int =
    if isinstance(obj, dict):              if ((typeof_op 315) = 4) then
        if obj.get("type") == "String":      if ((obj_get_1 1342639453) = 1153884070) then
            return True                         raise (Return 1)
        return any(IRScanner.uses_string(v)  else raise (Return (if (any_1 (Array.make 1 0))…
                   for v in obj.values())
```
`typeof_op 315` and `obj_get_1 1342639453` are applied to HASH CONSTANTS, not to `obj`; `"String"`
is the int `1153884070`; `any(genexp)` is `any_1 (Array.make 1 0)` where `val any_1 (a: array int)
: bool` is UNCONSTRAINED and its argument is fabricated. **`obj` does not appear in the body at
all.** The mutation test passes precisely BECAUSE of the erasure — changing `"String"` changes its
hash, so the output moves while the body still computes nothing.

**The gate that does catch it is structural: a body that never references a parameter cannot
compute anything about it.** Implemented as `bin/check-emitted-vacuity.py`, cross-checked against
the LIVE body so the many methods that legitimately ignore an argument (`_csl_nil(node)` returns a
constant literal) are not reported — only "live uses it, emitted does not". Verdict today: **8
fully-erased + 4 partially-erased VERIFIED functions**; all 8 fully-erased are IRScanner's
generic-`Any`-tree predicates (`uses_string`, `uses_sum`, `_check`, …).

This intersects lesson §10.3 (generic-`Any` tree walkers are not modellable) with an unwelcome
twist: they were **converted anyway** and booked as verified. Note also that unconstrained-oracle
erasure is SOUND-but-vacuous, not unsound — an arbitrary `bool` guard forces the verifier to prove
both branches — so nothing false was ever derived. What was lost is CONTENT: the proofs say
nothing about what these nine functions compute.

**LESSON: an anti-facade test that watches the OUTPUT of the emitter can be satisfied by erasure
itself. Test the STRUCTURE instead — does the emitted body read its inputs? Any future
"non-vacuity" gate should ask what the proof CONSTRAINS, not merely whether the artifact moved.**

Two false-positive classes cost real time while building the probe, both generalizable: reading a
body from the line AFTER the signature misreports every ONE-LINE definition (76 bogus hits), and
matching a parameter name without blanking STRING LITERALS makes `{"stmt": "Break"}` look like a
use of the `stmt` parameter (3 bogus hits). **Validate a new probe against known-good cases before
believing its headline number** — the first two runs of this one said 118 and 76.

### (m) run #6 — the Rocq certificate build fails IN-REPO but succeeds CLEAN; the artifacts are stale, not the proofs
Verifying `ledger == 3` the honest way — by BUILDING rather than by asserting it — `make -C
src/formal-semantics/rocq` **fails**: `Phase3_SOS.v:400: The reference SLambda was not found in the
current environment`, even though `Phase1_AST.v` defines `SLambda` and `Phase3_SOS.v` imports it.
No `.v` file was modified, so this reproduces at HEAD.

**My first hypothesis was that the certificates were broken. That was WRONG, and the refutation is
the point.** Copying `rocq/` to a scratchpad, deleting every build artifact and rebuilding from
clean: **exit 0, 64/64 `.v` compiled, zero errors.** The proof SOURCES are sound.

What is actually wrong is the committed ARTIFACTS. `.vo`/`.vok`/`.vos`/`.glob` files are TRACKED IN
GIT, and git does not preserve mtimes — so on checkout a stale `.vo` can appear newer than the `.v`
it was built from, and `make` silently accepts it and mixes stale with fresh. The dates make the
mechanism concrete: `Phase3_SOS.v` was last modified **2026-07-01** by `1637e746` ("Phase 8 —
SLambda closure construction, **both provers**"), while the committed `Phase3_SOS.vo` dates from
**2026-06-29** — two days EARLIER. That commit changed 19 source files and **zero** `.vo` files.

So the ledger claim was never false, but for a while it was UNCHECKABLE in the repo: anyone running
the documented `make` got a failure unrelated to their change, which trains exactly the "that gate
is always broken, skip it" reflex that killed `check-self-annotate-sync.sh` (lesson (i)).

Confirmed unchanged regardless: the project ledger is exactly **3** `Axiom` declarations —
`why3_implements_wp_w` (Phase6i_Soundness), `alt_ergo_correct` and `trusted_contracts_axiom`
(Phase5b_Soundness). None is in the failing file or in any Phase2* ADT certificate.
(Incidental, worth knowing: `Print Assumptions pycsl_soundness_verified` on the clean build reports
two STDLIB axioms — `propositional_extensionality` and `functional_extensionality_dep` — which are
classical and pre-existing, not project axioms, but they are assumptions and nobody had written
them down.)

**LESSON: never commit build artifacts for a proof assistant. Git does not preserve mtimes, so a
tracked `.vo` is a stale certificate that `make` will trust over its own source — the certificate
analogue of proving a stale mirror copy (lesson (j)). Gitignore them and rebuild from clean, or the
"certified" claim rests on a binary nobody can reproduce. And when a build fails, test the CLEAN
build before concluding the proofs are broken: here the sources were fine and only the artifacts
were rotten.**

### (n) run #7 — a sub-agent that BACKGROUNDS a census and then STOPS leaves an ownerless writer on the tree
The first Phase-1 drain agent converted 38 stubs cleanly (981->943) and exited with a clean tree. The
Phase-1 RE-DRAIN agent did not: it launched a `scratchpad/sweep.py` measure-before-build census with
`run_in_background`, said "I'll wait for the sweep completion event", and STOPPED — leaving the sweep
running under the session with no owner. A census does port -> prove -> REVERT per file, so the tree was
observed MUTATING in real time after the agent reported "completed": count bounced 943->941->942->938 and
different mirror files (`ir.py`, `monomorphize.py`, `from_lean_json.py`, `parser.py`) flickered dirty as the
sweep walked them, each with a `*.py.bak` backup. Killed mid-cycle, the sweep left ~5 files stuck in the
ported (marker-removed) state that never got reverted, so a naive count read **938** — a phantom "-5" that
was pure artifact.

Diagnosis that worked, in order: (1) confirm the tree is actually mutating (`count` + `git status` sampled
3x with a gap — do NOT trust a single mid-census count); (2) trace the PARENT CHAIN of the live
`pycsl.py` proc (`ps -o pid,ppid,cmd`, walk ppid up) — it resolved to `sweep.py` under THIS session's
`claude --resume`, proving it was my own orphan, not the separate `claude` session that also showed in
`ps`; (3) confirm the sweep writes results only at the END (`json.dump` after the loop) so a mid-kill has
nothing to salvage; (4) kill the sweep + its shell + its pycsl child + a stale 6-day `run_gate.sh` orphan;
(5) `git checkout -- src/self-annotate/` (the SANCTIONED use of the destructive command — the working-tree
changes are a dead census's garbage, HEAD is the verified state) + `find -name '*.py.bak' -delete` (checkout
does not remove UNTRACKED .bak files); (6) confirm count STABLE over 12s with no writer before trusting it.

**LESSON: a driver sub-agent must do all of its proving/sweeping IN THE FOREGROUND of its own turn and
return a concrete verdict — never background a census and stop, which converts it into an ownerless writer
that races the driver and corrupts increments. And the driver must, on EVERY sub-agent return, (a) verify no
repo-writing process is still alive (parent-chain trace, not just `pgrep`), and (b) treat the count as
untrusted until it is STABLE across several seconds. A single count read taken during a live census is a
phantom.** The 38-conversion batch itself was unaffected (committed, independently re-proved 8/8 SUCCESS
before the re-drain ran); only the uncommitted re-drain residue was discarded.

### (o) run #7 (Phase 2) — the vacuity gate's self-state blind spot: closed, and the booked set is CLEAN
The run-#7 re-drain flagged that `bin/check-emitted-vacuity.py` checks only PARAMETER erasure, so a
self-ONLY method that erases its `self.*` reads to a constant (`summary` → `""`, `process` → `0`) passes
it while being fully vacuous — the self-state analogue of (l). Measured and closed this Phase-2 increment.

**The booked set is CLEAN.** Extending the check to self-state and running it over all 943 booked
(`let`/verified) conversions finds **0 input-blind methods** — no already-converted stub is a self-state
facade. (The agent's `summary`/`process`/`message`/`as_dict` examples are `\trusted` `val` stubs it
temporarily un-trusted during its sweep and reverted — never booked; the worry is about FUTURE conversions,
which the gate now guards.)

**CALIBRATE BEFORE BELIEVING — the naive self-check over-fires 148/236 (63%).** Two false-positive
mechanisms, both load-bearing:
1. **Sibling-call reads.** A method that reads `self` only to CALL a sibling (`self._expr_to_whyml(x)`)
   emits a self-LESS bridge (`self__expr_to_whyml_2 x`) with no `self` argument — faithful, not a facade.
   Fix: count only self DATA-FIELD reads (a `self.<attr>` Load that is NOT a call callee); 148 → 3.
2. **Bridge-name field encoding.** `self._precedences.get(...)` emits `self__precedences_get_2 …` and
   `self._source.extend(t)` emits `self__source_extend_1 …` — the field is in the FUNCTION NAME, and
   `\bself\b` does NOT match `self__…` (a `_` is a word char, so no word boundary). Counting the `self__`
   bridge form as a self-use: 3 → 1.
The last 1 (`_union_arm_tag`, reads `self.program_ir`) is a REAL method that dispatches on its `elt` param
faithfully — only its record-arm branch degrades (the documented genexp `any_1` site). It is NOT a
self-only facade. The SOUND signal is INPUT-BLIND: the emitted body references NONE of its inputs — every
data param the live body uses is erased AND (if live reads self-state) no `self`/`self__` appears. That
clears `_union_arm_tag` (uses `elt`) → **0**.

**Gate hardened, `emitted_references_self` + `live_self_fields` added, mutation-tested 4 ways** (positive
facade fires; bridge-name, bare-self, and param-use all correctly cleared). Existing param behaviour
unchanged (12 known, exit 0). **LESSON: a self-state vacuity check is NOT a copy of the param check — the
self-field lives in the emitted BRIDGE NAME as often as in a `self` token, and a `\bself\b` test misses it
(a 63% false-positive cliff). The only sound facade signal is INPUT-BLIND: references none of {data params,
self-state} at once; anything that touches one input is real. Same calibrate-before-believe discipline that
took the param probe 118 → 76 → 12.**

### (p) run #8 — CHECK THE EXISTING VALUE MODELS BEFORE SCOPING A NEW CERTIFICATE BUILD
The 18h R2d+R3 run authorized a certificate-touching build (R3: swap the hval HMap carrier from a
Why3 map to an assoc-list, so `.values()` folds). It was spiked, verified axiom-free, landed — and
turned out UNNECESSARY. R2d de-vacuified all 8 IRScanner predicates via the PRE-EXISTING Phase2c
`pydict` catamorphism, whose `pydict = DNil | DCons key val rest` is ALREADY the iterable assoc-list
R3 rebuilt for the (younger, Phase2f) hval family. Two certified value models existed — the older
pydict (assoc-list, iterable) and the newer hval (map carrier, non-iterable) — and the wall report,
the fable reviewer, AND the driver all reasoned only about hval, missing that pydict already solved
`.values()`. R3 is banked (verified, byte-inert, a legit capability for hval-typed walkers) but was
avoidable session-scale + certificate work.
**LESSON: before scoping a NEW value-model/certificate build to unblock a wall, ENUMERATE the value
models that already exist and are certified, and check whether one already has the shape you need.
Here `grep` for the existing catamorphisms (`pydict`/`size_dict`, `pyval`/`pv_size`, `stmt_ir`) and a
spike porting ONE stub onto each would have shown pydict sufficed — before authorizing a certificate
touch. The fable review does not substitute for this: the reviewer reasoned from the report's hval
framing and inherited its blind spot. A "what existing capability already does this?" census is a
distinct, cheap gate that belongs BEFORE the report→review→impl cycle for any build that proposes a
new certified construct.**

### (q) run #8/18h — the count is blocked on EMITTER RECOGNITION, not provability (measured 3× over)
Across this run the same wall shape held for every count-moving cluster — sexp/tuple carrier, the
closure/nested-`def` family (item 4), the `ast.*` family (item 3), and the residual drifts: the
VALUE MODEL and its CERTIFICATE prove AXIOM-FREE (sexp: `Print Assumptions` = "Closed under the
global context", `sexp.mlw` positive/evil-twin non-vacuous; likewise hval/pyval/stmt_ir before it),
but the EMITTER RECOGNIZER cannot lower the verbatim live body onto the model. The sexp case is the
sharpest: cert proven, value oracle proven, yet `t[i]` is consumed as BOTH a string and a sub-sexp
at the same syntactic form (context-directed coercion the emitter lacks), the helpers build a
`List[str]` the single-string oracle sidesteps, and dispatch is on a string tag — three recognizer
features for −3 stubs.
**This SHARPENS §10.3.** The generic-`Any`/tuple/closure walkers are NOT "unmodellable" — they are
MODELLABLE and CERTIFIABLE; the bottleneck is that bridging each Python IDIOM (positional
heterogeneous tuple-walk, `List[str]` accumulation, mutable-closure `found=[False]`, `ast.*`
dispatch) to the proven model needs a BESPOKE per-idiom recognizer, each ~3 features for a few
stubs. So the residual count is a MULTI-SESSION RECOGNIZER-ENGINEERING program with per-cluster
diminishing returns, NOT a transcription backlog and NOT a provability wall.
**LESSON: when a count-moving target's value model + cert prove but conversions don't land, the
wall is the RECOGNIZER, not the math — and spiking the model/cert (which will pass) is NOT evidence
the build will convert. The decisive spike for these is the RECOGNIZER falsifier (can the emitter
lower the VERBATIM body's idiom?), run BEFORE the cert/emitter build, because the cert is the easy
part. Bank the proven model+cert as reusable oracles, record the recognizer blocker, and do not
build cert+emitter infra that has no converting consumer (no-dead-infra).**

### (i,k,g,j,m) CARVED into skill §10c (2026-07-24, item-8)
The five flagged judgment-call lessons — (i) dead-gate=disabled, (k) byte-diff population, (g) two SMT facts, (j) count-a-gate-skips, (m) never-commit-proof-artifacts + canonical-count — are now base-loop RULES in `self-tcb-reduction/SKILL.md` §10c items 16-20 (they were mistakes made >1x, so they bind future runs, not just document past ones). No longer "awaiting user decision".

## Wall: trusted method-val drops `#@ assigns self.<field>` frame — CERTIFIED-BOUNDARY (2026-07-27)

Report: `getting-better/trusted-val-assigns-writes-wall.md`. Phase-2 escalation after Phase-1
`no_cheap_remaining` at 877. Symptom: `parse` can't prove its `assigns self.i` because its only
effect is a trusted `_parse_contract` (`#@ assigns self.i`) call that emits **effect-free** — both
emission paths exclude the trusted-val self-field case (`_emit_frame_condition` skips self-object
targets for vals; the `_module_method_writes` machinery is gated `and not emit_as_val`).

**Make-or-break spike (measured, then reverted clean): REFUTE.** The one-line fix (drop `and not
emit_as_val`, emit `writes { self.<field> }` for the trusted-val + `@mutable_state` case) makes
`parse`'s OWN VC fully Valid — the targeted frame IS breakable in isolation — but refutes on two
independent gates:
1. **Sibling-proof invalidation (soundness finding).** `_parse_lock_order` (loop invariant/variant)
   and `_parse_interface` (postcond) proved at baseline ONLY because their trusted callees
   (`_parse_assigns`, `_parse_mutex_expr_str`) were unsoundly effect-free. Emitting the faithful
   `writes { self.i }` havocs `self.i`; the callees carry no monotonicity/bound `ensures` to
   re-establish the invariants → 4 new unproven goals. **The current "verified" mirror has methods
   that are green only because trusted callees under-declare their effects.**
2. **Unbound-field target.** Module5_IREmitter L3-tc breaks: a trusted method's
   `#@ assigns self._cur_func_symtab` names a field that is NOT a bound mutable record field →
   `unbound function or predicate symbol '_cur_func_symtab'` (the "unbound target" hazard the
   statements.py:1849 comment warned of, resurfaced as an unbound symbol).

**Corpus-inert (report premise CORRECTED).** byte-diff = 0 across 812 programs; NO corpus program
has the (trusted-val ∧ @mutable_state ∧ assigns self.field) combination (0661/0662 aren't
@mutable_state; 0900/0901's trusted method is `__init__`/`assigns \nothing`). So this is NOT a
corpus-perturbing risky brick — the blocker is proof-invalidation, not blast radius.

**LESSON: emitting a faithful frame onto a previously effect-free trusted val is soundness-IMPROVING
but not a free win — it can INVALIDATE sibling proofs that silently depended on the effect-free
unsoundness, and it requires each assigned self-field to be a bound mutable record field. The real
cost is (a) strengthening every affected trusted callee with faithful monotonicity/bound `ensures`
(the blessed parser-vein pattern) so siblings survive the havoc, AND (b) making the assigned fields
real mutable record fields. Multi-method, multi-file — beyond a single-stub spike. FLAGGED for the
user: this surfaced a latent unsoundness (effect-free trusted callees) worth a dedicated
faithful-frame campaign, not an autonomous inline land.**

## Wall: _pb_stmt/_cs_stmt trio-fusion — CERTIFIED-BOUNDARY (feasible, authorizable; 2026-07-27)
After `_pb_expr` (875) unblocked its callers, `_pb_stmt` spiked → REFUTE for a single additive
increment, but the spike PROVED it is NOT a proof wall: a standalone `.mlw` (11 goals Valid) shows
termination works with existing `pyval`/`pydict`/`pv_size` + size-carrying extraction postconditions
+ a **lexicographic 2-component variant `{size, phase}`** (the naive single `pv_size` fails only at
`pb_descend(v)→pb_stmt(v)` equal-size; phase clears it). Ledger stays 3, NO new value-shape/cert/axiom.
**Why it's a BOUNDARY for autonomous landing:** `_pb_stmt` is MUTUALLY RECURSIVE with the
already-converted walkers `_pb_body`/`_pb_descend` (today trusted `_pb_stmt` is called by opaque
`int`/`0` handles). Converting it forces: fuse the trio (+helpers) into ONE `let rec…with…` group;
RETYPE + RE-EMIT `_pb_body`/`_pb_descend` (int→pyval/string/sdict) — i.e. PERTURB converted walkers;
a NEW cross-function trio-fusion emitter that claims the trio + suppresses the corpus-shared generic
`recognize_void_dispatch`/`recognize_void_generic_descend` emissions for it while leaving the generic
path intact for corpus code; emit-deferral after `_pb_expr`. This is a reorder + shared-emitter
modelling change that re-emits VERIFIED artifacts = the RISKY-brick class (unlike additive byte-inert
`_cp_walk`/`_pb_expr`). `_cs_stmt` = same fusion + trusted `_cs_clause` prerequisite (needs
`_ir_free_vars` too).
**LESSON: the walker vein splits into TWO risk classes — ADDITIVE recognizer extensions (new matcher,
backward-compatible, byte-inert, converted walkers untouched → auto-landable under gates:
`_cp_walk`/`_pb_expr`) vs MUTUAL-REC FUSION (must re-emit converted walkers + new cross-function
fusion architecture + emission reorder → FLAG/authorize, don't auto-dispatch). The `{size,phase}`
lexicographic variant + size-carrying extraction-helper postconditions are the banked, proven
termination recipe for the fusion build when authorized.** FLAGGED for the user as a de-risked,
authorizable multi-feature increment (files: generic_fold.py fusion emitter, functions.py
dispatch+suppression, mirror _pb_stmt/_pb_body/_pb_descend), gated by whole-file proof + corpus byte-diff 0.

## REFINEMENT (2026-07-27): _pb_stmt trio-fusion — the real terminus is WHOLE-FILE E-MATCHING SATURATION
The fusion BUILD was executed (scoped trio-fusion emitter + mirror `_pb_stmt` body) and passed EVERY
gate EXCEPT the whole-file proof: corpus byte-diff **0** (scoping correct — no corpus leak), §10c
all-7 importer L3-tc ✓, vacuity 0, fidelity drift 2, `_pb_stmt` a faithful structured dispatcher.
The whole-file proof failed with exactly **1 unproven goal**: postcondition of `_pb_stmt__body'vc`,
`Timeout (30s, 32.6M steps)`. Diagnosis (measured, not assumed): NOT a missing local postcondition —
local asserts add subgoals and still time out; the blowup is **E-matching over the recursive
`wf_dict`/`wf_ir_binds` predicates in the FULL whole-file solver context**. The prior spike proved the
same VC Valid in ISOLATION (11-goal standalone .mlw) — so the fusion is sound and feasible in
isolation; the terminus is whole-file **solver-context saturation** (same class as act_block/for_block
and the parser solver-context-saturation terminus), a proof-SCALE wall.
**LESSON: a spike that proves a VC in an isolated .mlw does NOT prove it discharges in the FULL
whole-file context — E-matching over the file's recursive well-formedness predicates
(`wf_dict`/`wf_ir_binds`) can saturate the solver when the new goals are added. The isolation spike
measures FEASIBILITY (the math works), not whole-file PROVABILITY (the §10.10 gate). To land the
trio-fusion, the missing piece is MODULAR VERIFICATION (prove the trio in a separate module / restrict
the wf_* triggers), which touches the whole-file-proof gate = REVIEW-GATED. The fusion EMITTER itself
is built + validated (byte-diff 0 / §10c / vacuity / sound-in-isolation) and banked for that session.**
FLAGGED for the user: trio-fusion needs a modular-proof approach, not just the fusion emitter —
a bigger, §10.10-gate-touching lift than the earlier "authorize the fusion build" framing implied.

## Wall: _pb_stmt trio-fusion — BROKEN (2026-07-29, user-authorized), supersedes the CERTIFIED-BOUNDARY
The trio-fusion, previously recorded CERTIFIED-BOUNDARY (whole-file "E-matching saturation → modular
verification, review-gated"), is now BROKEN and the boundary framing was WRONG on two counts, both
caught by MEASUREMENT: (1) NOT an E-matching-over-wf_* problem — deleting `wf_ir_binds` left the failing
goal's Alt-Ergo step count unchanged (~92.9k) vs 0.26s in isolation, so the cause was generic full-module
CONTEXT SIZE, not that lemma's instantiation; (2) NO modular isolation / trigger surgery was needed. The
fix was a better-SHAPED extraction helper: route the trio's two child extractors through ONE shared
recursive `_pb_stmt__dget : pydict -> option pyval` whose postcondition is on `pv_size` (Z3 discharges in
0.05s), and make the list extractor a NON-recursive wrapper (`pv_size (PList xs) = 1 + size_list xs`, one
unfold). Prover cascade Alt-Ergo→Z3 closes all 60 trio goals; whole-file 449 Valid / 0 unproven;
corpus byte-diff 0; ledger 3.
**LESSON: a "whole-file solver saturation" terminus is a HYPOTHESIS about the CAUSE, not just the
symptom — MEASURE which term drives the blowup (delete the suspected lemma/predicate and re-count steps)
before concluding "needs modular verification / trigger surgery / review-gate". Here the real lever was
re-SHAPING the emitted helper (a shared recursive `pv_size`-carrying extractor + a non-recursive wrapper)
so the solver discharges the size VC structurally in a small step budget — an IN-SCOPE emitter fix, not a
§10.10-gate change. Two consecutive boundary diagnoses on this wall were both wrong; the win came from a
step-count differential, not from authority.**

## Wall: exception_model string-keyed-set — CERT/AXIOM boundary at bases_closure (2026-08-02, authorized)
User-authorized string-keyed-set κ-campaign. The membership MODEL is SOUND + proven (isolated spike:
handler_catches core `raised in bases_closure(handler)` over `map string bool` = Valid 0.01s). BUT the
cluster is gated behind `bases_closure` — a worklist BFS (`pop`/`seen.add`/`frontier.extend(get(b))`)
over the string->list-of-strings exception hierarchy. Over the abstract `map string (list string)` NO
well-founded variant exists (`get(b)` can encode an unbounded/cyclic chain); the loop proves terminating
ONLY with a NEW codomain-bound AXIOM (`∀k x. mem x (get k) -> mem x u` for a bounded universe u) + a ghost
Fset mirror + 3 loop invariants + a lexicographic variant — none of which PyCSL auto-synthesizes and the
axiom violates ledger-3. `subclasses_of.candidates` is unannotated -> fail-closed (a guessed κ = facade).
`all_phase1_exceptions` = out-of-vein (`sorted(KNOWN_EXCEPTIONS)`, a separate array-string-order feature
with corpus byte-diff risk on the shared `sorted`). CORRECTLY did NOT smuggle the axiom.
FLAGGED narrow path (not auto-built, safe-vs-risky): handler_catches alone converts IF bases_closure gets
a faithful `-> frozenset[str]` annotation (string-typed but stays trusted) + Module5 κ + Module6 bool-return
+ in-over-call-result — a live-emitter modelling change with byte-diff risk (touches shared `sorted`).
LESSON: the string-keyed-set MEMBERSHIP model is sound + reusable, but a set BUILT by a worklist/frontier
BFS over an abstract map has no dischargeable variant without a bounded-universe axiom — apply the model to
COLLECT-walkers (bounded structural recursion, e.g. ir_inline _assigned_locals) NOT frontier-BFS builds.

## WALL (2026-08-02): census `--no-proof` over-count — the inline-recursive `.values()` bool-walk
`ir_scanner.py::uses_inline_set_or_dict_ops` was flagged CHEAP-PASS by a census that used only
`pycsl <file> --no-proof` (L3-tc). REPRODUCED base-loop lesson #1: `--no-proof` does NOT discharge
the TERMINATION VC. The verbatim port type-checked but the WHOLE-FILE proof TIMED OUT on exactly
`irscanner__uses_inline_set_or_dict_ops'vc` sub-goal "termination" (3× Timeout 30s) — the inline
self-recursive `for v in obj.values(): if self(v): return True` walk fell to a NAIVE emission whose
variant Why3 can't discharge in-context. REVERTED (count held 830). NOT a cheap win.
BUT NOT a hard boundary either: the sibling `collection_binder_kinds` (SAME `.values()` inline
recursion, SET-returning) PROVES green in the same ir_scanner whole-file context because it matches
`recognize_setfold`, which emits the certified `pv_size`-variant fold. So the make-or-break spike for
a bool variant is PRE-SATISFIED. FIX = a `recognize_bool_existence_values` recognizer + emit modeled
on `emit_setfold_group` (OR-fold bool over the `pv_size`-variant `.values()`/list descent, with the
dict-node early-return predicate; `.endswith` → opaque `val pystr_suffix` result-unconstrained, not an
axiom). Leverage: ~3 bool stubs (uses_inline_set_or_dict_ops, _is_decode_call, _test_contains_map).

## BOUNDARY (2026-08-02): _check_noreturn — body-representation mismatch (needs the pyval→stmt_ir bridge cert)
Measure-first spike on the campaign-3 target `_check_noreturn` (core_ir_semantic; the SOLE remaining
trusted stub of the noreturn cluster — siblings _collect_noreturn_names/_check_noreturn_successors/
_noreturn_walk_stmts/_stmt_is_noreturn_call all converted). Verbatim port FIDELITY-clean (drift stays 2),
but the whole-file typecheck FAILS. Root cause (precisely located, NOT a value-soundness cert):

_check_noreturn calls THREE already-converted body-helpers on the SAME `body = func.get("body")`:
  - `_body_has_return`  : emitted `stmt_list -> bool`  (matches recognize_stmt_has — "Return"=SReturn
     is a known stmt_ir ctor, so it lowered via the bespoke `stmt_ir`/`stmt_list` ADT).
  - `_body_has_raise` / `_body_has_diverging_construct` : emitted `list pyval -> bool` (their tags
     "Raise"/While/For/Call are NOT stmt_ir ctors → they fell to the generic pyval `.values()` walk).
`func.get("body")` is a `list pyval` (pget_list). It type-checks against the latter two but COLLIDES
with `_body_has_return`'s `stmt_list` param. There is NO axiom-free `list pyval -> stmt_list` bridge —
the real one (`_py_stmts_to_ir`) is TRUSTED.

I built recognize_check_noreturn + emit (pyval-model, field-truthiness guards, pget_list body, raise
declared) — it matched + emitted faithfully, but hit exactly this `_body_has_return` type collision.
Three resolution paths, all rejected for autonomous inline landing:
  (A) UNIFY: make `_body_has_return` emit `list pyval` like its siblings → requires stopping
      recognize_stmt_has from matching the "Return" walk = perturbs a SHARED corpus recognizer (byte-diff
      risk). Rejected.
  (B) INLINE: emit a local `list pyval` "Return"-existence walk in _check_noreturn. FACADE — the tag
      "Return" would be HARDCODED in _check_noreturn's emitter, so changing `_body_has_return`'s tag
      would NOT move _check_noreturn's .mlw → FAILS the mutation test. Rejected (Gate C).
  (C) BRIDGE: an axiom-free `pyval -> stmt_ir` / `list pyval -> stmt_list` parser (the de-trusted
      `_py_stmts_to_ir`) + co-landing Phase2* cert → lets _check_noreturn CALL `_body_has_return`
      faithfully. This IS the authorized "cert" campaign — a large multi-session build, not an inline win.

VERDICT: _check_noreturn stays trusted pending the (C) pyval→stmt_ir bridge cert. Reverted clean (829).
The precise blocker is now recorded for that cert campaign; the recognizer/emitter design (pyval-model
guard + pget_list body + the three helper calls) is ready to reuse once the bridge exists.

### campaign-C bridge SCALE (measured 2026-08-02)
The `list pyval -> stmt_list` bridge is a total RUNTIME WhyML parser `pyval -> stmt_ir` (+ `list pyval
-> stmt_list`): dispatch on each PDict's "stmt" tag, construct the matching stmt_ir ctor (~24: SPass..
SGhostAssign), recursively parse children — INCLUDING the emit_ir expression slots each compound ctor
carries (SWhile emit_ir stmt_list, SIf emit_ir stmt_list stmt_list, ...). So it drags in the full
emit_ir expression grammar parse too. Termination = pv_size structural recursion; the ADT cert
(Phase2d_StmtIR.v / StmtIR.lean) already exists (axiom-free). FEASIBLE but LARGE (multi-session):
this is the real shape of the authorized cert campaign. Unlocks _check_noreturn + reconciles the
9 stmt_ir/stmt_list consumers with the pyval world. NOT a heartbeat-tail inline win.

## BOUNDARY (2026-08-02): _check_class_invariants — set-ENUMERATION over the membership-only StrSet
Measure-first (IR dump + emitted-type check, NO build) on the next short target `_check_class_invariants`
(core_ir_semantic). Body: `for td in ir["type_decls"] if kind=="record": field_set=set(field_names);
for inv in class_invariants: for var in sorted(v for v in _ir_free_vars(inv) if v): if var not in
field_set: raise`. The inner loop ENUMERATES `_ir_free_vars(inv)`. But `_ir_free_vars` emits
`pyval -> map string bool` (the certified MEMBERSHIP-only StrSet). A `map string bool` is a TOTAL
FUNCTION — it has NO enumeration; you cannot `for var in` it. So the check (iterate the free-var set,
test each against field_set, raise) is UN-modelable on the current representation.

This is the SET-ENUMERATION boundary — SAME ROOT as `bases_closure` (worklist BFS needs to enumerate
an abstract map) and the SAME CLASS as `_check_noreturn` (representation mismatch). SYSTEMIC finding:
the `map string bool` StrSet model — which UNLOCKED many conversions (membership guards, set-collect
folds, R-W2d, union cluster) — CANNOT serve any stub that ENUMERATES a COMPUTED set. Fixing needs
`_ir_free_vars` (and siblings) to return an ENUMERABLE `list string` instead of `map string bool` —
a §10.4 verified-method RE-REPRESENTATION with corpus/proof risk, NOT an inline win. There is no
`map string bool -> list string` bridge (you cannot enumerate a total function). Record + skip.
Stays trusted at 828.

### CORRECTION (2026-08-02): _check_class_invariants is NOT a set-enumeration boundary — CONVERTED
The 1bd52a75 note above was WRONG. Measure-first found the CONVERTED sibling `_cs_clause` already
lowers `for v in _ir_free_vars(clause): if <membership guard>: raise` via the sound ARBITRARY-ELEMENT
device: call `_ir_free_vars` (VC discharges), bind `let v = __anystr ()`, apply the EXACT guard to
that arbitrary element -> conditional raise. Under `ensures True` + declared `raises`, this SOUNDLY
OVER-approximates the loop's raise behaviour (a `map string bool` has no element list, but you don't
NEED to enumerate — one arbitrary element with the real guard covers the raise). `_check_class_invariants`
is the SAME raise-consumer wrapped in type_decls/class_invariants list folds + a set_add field_set fold.
CONVERTED via recognize_check_class_invariants (828->827), whole-file proof [+] SUCCESS, byte-diff 0,
ledger 3. LESSON: "membership-only StrSet can't be enumerated" is TRUE but does NOT imply the CONSUMER
is a boundary — a for-loop-that-RAISES over a set lowers via the __anystr over-approximation, NOT
enumeration. The ~dozens of "enumeration-blocked" stubs must be RE-triaged: raise-consumers are
convertible (this device); only set-BUILDING enumerations (out.add per element) genuinely need an
enumerable representation.

## BOUNDARY MEASURED (2026-08-02): _check_noreturn bridge parser — pget_list-extraction variant TIMES OUT
Per cost≠floor (measure the scale boundary, don't assume it), I BUILT the pyval->stmt_ir structural
parser (`__ps`/`__psl`/`__phl`/`__ph`/`__pmcl`/`__pmc`) that maps "Return"->SReturn + compound tags
(If/While/For/Try/Match/CriticalSection) to their ctors with recursed stmt-sublists, everything else
->SPass, placeholder expressions (IrNum 0/IrSNone/IrONone). It TYPE-CHECKS (L3-tc ✓ — all ctor arities/
record fields/mutual types correct) and is a SOUND ABSTRACTION for _body_has_return (which ignores
expressions). But `--fun _check_noreturn` MEASURED 24 Timeouts, ALL on `_check_noreturn__ps'vc` VARIANT
DECREASE: Why3 cannot prove `size_list (pget_list "body" d) < pv_size (PDict d)` — the pget_list
RECURSIVE extraction breaks the size-member chain (boolfold's __v/__d recurse on DIRECT DCons members
so the member-size lemma applies structurally; the parser extracts a SPECIFIC key's list via pget_dyn,
whose result-size has no lemma). CONFIRMED BOUNDARY (measured, not assumed).
FIX: add `lemma pget_size: forall k d. size_list (pget_list k d) <= size_dict d` (provable axiom-free by
recursion over d) to the SHARED preamble size theory — a §10c-wide + whole-file-reproof modular-theory
change = REVIEW-GATED (§10.10). This is the concrete, minimal unblock for _check_noreturn + the whole
stmt_ir/pyval bridge. NO new axiom needed (the lemma is provable); ledger stays 3. Reverted clean (821->822).

## CORRECTION (2026-08-03): _check_noreturn bridge is NOT review-gated — pget postconditions (corpus-inert)
The ac341964 "review-gated / corpus sanctioned-reset" claim was WRONG on the decisive dimension.
MEASURED: 60/60 corpus programs emit NO pget_dyn/size_dict (the pydict theory is mirror-only) — so a
`pget` size fact is BYTE-DIFF-0 by construction (corpus-inert). The real fix is not a standalone lemma
(pget_dyn/pget_list are program `let`s, unusable in a logic lemma) but POSTCONDITIONS on them:
  pget_dyn : ensures { match result with Some v -> pv_size v <= size_dict d | None -> true }
  pget_list: ensures { size_list result <= size_dict d }
Both provable axiom-free (structural recursion + the existing size_dict_nonneg lemma), SAFELY ADDITIVE
(stronger contracts can't break the ~40 caller proofs, only help), ledger 3. Emission order OK (pget_*
emit AFTER pv_size/size_dict in _emit_pydict_theory). This is a NORMAL shared-emitter change (§10c
re-typecheck + mirror re-proofs + byte-diff 0), autonomously attemptable — NOT coupling-rule/corpus
review-gated. ATTEMPTING per cost≠floor (measure the fix, don't assume). Open risk remains ONLY the
E-matching: does the parser variant DISCHARGE using pget_list's ensures (measure via --fun).

## 2026-08-03 — typing-check leaf family: warn-observable = vacuous-by-design (STAY trusted)
The core_ir_semantic typing checks (_typeddict_check_subscript, _namedtuple_check_subscript,
_check_typeddict_access, _check_union_narrowing) are OBSERVATIONALLY VACUOUS to convert: their only
effect is `warnings.warn`, which the emitter lowers as effect-free (opaque unit). Per the generic_fold.py
walk+leaf convention (note ~line 6786: "leaf ... observable is a warnings.warn (effect-free) ... STAYS
trusted") + §10.7 (VALUE not count), converting a warn-only leaf proves the same trivial `ensures True`
a `val` already gives — a count-only win that Gate C non-vacuity must reject. DO NOT convert warn-leaves.
NON-VACUOUS subset = the RAISING checks (_namedtuple_check_call raises PyCSLSemanticError on wrong arity;
_check_namedtuple_access reaches it via _namedtuple_walk_construction). Those ARE convertible (raise is a
real observable, cf. the __anystr raise-consumer non-vacuity) BUT need a tuple-from-dict-value model
(`nt_arities[callee]` → (nfields, field_names, defaulted) unpack + `len(defaulted)`/`len(args)` +
arity-range raise) — a genuine value-model feature-build, not a cheap win.
LESSON: before converting a check-leaf, ask "does it RAISE, or only warn?" — warn-only = vacuous boundary.

### _namedtuple_check_call — INT-MODEL caller-coupling (measured from mlw, definitive)
The current trusted val is `(call: map int (option int)) (nt_arities: map int (option int))` — the OLD
int-model. Its VERIFIED caller _namedtuple_walk_construction is also int-model-typed and calls it as
`_namedtuple_check_call (any map int (option int)) nt_arities fname` (passes `any` for the call node — the
int-model can't represent it). A faithful pyval/pydict conversion of the leaf would CASCADE: re-model the
whole namedtuple chain (walk_construction + _check_namedtuple_access) int→pyval simultaneously, re-porting +
re-proving each VERIFIED function (§10.4). Coupled multi-function campaign, NOT an autonomous cheap win —
the ebf9dfcb caller-coupling trap at chain scale. LESSON: before building a leaf, `grep` the current
trusted-val SIGNATURE in the .mlw — an int-model val with a verified int-model caller = coupling boundary.

## 2026-08-03 — clean-simple fast-file frontier DRAINED (6 conversions this session)
Session landed 6 conversions (820→814): find_assigned_vars (ir_scanner, ref-accumulator set-collect),
_test_contains_map (auto_trust, recursive bool-fold + opaque cross-mixin pyval-predicate), _is_linear_vc
(auto_trust, all()-AND-fold, all distributes over ++ so no list-append), handler_catches (exception_model,
h==r||opaque-in-closure, INT return to match verified caller), subclasses_of (exception_model, set-filter-
fold over handler_catches), classify (import_classifier, split-first + StrSet-membership + 3 opaque const
returns named by identifier). Banked recognizer devices: opaque input-dependent pyval/string predicate;
short-circuit bool-fold; set-filter-fold; StrSet membership = map application; reflect-the-literal separator;
return-type MATCH for verified callers (bool→int); const-return-as-named-opaque-val (non-facade).

REMAINING FRONTIER (measured): clean-simple targets EXHAUSTED. Next tier = MEDIUM string-op-heavy funcs,
buildable like classify but heavier (several opaque string vals each): ir_inline._global_call_target
(partition + StrSet + map-string-string lookup + opaque _method_key), ir_inline._method_edges (_walk_dicts
set-collect + startswith + _method_key), monomorphize._type_str/_match_generic_annotation (regex/sanitize +
tuple), _global_call_target family. BOUNDARY classes (need a FEATURE, not a recognizer): self-state record
readers (_field_type_for/slot_id/as_dict/arity/all_agree/ok — need field-projection model), module-const
readers (bases_closure/predicate_definitions/_strip_const_name — need const-splice), raw-ast (pure_ast
parser ~150 methods, Weaver/Ingestor visitors), I/O (_stub_set), stateful-mutation (_inject_functions),
pure-string-regex-transform (_mangled_name/_expand_anon_binders — one opaque val = facade, need real string
theory = the no-more-int campaign). _has_dynamic_exec (functions.py) is clean but the file's proof is slow.

## 2026-08-03 — ir_inline global-call vein: 2 conversions (814→812) + _recursive_methods BFS boundary
Landed `_global_call_target` (7b27a71c, 814→813) and `_method_edges` (0d8b1ee6, 813→812) in
ir_inline.py (fast file: emit 0.8s, proof grew 61s→~2.5-9min with the pyval theory — still SUCCESS).
Both are bespoke recognizers in generic_fold.py modeled on `classify` + R-W2d `_assigned_locals`.
NEW banked devices (reusable for the medium string-op tier):
- **pyval single-node field read** = TYPED-irkey `option string`/`option pyval` readers
  (`_emit_skey_reader`/`_emit_pval_reader`): `call.get("type")`/`.get("func")`/`.get("body")` are
  K_type/K_func/K_body TYPED keys — a K_dyn getk SILENTLY skips them (ref_accumulator lesson #1), so
  match the constructor directly; the helper falls back to the K_dyn guard form for a genuinely-dynamic
  key (mutation-safe either way).
- **partition → two opaque before/after projections** `(string,sep)->string` reflecting the sep;
  **`x in <str>` → a PRIVATE opaque containment val** (str_contains_op is NOT in every file's preamble —
  a self-contained `val __has` keeps the file byte-inert, no shared-string-theory gate touched).
- **`Dict[str,str]` param → `map string string`** total lookup (`g_class recv : string`); **`Set[str]`
  → `map string bool`** membership; **`Optional[str]` return** = the union `Arm_<idx>_0 s`/`Arm_<idx>_None`
  where idx = `union_name.rsplit("_",1)[-1]`.
- **computed-element set fold**: `_method_edges` folds `_walk_dicts (func.body)` (`list pyval`,
  size_list variant — STRUCTURAL, discharges) with a computed `cand: option string` (3-way self./
  dotted/bare) and a `names`-membership-gated `set_add`. `cand=None` on the dotted-not-a-global branch
  → `option string` None arm → not added (faithful).
BOUNDARY — `_recursive_methods` = worklist-BFS over the abstract `edges: map string (set string)`
(`stack.pop()/seen.add/stack.extend(edges.get(n))`): SAME class as `bases_closure` — no dischargeable
variant without a bounded-universe AXIOM (ledger-3 violation). Stays trusted. (The _method_edges fold is
NOT this boundary — it's a bounded structural `_walk_dicts` descent.)

## 2026-08-03 (worker cont.#4) — fast-file cheap frontier RE-SWEPT at 810: exhausted; find_self_method_calls BOUNDARY
Full re-survey of the FAST/small mirror files (ir_inline, monomorphize, import_classifier, exception_model,
auto_trust, scc, struct_format, types, functions, ConcurrencyChecker, module_collect, exec_splice,
abstract_ops, expr_ghost_spec_ops) found NO clean single-build cheap win — every remaining stub sits in a
MEASURED boundary class: nested-def-dropped-closure (functions._returns_string_seq, auto_trust family),
self-state map read (types._field_type_*, _infer_tuple_slot_type, _param_type_str), string-construction
(monomorphize._mangled_name/_rewrite_annotation_str, functions._callable_whyml_arrow), regex-whole-body
(monomorphize._match_generic_annotation, struct_format.parse_format/calcsize), graph/BFS
(scc.compute_sccs/sort_functions_by_scc, exception_model.bases_closure, ir_inline._recursive_methods),
module-const reader (exception_model.predicate_definitions/all_phase1_exceptions), raw-ast/IO
(import_classifier.collect_imports/check_imports, module_collect.*, ConcurrencyChecker.*, exec_splice.*),
giants (ir_inline._Inliner.*, monomorphize._specialize_*, expr_ghost_spec_ops emitters), heterogeneous
Dict[str,Any] value-model builders (functions._build_method_*_map).

### SPIKED + REFUTED: scc.find_self_method_calls (recursive Set[str] pyval walker + string construction)
Its sibling `find_calls_in_ir` (same file) converts cleanly via the generic pyval set-union walk recognizer
(emits `PDict`/`PList` catamorphism + `__pre` with `set_add`, `Map.get func_names_set m`). find_self_method_calls
LOOKS identical in shape but adds (a) early-return guard `if not self_type or not concrete_set`, (b)
string construction of the collected element `prefix = self_type.lower()+"__"; resolved = prefix + f[len("self."):]`,
(c) `isinstance(f,str)` + `f.startswith("self.")`. Ported verbatim (faithful Set[str] retype) + emitted
`--no-proof --keep-mlw`: the set-walk recognizer does NOT fire — the body drops into the GENERIC imperative
int-lowering, a total int-hash-erasure FACADE (`obj: int`; `typeof_op 315`, `obj_get_1 1138418396`,
`(obj_get_1 1342639453)=502964910`, `f_startswith_1 1143254347` — all applied to HASH CONSTANTS not to obj/f;
`func_names_set: map int (option int)` int-keyed) that additionally FAILS L3-tc (`scc.mlw:261` type error).
Reverted clean (git checkout single path + rm scc.mlw); count/fidelity restored (mirror-check 52/52).
BOUNDARY = the generic pyval set-union walk recognizer accepts only element-forwarding `__pre` bodies (add an
EXISTING PStr value); it has no path for a CONSTRUCTED-string element (`.lower()`/concat/slice) nor an
early-return guard nor `startswith`. Reopen = extend that recognizer (generic_fold.py) with faithful,
mutation-sensitive string-op construction in the `__pre` + guard/startswith support — a Phase-2 recognizer
build (facade-risk, needs the report->review->impl cycle), NOT a worker cheap win.

## 2026-08-03 — OPERATIONAL: whole-file proof of BIG importer files can hang on a vacuity-diagnostic goal
On statements.py/functions.py-scale whole-file proofs, the pycsl vacuity pass (separate `why3 prove … /tmp/.pycsl_vac_*.mlw` invocations AFTER the main goals) can leave ONE `why3`/Z3 worker running for minutes despite its own `--timelimit 5` (the solver ignores the wall-clock limit on a pathological goal). Symptom: output stalls at "Warnings/Errors from Why3:" with the main goals all Valid, one live `why3 prove …vac…` worker. FIX: `kill -9` that single hung worker — pycsl then prints the main verdict ("[+] Verification SUCCESS! All contracts formally proven.", the vacuity goal is best-effort/non-blocking). Confirm 0 non-Valid in the MAIN results (`grep 'Prover result is: Valid'` count vs Timeout/Unknown/Invalid=0). Non-vacuity is independently assured by the recognizer mutation-test (perturb each source literal → .mlw moves).

## 2026-08-03 — OPERATIONAL: workers must NEVER run byte-diff-sweep / touch corpus fixtures
Two autonomous workers ran `bin/byte-diff-sweep.sh` (or a variant) despite instructions, spawning 812-file corpus-emit swarms that orphan on worker-end AND — once — DELETING 46 committed corpus fixtures (test-suite/corpus/pycsl-reference/*.proofs/*.mlw + the 0893–0924 no-.py hand-written `.mlw` reference fixtures). Supervisor restored them by explicit-path `git checkout HEAD -- <paths>`. RESOLUTION: the SUPERVISOR owns byte-diff 100% (batch, after each worker) — worker prompts must state ZERO byte-diff (no sweep, no worktree, no corpus touch, not even a "light" check). Workers may build + typecheck + fidelity + mutation-test + whole-file proof only; they touch ONLY src/self-annotate + src/pycsl/module6_whyml. `bin/byte-diff-sweep.sh` itself is SAFE (only rm's `corpus/<name>.mlw` for existing <name>.py; the no-.py fixtures are untouched) — the deletions came from a worker's non-standard rm/git command, not the script.

## 2026-08-03 — Phase-2 WALL: module-const LIST/SET/type-dict membership+iteration is a FRONT-END-COLLECTOR gap (module6-only cannot reach it)
Worker #11 measured the next ranked capability ("module/class-const LIST/DICT membership+iteration splice") against its 3 named targets + a full census of the 44 small (≤4-stmt) const-referencing `\trusted` stubs. VERDICT: the capability is NOT tractable in module6 alone; all consumers read constant SHAPES the front-end ERASES. This is a Module5/front-end (`frontend/module_collect.py` + `Module5_IREmitter.py`) gap — OUT of the worker's allowed dirs (src/self-annotate + src/pycsl/module6_whyml) and high-risk/review-gated — so recorded as a Phase-2 wall, NOT attempted.

### The measured captured-vs-erased boundary (the root)
Front-end const collectors that DO reach module6 as IR fields: module str→str dict (`collect_module_const_dicts`→`_module_const_dicts`), module str→int dict, module compound dict, module int/str SCALAR (`collect_module_constants`→`_module_constants`), class-body INT const (`_collect_class_constants`), and class-body STR-SET (`_collect_class_str_set_constants`→`str_set_constants` on the type_decl). ERASED — captured by NO collector, absent from the IR (verified by running each collector on the target files: all return `{}` for these names):
- **module-level str-SET / frozenset** (`KNOWN_EXCEPTIONS=frozenset({...})`, `_ARITH_ADD_OPS={"+","-"}`, `_COMPARISON_OPS`, `_LOGICAL_*_OPS`, `_HEADER_CONSUMERS`, `_BLOCK_HDRS`) — there is a CLASS-body str-set collector but NO module-level one.
- **module-level list-of-str-pairs** (`_PREFIX_STRIPS: List[Tuple[str,str]]`, `_LIBRARY_PREFIX_STRIPS`).
- **type-keyed dict** (`_PY_OP_MAP: Dict[type,str]` — keys are `ast.Add`/`ast.Sub`… objects, read via `.get(type(op),"?")`).
Because module6 recognizers key off the collector-populated IR fields and there is no field for these, module6 has NO access path to the literals — a module6-only recognizer literally cannot see them.

### The 3 named targets, each classified
1. **`from_lean_json._strip_const_name`** (`for src,dst in _PREFIX_STRIPS: if name==src: return dst; return name`) — const `_PREFIX_STRIPS` is module list-of-str-pairs → ERASED. Needs a new front-end collector `collect_module_const_str_pairs` (module→List[(str,str)]) + a module6 linear-ITE lowering (`if name="Nat.gcd" then "gcd" else … else name`, mutation-sensitive). The module6 half is trivial; the FRONT-END half is the gate. WALL.
2. **`Module5_IREmitter._py_op_to_str`** (`return self._PY_OP_MAP.get(type(op),"?")`) — const `_PY_OP_MAP` is `Dict[type,str]` → ERASED, AND the access needs `type(op)` node-kind reflection to a discriminant. Needs a type-keyed-dict collector + reflection. WALL (heavier than #1).
3. **`ir_scanner._collect_mutations`** — const `_MUTATING_METHODS` (class str-SET) IS captured (verified: all 10 members in `str_set_constants` for IRScanner). But the const is a tiny fraction of the body: the function is a heterogeneous recursive tree-walker over untyped IR stmt dicts (`func.rsplit(".",1)`, `"." in func`, `.get("stmt")`/`.get("value")`/`.get("array")` chains, out-param `out.append`, recursion into body/orelse/finalbody + Match cases). It is the Dict[str,Any] value-model / nested tree-walker RESEARCH wall documented across this ledger, independent of const capture. WALL.

### Census result (why there is no module6-only cheap win here)
44 small const-referencing `\trusted` stubs. Every tractable-looking one is blocked by exactly one of: (a) the ERASED module-compound-const gap above (str-sets / list-pairs / type-dicts — the majority); (b) the stateful token-cursor parser wall (`proof2why3/parser.parse_*`, `frontend/pure_ast.*` — @mutable_state recursion + node construction, even where a membership set is involved); or (c) the heterogeneous-dict recursive tree-walker wall. The seemingly-cheapest, `exception_model.all_phase1_exceptions` (`return sorted(KNOWN_EXCEPTIONS)`), is doubly blocked: `KNOWN_EXCEPTIONS` is an erased module frozenset AND `sorted()` needs a sorted-literal-seq lowering.

### Reopening capability (the ONE unlock — a supervisor/review-gated Phase-2 build)
Add a FRONT-END collector family for module-level COMPOUND constants — `collect_module_const_str_sets` (frozenset/set of str-lits → `str_set_constants`-style field), `collect_module_const_str_pairs` (List[(str,str)]), and (harder) a type-keyed op-map — wired in `Module5_IREmitter.py`, THEN the module6 lowerings (membership `x in SET`→`str_eq_op` disjunction like the class-str-set path already does; list-pair→linear-ITE; `sorted(SET)`→sorted-literal `Seq.cons`; type-dict→node-kind reflect+ITE). This mirrors exactly how the class-str-set capability (L4b) and the const-str-dict capability (84a5cc85) work, but for module-level compound shapes. It is corpus-inert by construction (no reference program reads a module compound const this way) but it EDITS THE FRONT-END, so it is out of worker scope: escalate as a report→fable-review→impl Phase-2 cycle. Once landed, target #1 converts immediately and the parser/tree-walker targets remain separately walled.

## 2026-08-03 (driver cont#14) — NESTED-def / dropped-closure wall = RESEARCH WALL (spike REFUTED at Q2)

MEASURE-FIRST feasibility spike on the highest-multiplicity Phase-2 wall (nested `def` closures Module5
drops; ~21 stubs per run #5 census — `core_ir_semantic` collectors + `auto_trust._is_linear_expr`/
`_has_set_op_on_map`/`_should_auto_trust_tuple_return`). Verdict: **RESEARCH WALL** — the front-end capture
is cheap and byte-inert, but it is the WRONG HALF; lowering the captured body sits on two pre-existing
CERTIFIED-BOUNDARY research floors. NO source touched; tree clean (only a scratchpad census script written).

**Q1 (byte-inertness) — PASSES.** AST census over the 893-file corpus (`scratchpad/nested_census.py`,
parent-scope-tracking walk): **ZERO** TRUE nested-function closures (a `def` whose nearest enclosing scope is
a `FunctionDef`). The coarse grep `^\s+def ` hits 152 files, but ALL are class METHODS (`def` under `class`),
which Module5 already captures normally — NOT the dropped-closure case. So an additive nested-def capture into
a NEW IR field is byte-inert BY CONSTRUCTION (no corpus program's IR changes). This half is feasible.

**Q2 (reconstructability without a facade) — REFUTES.** Target `auto_trust._is_linear_expr` (nested
`def _check(e)`, a recursive type-dispatched linear-arith predicate over the contract-expr IR dict). Even a
PERFECT capture of the closure into an IR field cannot lower faithfully without BOTH of two documented
research floors — each independently sufficient to refute:
  1. **Recursion + structural variant.** `_check(left) and _check(right)` needs `let rec` PROGRAM-function
     emission with a discharging structural variant. The emit_ir theory has a `size` logic function
     (preamble.py:4708) but — per the isinstance CERTIFIED-BOUNDARY (this ledger, line ~328) — "there is no
     path to emit it as a program-function variant." The existing `let rec` machinery (functions.py) serves
     RECOGNIZER-matched mutually-recursive method groups with hand-authored variants baked into each
     recognizer; there is no path to synthesize a variant for a freshly-captured arbitrary closure.
  2. **Heterogeneous pyval value model.** The constant branch `val = e.get("value", e.get("n",0)); return
     isinstance(val,(int,float,bool))` distinguishes numeric from string/other at RUNTIME. `num_of` (the
     Number-value projector, preamble.py:4855) returns `int`, so `isinstance(val,(int,float,bool))` collapses
     to always-True over it — a FACADE (the float/string rejection vanishes, mutation-insensitive). Faithful
     lowering requires the heterogeneous `Dict[str,Any]`/`pyval` value model — the repeatedly-recorded
     research-grade floor (this ledger, "giants emit-ir substrate = CERTIFIED-BOUNDARY").
  Without both, the only lowering is the banned facade (`_check` vanishes → constant `let found=…; found[0]`,
  exactly the run #5 §A facade shape). Corroboration from the base loop itself: `generic_fold.py:12985`
  already tags `_is_linear_expr` "(trusted: nested-closure boundary) ... opaque pyval->bool over-approximation"
  and lowered its ONLY consumer `_is_linear_vc` by treating it as an opaque call, never its body.

**Q3 (cost) — multi-session RESEARCH, not a worker build.** The nested-def capture alone converts ZERO stubs
(non-vacuity forbids committing front-end infra with no consumer conversion), so it is not even a committable
increment until the two floors above land. It is COST/SCALE-AND-CORRECTNESS blocked: the two floors are
CORRECTNESS boundaries (facade-or-nothing without them), and building them is session-scale research.

**Reopening capability.** The nested-def front-end capture is real, cheap, and byte-inert — bank it as the
FIRST step of a Phase-2 cycle, but ONLY co-landed with (1) captured-closure `let rec`+auto-variant program
emission over the IR ADT AND (2) the heterogeneous pyval value model. All three must land together (the
fixture-witness co-land pattern) or the capture is dead infra. Do NOT re-run the Q1 census (answer: 0) and do
NOT attempt `_is_linear_expr` as a worker build — it is a facade until both floors exist. The `core_ir_semantic`
`.values()` collectors behind this same wall share floor (2) and additionally the untyped-dict `.values()`
iterator model. This is the same single highest-leverage root this ledger names throughout: the emit_ir-typed
sub-node / heterogeneous `Dict[str,Any]` value model + certified recursive fold.

## 2026-08-03 (worker #15) — value-model "smallest-bounded-gap" census: NO bounded projector-over-existing-leaves remains

MANDATE: MEASURE-FIRST for the SMALLEST byte-inert, axiom-free, ledger-3 value-model extension that unblocks ≥1
trusted stub — a definitional `let function` over EXISTING certified ADT leaves (the `num_of` / `is_constant` /
`is_num_or_float` shape, fixture 0924), NOT a new ADT/cert. Census over the tractable (non-parser, non-giant)
files, live bodies read. VERDICT: **no such gap exists.** The last definitional-projector-over-existing-leaves
additions (`num_of`/`is_constant`/`is_num_or_float`) were already built and their sole consumers (`_is_null_byte_lit`)
converted. Every remaining value-model-blocked stub needs a NEW value shape / new-ADT+cert, self-state modeling,
class-constant-splice, or string char-parsing. Per-stub measured blocker (each a distinct root, none a projector add):

| stub (file) | exact gap | class |
|---|---|---|
| `_namedtuple_check_call` (core_ir_semantic) | `nt_arities: Dict[str,Tuple[int,list,list]]` param + `n,f,d = nt_arities[k]` unpack + `len(list)` COUNT (size_list is a size-MEASURE not a count) | NEW tuple-valued-dict shape + pyval-list length fn; >70min whole-file proof. new-shape+COST |
| `_collect_tuple_var_assigns`, `_collect_array_var_assigns`, `_call_return_whyml_type` (types.py) | read `self._module_method_return_types` self-state map + `fn.rpartition(".")` string ops | SELF-STATE map boundary (not pyval) |
| `_track_collection_metadata` (types.py) | writes 4 self-state maps (`_known_collection_elements/_sizes`, `_record_array_locals`) + dict-comprehension `elem_map` + `str(int(...))`/`repr(float)` construction | self-state + string-construction |
| `_collect_mutations` (ir_scanner) | `method in IRScanner._MUTATING_METHODS` (10-elem Set[str] CLASS CONSTANT, invisible to a fn-level recognizer) | class-constant-splice feature |
| `find_array_and_dict_vars` (ir_scanner) | huge value-classification elif + `Tuple[Set,Set]` return | multi-piece |
| `_module_const_int` (module_collect) | `value: Any` param (int-erases) reflecting RAW `ast.Constant`/`ast.UnaryOp(USub)` — the emit_ir const model (is_constant/num_of) is over emit_ir LEAVES, there is NO raw-ast const-node model; needs `Any`→`ast.expr` live-source annotation + a raw-ast Constant/UnaryOp node-reflection ADT (`is_ast_const`/`ast_int_of`/`is_usub`/`operand_of`) | NEW raw-ast node-reflection ADT (L1-scale, tparam Phase2h precedent) + co-landing cert |
| `parse_format`/`calcsize`/`slot_id` (struct_format) | char-by-char format-string cursor parse + native-size dict | string char-parsing |
| auto_trust remaining 7 | nested-def dropped-closure / str+eval (per ref_accumulator memory) | closure / eval |

**Smallest of the new-shape builds = `_module_const_int` raw-ast const-node reflection** (L1-scale ADT, one node
family: Constant + UnaryOp/USub, plus the faithful `Any`→`ast.expr` source annotation). It is UNBOUNDED per the
worker mandate (new ADT + co-landing formal-semantics cert), so recorded here as the reopening capability rather
than built by a limited-context worker (orphan-avoidance: a session-scale ADT+cert+proof must run in a fresh window,
never as a context tail). REOPENING CAPABILITY (fundable per COST/SCALE≠floor): raw-ast Constant/UnaryOp node
reflection ADT + axiom-free `Phase2*` cert, then converge on `_module_const_int` (+ sibling `Module5._const_int_value`).
NOTE the worker#14 `num_of`-collapse claim did not reproduce: `is_num_or_float` (IrNum/IrNumF) and `is_num` (IrNum,
excludes IrBoolC) already distinguish numeric-vs-string-vs-bool faithfully over emit_ir; the numeric `isinstance`
tests that remain blocked (types.py:96-114) are gated by SELF-STATE writes, not by a value-model projector gap.

---

## `ir_scanner._collect_mutations` — CERTIFIED-BOUNDARY (whole-file proof-SCALE, NOT correctness) — worker#17, 2026-08-03

**Verdict:** the conversion is fully BUILT and FEASIBLE (typechecks, non-facade, mutation-sensitive,
proves in TRUE isolation, needs NO new ADT / cert / axiom, ledger stays 3, count 804→803) but the
whole-file pycsl proof FAILS on a *sibling* — it is the whole-file E-matching SCALE wall predicted by
[[isolation_spike_not_whole_file]]. Reverted to clean (HEAD ec17e1c5).

**What was built (banked design, reconstructable):**
- **Front-end additive collector** (`Module5_IREmitter.visit_ClassDef`): a FIELDLESS/BASELESS class
  (a namespace of `@staticmethod`s like `IRScanner`) emits NO `type_decl` (`if fields or bases:` gate),
  so its class-body str-set const `_MUTATING_METHODS = {...}` is LOST. Capture it into a new module-level
  IR field `class_str_set_constants[ClassName] = {CONST: [members]}` in the `else` branch — additive,
  read ONLY by the new recognizer → byte-inert corpus-wide. (`_collect_class_str_set_constants` already
  exists; the gate is the blocker.)
- **Recognizer** `recognize_collect_mutations(func, class_str_sets)` (generic_fold.py): structural match of
  the 3-arg void walker; requires `out` in the `#@ assigns` frame (frame-fidelity, like recognize_generic_fold
  — so the mirror contract changes `assigns \nothing`→`assigns out`, matching `find_named_expr_targets`);
  extracts tags/keys/`Var`/`Call`/rsplit-sep positionally + members from `class_str_sets["IRScanner"]["_MUTATING_METHODS"]`.
- **Emitter** `emit_collect_mutations_group`: a `ref (list pyval)` ref-accumulator that `Cons`es WHOLE
  matching pyval stmt nodes (the ONE new element-shape vs the `find_assigned_vars` `map string bool`
  accumulator — reuses `Cons`/`PList`, no new value model). Membership `method in _MUTATING_METHODS` →
  `pystr_eq` disjunction over the resolved members; `func.rsplit(sep,1)`/`sep in func` → per-fn opaque
  `val`s reflecting the sep (banked reflect-the-literal). All non-facade (0 int-hash markers, real pydict
  readers), mutation-sensitive (perturbing a member / the sep / a tag moves the .mlw).

**The wall (measured, decisive):**
- `find_assigned_vars`' `_list_reader` size-postcondition goals (`Lbody`/`Lorelse`,
  `ensures { size_list result <= size_dict d }`) are at the RAZOR'S EDGE at HEAD: `why3 prove -a split_vc
  -P alt-ergo/z3 -t 30` on the HEAD-equivalent `.mlw` TIMES OUT both provers in ISOLATION, yet TRUE-HEAD
  `pycsl` = **SUCCESS** — because pycsl's `_dispatch_provers` proves residual goals PER-GOAL
  (`-g <file>:<line>`, best-of-N alt-ergo→z3), which barely clears them.
- Adding ANY pydict-recursive function to the module (measured: even the readers+helpers alone, `cm_nowalk`)
  tips BOTH provers on those two goals from 851 steps / 0.16 s to a 30 s / ~28M-step timeout — a ~33 000×
  regression. `pycsl` then reports exactly `2 goal(s) remain unproven` = `find_assigned_vars__Lbody/Lorelse`.
- Tried, did NOT clear it under pycsl split_vc: (a) size-postcond list-readers → +4 own timeouts (6 total);
  (b) generic void-descent with `variant { pv_size v }` size-FUNCTION variants → still 2 (the size-fn
  variant injects `pv_size (PDict d)=1+size_dict d` triggers globally); (c) **structural** variants
  `variant { v }/{ d }/{ xs }` (fixes plain-`why3`, 0 timeouts there!) → still 2 under pycsl split_vc;
  (d) footprint cut 16→11 symbols (one `__irk_eq`+`__get` vs 7 opt-readers) → still 2; (e) an explicit
  `assert { size_list xs <= size_dict d }` HINT inside `find_assigned_vars`' own `_list_reader` → still 2.

**Classification:** COST/SCALE, not CORRECTNESS (the build proves in true isolation; no ADT/cert/axiom).
Per COST/SCALE≠floor it is NOT a terminal floor. **Reopening capability:** review-gated MODULAR
verification (§10.10) — a `#@ no_inline`-style modular boundary that proves `find_assigned_vars`' readers
(and/or the new walker) in a SEPARATE proof context so the shared-module E-matching stops summing; OR a
robustification of the `find_assigned_vars` size-postcond readers that survives an enlarged module.
**Ops lesson (cost real iterations):** an isolated `why3 prove` is NOT representative — pycsl proves
residual goals PER-GOAL best-of-N; always validate whole-file provability with `pycsl` itself, and note a
goal that is fast under plain `why3` (no `-a split_vc`) can still time out under pycsl's `split_vc`.

---

## `ir_scanner._collect_mutations` — `#@ no_inline` REFUTED (worker#18, 2026-08-03) — CERTIFIED-BOUNDARY stands

**Task:** apply the `#@ no_inline` modular-verification reopening worker#17 named for the `_collect_mutations`
whole-file E-matching SCALE wall (adding a pydict-recursive walker tips `find_assigned_vars`' `__Lbody`/`__Lorelse`
size-postcond readers, `ensures { size_list result <= size_dict d }`, from 0.16s → 30s timeout under pycsl split_vc).

**Verdict: `#@ no_inline` CANNOT clear this wall — spike REFUTED before any rebuild (Gate S / measure-before-build).**
The `_collect_mutations` conversion is NOT rebuilt (it would produce WhyML byte-identical to worker#17's, which already
FAILS). Count stays 804, HEAD 69d4b6e6, tree clean, ledger 3.

**Decisive falsifier (cheap, empirical — no rebuild):** applied `#@ no_inline` to `find_assigned_vars` in the mirror
at HEAD and re-emitted; the WhyML is **BYTE-IDENTICAL** to HEAD (`diff` empty). `#@ no_inline` is a **no-op on emission**
here. Root causes, all structural:
1. **`#@ no_inline` is a Python-method call-site *splicing* directive** (`ir_inline.py` `_Inliner`): it changes whether a
   caller gets the callee's Python body spliced in vs a contract-`val`. It NEVER removes a function's definition from the
   emitted Why3 module.
2. **The E-matching pollution is module-level *definition presence*, not call-site splicing** (worker#17's measurement;
   independently the expr-grammar progress-log lesson: "#@ no_inline does NOT help = module-level presence not call-site").
   `find_assigned_vars`' size-postcond readers time out because the module gains another recursive walker's reader
   definitions/triggers — which `no_inline` leaves fully in place.
3. **Every method in `ir_scanner` is a *recursive* walker** → `ir_inline.py` already refuses to inline recursive methods →
   `no_inline` is *universally inert* for this file (byte-identical emission confirmed). The polluting walker
   `_collect_mutations` is itself recursive, so `no_inline` on it is likewise a no-op.
4. **The size-postcond readers `__Lbody`/`__Lorelse` are recognizer-emitted WhyML helpers, NOT Python methods**
   (confirmed: absent from the mirror source). The task's literal instruction — "mark the `_list_reader`-emitted
   `Lbody`/`Lorelse` as `#@ no_inline` modular boundaries" — has **no applicable source site**; those readers have no
   Python form to annotate, and the recognized-fold lowering path does not consult `#@ no_inline` at all.

**Corrected reopening capability:** NOT `#@ no_inline`. The §10.10 mechanism that creates a **separate proof context**
(what worker#17's note actually described) is **`#@ verify_module <name>`** — emit `find_assigned_vars` (and/or the new
`_collect_mutations` walker) into its OWN top-level Why3 `module`, re-declaring the shared infra, so their recursive reader
definitions are NOT co-resident and the shared-module E-matching stops summing. That is a deliberate, review-gated build
(cross-module `self.<m>` calls lower to proven-interface `val`s via the Track-B narrowing VC), NOT a worker-scope
annotation. Alternative reopening: robustify the `find_assigned_vars` size-postcond readers to survive an enlarged module
(worker#17 tries a–e failed at this). CLASSIFICATION unchanged: COST/SCALE (fundable), not CORRECTNESS — no ADT/cert/axiom.

**Ops lesson (carry-forward):** `#@ no_inline` addresses *per-caller body-splice blowup* (the os `sys_write` case); it is
the WRONG tool for a *co-resident-recursive-definition E-matching* blowup. Distinguish the two before proposing it:
splice-blowup ⇒ `#@ no_inline`; module-presence-blowup ⇒ `#@ verify_module` (separate module) or reader robustification.

---

## `ir_scanner._collect_mutations` — `#@ verify_module` REFUTED **within scope** (worker#20, 2026-08-03) — CERTIFIED-BOUNDARY stands, reopening NOW PRECISE

**Task:** rebuild worker#17's PROVEN `_collect_mutations` recognizer AND use the `#@ verify_module <grp>` grouping
(the reopening worker#18 named) to isolate `find_assigned_vars`' razor-edge `__Lbody`/`__Lorelse` size-postcond
readers so the whole-file ir_scanner proof survives the added pydict walker.

**Verdict: `#@ verify_module` CANNOT be applied to a RECOGNIZER-EMITTED function within this worker's additive
scope — spike REFUTED before the `_collect_mutations` rebuild (Gate S / measure-before-build).** Count stays 804,
HEAD b7c31eb4, tree clean, ledger 3. NO rebuild spent (the decisive falsifier is cheaper than the build).

**Decisive falsifier (cheap, empirical):** tagged `find_assigned_vars` (already-converted, recognizer-emitted) with
`#@ verify_module VarsMod` in the mirror and emitted (`pycsl … --no-proof --keep-mlw`). **L3-tc FAILS** at
`ir_scanner.mlw:333`: `unbound program function or variable symbol 'irscanner__find_assigned_vars'` +
`cloned theory VarsModSig does not contain any abstract symbol`. **Reproduced across groupings:** a second
experiment putting BOTH `find_assigned_vars` and `find_named_expr_targets` in one group (`#@ verify_module FAVMod`
on both) fails IDENTICALLY — `FAVModSig` declares the two helper first-lets (`…__gstmt`,
`…__get_K_type`) and the clone substitutes the two public symbols the Sig never declared. Grouping is irrelevant;
the blocker is per-function Sig extraction.

**Root cause (READ, decisive — a NEW blocker #17/#18 never reached; they named verify_module as the *untested*
reopening):** the modular emitter `_transpile_modular` builds each `<G>Sig` interface via
`_sig_val_from_let(let_block)` (Module6_WhyMLTranspiler.py:1044), which converts the **first** `let`/`let rec` it
sees to the interface `val` and **breaks at that let's body `=`**. This assumes a *single-body* method (correct for
os `_dir_lookup`/`ReadMod`/`FindSlotMod`/`FindFreeMod` — one `let <fn> = body`, public-first). But a
**recognizer-emitted** function is a CLUSTER of helper `let rec`s (`__gstmt`, `__Lbody`, `__Lorelse`, `__f`, `__nx`,
…) with the PUBLIC `let irscanner__find_assigned_vars` emitted **last** (confirmed: `ir_scanner.mlw` helper at
provider L241, public at L328). So `<G>Sig` declares the WRONG symbol (`…__gstmt`, the first helper) and the
provider's trailing `clone {g}Sig with val <public> = <public>` (line 1201–1203) references the true public symbol
the Sig never declared → the unbound/`refn'vc` failure. The bug is intrinsic to the provider's **self-clone**
(`<fn>'refn'vc`), independent of whether any cross-module caller uses the Sig — so it hits `find_assigned_vars`
AND (identically) a tagged `_collect_mutations` (also recognizer-emitted). verify_module is therefore unusable on
EITHER walker in this file as-is.

**Reopening capability — now NARROW and OWNED (was: vague "review-gated modular verification"):** teach
`_sig_val_from_let` / `_transpile_modular` (Module6_WhyMLTranspiler.py) to select the group's **public entry**
symbol `whyml_ident(f['name'])` for the `<G>Sig` `val` (keeping the helper `let rec`s private inside the provider
`<G>` module) and substitute only that public symbol in the clone. Small, correctness-improving transpiler fix —
BUT it is (a) OUTSIDE this worker's additive-only scope (edits `Module6_WhyMLTranspiler.py`, not
module_collect/Module5/module6_whyml/), and (b) **corpus-relevant** (os's three `verify_module` groups are
single-body and rely on the current first-let behavior; the fix MUST preserve their emission — byte-diff gated).
CLASSIFICATION: CORRECTNESS-adjacent transpiler capability (a modular-emitter *bug* on multi-let groups), NOT a
COST/SCALE grind. An in-scope alternative (restructure the recognizer to emit the public `let` FIRST in a mutual
`let rec … with …` block, module6_whyml/) was NOT pursued: it changes the FLAT emission of the already-landed
`find_assigned_vars` (byte-diff + re-prove the razor-edge goal) — a risky reorder, flag-not-auto per safe-bricks.

**Ops lesson (carry-forward):** `#@ verify_module` modular emission was built + tested ONLY for single-body methods
(os). It silently mis-emits any **recognizer-emitted** function (multi-`let` cluster) because `_sig_val_from_let`
is first-`let`-only. Before proposing verify_module to isolate a RECOGNIZER-lowered walker, this Sig-generation
gap must be fixed first. Chain of named reopenings for this wall is now: no_inline (#18 refuted) → verify_module
as-is (#20 refuted, recognizer-group Sig bug) → `_sig_val_from_let` group-awareness fix (out-of-worker-scope,
corpus-gated).

---

## `ir_scanner._collect_mutations` — `#@ verify_module` REFUTED **decisively** (worker#22, 2026-08-04) — CERTIFIED-BOUNDARY stands; verify_module is the WRONG reopening

**Task:** the `_sig_val_from_let` public-entry Sig fix worker#21 named IS committed (HEAD 52c08479, os byte-diff 0).
So rebuild worker#17's `_collect_mutations` recognizer, apply `#@ verify_module` to isolate `find_assigned_vars`'
razor-edge `__Lbody`/`__Lorelse` size-postcond readers, and land the whole-file proof (804→803).

**Everything BUILT and GREEN except the proof — the recognizer is NOT the blocker:**
- Front-end collector (Module5 `visit_ClassDef` `else` branch → module-level `class_str_set_constants[Cls]={CONST:[members]}`
  for a FIELDLESS class; captures `IRScanner._MUTATING_METHODS`'s 10 members, source order) — DONE, verified.
- `recognize_collect_mutations(func, class_str_sets)` + `emit_collect_mutations_group` (generic_fold.py; dispatch
  functions.py passing `self.ir["class_str_set_constants"]`; gate `needs_pydict` preamble.py) — DONE. The emitted
  MutMod provider body is **BYTE-IDENTICAL to worker#17's banked `scratchpad/cm_structvar.mlw`** (`ref (list pyval)`
  Cons-accumulator, generic `__walk/__walkd/__walkl` structural-variant descent, 3 branch checkers, `pystr_eq`
  member disjunction, opaque `__hassep/__recv/__meth` reflecting the "." sep). **L3-tc ✓.** MUTATION TEST PASSES
  (perturb a member `append→appendXY` → disjunction moves; perturb sep `.→/` → `__hassep f "/"` moves) — NON-FACADE,
  `list pyval` model, no int-hash. The Sig fix works: `MutModSig`/`VarsModSig` correctly declare the PUBLIC entry.
- Count 839→838 (grep-count; the "804" ledger is a different scope).

**The wall (decisive 3-proof spike, Gate S / measure-before-build):** `find_assigned_vars`' two size-postcond reader
goals (`__Lbody'vc`/`__Lorelse'vc`, `ensures { size_list result <= size_dict d }`) are the razor-edge, and
**`#@ verify_module` modular emission ADVERSELY TIPS them — it is the WRONG tool, not a scale-vs-isolation win.**
Three whole-file `pycsl` proofs, differing ONLY in the verify_module tags:
| variant | find_assigned_vars tag | _collect_mutations | find_assigned_vars `__Lbody/Lorelse` | file verdict |
|---|---|---|---|---|
| **t3 = HEAD** | none (flat) | trusted stub | **Valid, 0.23s / 490K steps** | **SUCCESS** (all proven) |
| t2 | `verify_module VarsMod` | trusted stub | **Timeout, 30s / 280M steps** | FAILED (2 goals) |
| proof2 | `verify_module VarsMod` | converted (MutMod) | Timeout, 30s / 280M steps | FAILED (2 goals) |
The t2-vs-t3 pair is decisive: with `_collect_mutations` still TRUSTED and the ONLY change being the
`#@ verify_module VarsMod` tag on `find_assigned_vars`, its goals regress **Valid 0.23s → Timeout 30s/280M steps**
(a ~6-order-of-magnitude search explosion). The modular scaffolding (`module VarsMod use Shared … clone VarsModSig
with val …`'s `'refn'vc` context + the `use Shared` trigger set) perturbs the already-razor-edge E-matching past the
cliff. So verify_module CANNOT rescue this wall — isolating find_assigned_vars makes it WORSE, not better. This
supersedes the #17/#18/#20 chain's assumption that verify_module (once the Sig bug is fixed) is the reopening.

**Classification:** COST/SCALE-adjacent CORRECTNESS wall (no ADT/cert/axiom; the razor-edge is a solver-search
cliff). **Both landing paths that keep `find_assigned_vars`' current size-postcond emission FAIL:** flat+cm tips it
(worker#17), modular tips it MORE (worker#22). **Corrected reopening — the ONLY remaining path:** make
`find_assigned_vars` ROBUST by a **faithful selective-structural-variant rewrite** of `emit_find_assigned_vars_group`
that eliminates the `__Lbody`/`__Lorelse` size-postcond readers entirely (recurse via mutual structural
`{v}/{d}/{xs}` variants like `_collect_mutations` already does + proves robustly), THEN convert `_collect_mutations`
FLAT (no verify_module). FEASIBILITY: the structural pattern is proven (_collect_mutations). RISK/CAVEAT: (a) it
RE-EMITS an already-landed, already-proven function (regression risk; the mirror `.mlw` moves — corpus-inert since
find_assigned_vars is mirror-only, but re-prove required) — "flag-not-auto per safe-bricks"; (b) FAITHFULNESS TRAP:
a NAIVE generic structural descent over-collects (find_assigned_vars descends SELECTIVELY — While/For `body` only,
NOT `orelse`; If `body`+`orelse`; Try `body`+handlers) so the structural rewrite must preserve per-tag selectivity
(bind the descent list via a structural `match` on the parent's cells, NOT via a reader function that breaks the
structural-order chain). Chain of reopenings is now: no_inline (#18 refuted) → verify_module-Sig-fix (#21 built) →
verify_module-as-reopening (#22 REFUTED, decisive spike) → **find_assigned_vars faithful-structural-robustification
(un-tried; the only remaining path, in-scope filewise but risky landed-fn re-emission).**

**Ops lesson (carry-forward, general):** `#@ verify_module` isolation is NOT a universal "stop the E-matching
summation" lever — for a goal already at the solver-search RAZOR EDGE (proves flat only via pycsl's per-goal
best-of-N), the modular `use Shared`/`clone …'refn'vc` context is a PERTURBATION that can tip it OVER the cliff.
Before proposing verify_module to rescue a razor-edge goal, spike it: tag the razor-edge function ALONE (leave the
new walker trusted) and prove — if THAT regresses vs flat-HEAD, verify_module is refuted and the real fix is goal
robustification (structural variants), not isolation. Reusable artifact: `scratchpad/cm_structvar.mlw` is the banked
byte-identical `_collect_mutations` group emission for the next attempt (recognizer rebuild is a solved ~1h step).

---

## 2026-08-04 — 96h run, campaign (1) Wall-2 iterator model RE-MEASURED: CERTIFIED-BOUNDARY (exhausted)

Worker measured every residual `\trusted` mirror stub whose LIVE body uses `.items()`/`.values()` and
emitted the tractable ones in isolation. Verdict `no_feasible_candidate` — the recognizer-addressable
`.items()`/`.values()` frontier is exhausted at the 804 floor. The residual walkers share ONE root: the
**nested-`def` closure idiom** (boundary A) — the existing recognizers were built for module-level /
self-recursive walks and do NOT match a nested `def rec` + mutable-cell (`found=[False]`) closure.
Residual list + concrete first blockers:
- `preamble.py::_func_returns_string_seq` / `functions.py::_returns_string_seq` — nested `def rec` +
  `found=[False]` closure over `.values()`, threads a LOCAL second dict `svt`; isolation emission is a
  broken facade (closure→top-level `py_rec` writing `found` out of scope, int-hash erasure); functions.py
  variant also reads `getattr(self,"_seq_value_types",{})` (self-state).
- `core_ir_semantic.py::_check_typeddict_access/_check_namedtuple_access/_check_union_narrowing` — walkers
  already converted, but blocked: `.items()` set-comp int-key-erases the `set` param to `map int (option int)`,
  and their leaf checkers are warn-only facades (`_namedtuple_check_call` also tuple-unpacks a heterogeneous
  dict value `nt_arities[callee]=(int,list,set)`).
- `ir_scanner.py::find_array_and_dict_vars/collect_escaping_exceptions/_collect_mutations/find_iteration_mutations`,
  `ir_resolve.py::_contract_referenced_names`, `preamble.py::_collect_critical_mutexes` — hard boundaries
  (Tuple[Set,Set], cross-module split, out-param append, record-of-dict, nested-def closure, self-state+sorted).
The single buildable-in-principle target is a NEW recognizer for the nested-`def` closure existence/collect
walk (would cover the `_*returns_string_seq` pair + `_contract_referenced_names` + `_collect_critical_mutexes`
+ the core_ir_semantic collector family) = boundary A, a deliberate multi-session build (faithful nested
FunctionDef + mutable-cell closure IR modeling + local-dict threading), NOT a single-session recognizer match,
and its natural proof targets (preamble.py/functions.py) are the wedge-prone heavy mirror files. Ledger 3,
tree unchanged, no facade/axiom. → advance to campaign (2) string-keyed-set κ-inference.

## 2026-08-04 — 96h run, campaign (2) string-keyed-set κ-inference RE-MEASURED: CERTIFIED-BOUNDARY (mined out)

Worker measured every residual StrSet-touching stub (membership + building). Verdict `no_feasible_candidate`,
count unchanged 804. TWO sub-walls, decomposed:
- **module-level compound-const front-end κ-gap: BROKEN + MINED OUT.** The additive-collector fix already
  landed (6b90b307 `collect_module_const_str_pairs`→`_strip_const_name`; 0c258e45 `collect_module_const_str_sets`
  →`all_phase1_exceptions`), byte-inert, ledger 3. A general `x in MODULE_SET` membership recognizer over the
  existing collector has NO clean whole-body target left: every consumer is either already converted
  (`_val_is_bool`,`_check_no_exception`) or embedded in a heavier boundary (regex-cursor parser struct_format;
  set-difference-over-dict.keys() ir_schema; recursive Term-ADT canonical; raw-ast/token-cursor Ingestor/parser).
- **worklist-BFS bounded-universe: BOUNDARY STANDS (ledger-3).** `bases_closure`/`_recursive_methods`/
  `compute_sccs` build a set via BFS over an abstract `map string (list/set string)` with no dischargeable
  variant absent a bounded-universe AXIOM → would violate ledger 3. Hard boundary. Plus I/O + stateful-mutation
  residuals. All clean structural collect-walkers already converted. → advance to campaign (3) _check_noreturn/SRaise cert.

## 2026-08-04 — 96h run, campaign (3) _check_noreturn/SRaise cert: ALREADY COMPLETE (no work available)

Worker (spike-first) found the campaign already landed in the current tree, ledger 3:
- `_check_noreturn` is a VERIFIED body (mirror core_ir_semantic.py:653), landed baaebd51 via pget
  size-postconditions on the EXISTING pydict theory — it only READS the IR dict, constructs no SRaise,
  needed NO new value shape and NO cert. The whole noreturn family (551/600/653/705/720/731/761) is verified.
- The SRaise stmt_ir value shape already exists independently (statements.py:37 `stmt_ir = ... | SRaise string`)
  with axiom-free co-landing certs already built in BOTH provers: src/formal-semantics/rocq/Phase2d_StmtIR.v
  ("Closed under the global context, NO axiom, nothing Admitted") + lean/PyCSL/StmtIR.lean (standard kernel
  axioms only); no Axiom/Admitted/Parameter/sorry/admit in either. Ledger intact at 3.
The only SRaise-ADJACENT residual is `_py_stmt_raise` (Module5_IREmitter) — held NOT by the value shape
(SRaise exists) but by a callee Name-vs-Attribute distinguishability CORRECTNESS boundary (different campaign).
→ campaign (3) resolved COMPLETE; advance to campaign (4) string-parse modeling.

## 2026-08-04 — 96h run, campaign (4) string-parse modeling: CERTIFIED-BOUNDARY (mined out)

Worker measured the whole string-parse frontier. Verdict `no_feasible_candidate`, count unchanged 804.
CORRECTION to faithful_string_op_project memory: the LIVE emitter (expressions.py:5505-5570) ships MORE than
P1-P4 — it also has faithful, mutation-sensitive `str_startswith_op`/`str_endswith_op`/`str_find_op` (each with
a real `(result=1)<->(len prefix<=len s /\ substring s 0 .. = prefix)` ensures). So every whole-body stub
reachable with existing ops is ALREADY converted (`_clean`, `safe_mutex_name`, `_strip_const_name`, `_short_type`,
`safe_exc_name`, `_call_returns_string_collection`). The two genuine missing ops that would each unlock >0 bodies
CANNOT be added within ledger-3:
- **regex-cursor model** (`_TOKEN_RE.match(s,pos)` / `re.sub`) — no sound WhyML model without heavy machinery;
  an opaque match is a Gate-C facade. Blocks parse_format/calcsize/_strip_all_parens/_alpha_rename.
- **`int(str)`/`float(str)` string→numeric parse** — the no-more-int wall; any lowering is an int-hash facade.
  Blocks _parse_number/calcsize.
Adding faithful `partition`/char-iteration would unlock NO single whole body (each such stub also needs a
regex/int-parse op or touches heterogeneous IR-dict/self-state). `stable_hash` = irreducibly opaque sha256
(not string-parse). `classify` residual membership = the separate collection value-model wall (int-hash facade).
→ campaign (4) CERTIFIED-BOUNDARY; advance to campaign (5) opaque ast/IO.

## 2026-08-04 — 96h run, campaign (5) opaque ast/IO modeling: CERTIFIED-BOUNDARY (Gate-C reject on the one candidate)

Worker produced ONE candidate — `import_classifier.any_function_trusted` (raw-ast existence walk) — and
honestly flagged it borderline. Supervisor ran the evidence-based Gate-C review (emitted WhyML + compared to
the accepted precedent `_has_dynamic_exec`) and REJECTED it. Count returned 804, WIP reverted.

DECISIVE DISTINCTION (banked, general — the opaque-ast non-vacuity line):
- `_has_dynamic_exec` (ACCEPTED) descends a REAL modeled pyval: `match v with PDict d | PList xs`, reading
  REAL accessors (`_gbody`/`_gtype`/`_gfunc` typed-key readers over the real pydict ADT), recursion over REAL
  size measures (`pv_size`/`size_dict`/`size_list`); only the leaf exec-test rests on real `pystr_eq` string
  compares. Non-vacuity SATISFIED — the proof establishes correct structural recursion over real modeled data.
- `any_function_trusted` (REJECTED) has NO pyval model of the raw pure_ast tree, so `ast.walk(tree)` lowered to
  a FULLY OPAQUE `val __walk (tree:pyval) : list pyval` that MANUFACTURES the list spine; the fold walks that
  opaque list (`variant {xs}` terminates trivially), and BOTH leaf predicates (`__is_FunctionDef`/
  `__getattr_csl_trusted`) are opaque `val`s too. Body reads ZERO real accessors; postcondition `ensures true`.
  The verified skeleton is only "a fold over an opaque list terminates." `__walk`/`__is_`/`__getattr_` ARE the
  opaque `_get_N`-style primitives Gate-C non-vacuity forbids. Count 804→803 but the TCB does NOT shrink — it
  relocates from 1 stub into 3 opaque vals. Count-only win → Gate-C REJECT (skill §7 VALUE-not-count).

RULE (carve-out): an opaque-ast/IO conversion is non-vacuous ONLY if the fold descends REAL modeled structure
(real pyval constructors + real accessors, like _has_dynamic_exec) OR the postcondition constrains a real result
(e.g. a StrSet the body builds with size bounds). A raw-ast tree with NO pyval model yields an all-opaque
skeleton (opaque walk + opaque leaves + ensures true) = facade, stays \trusted. The residual ast/IO stubs
(`collect_imports`/`check_imports`/`_stub_set`/`audit_proof._parse_*`/`_index_proofs_dir`) share this
opaque-external-primitive root PLUS heavier obstacles (tuple/List construction over node reads, filesystem
iterdir+path .stem/.suffix, unmodeled read_text() string parse, caller-coupling to verified classify) → boundary.

=== ALL 5 AUTHORIZED CAMPAIGNS RESOLVED (2026-08-04 96h run) ===
(1) Wall-2 .items()/.values() iterator model — CERTIFIED-BOUNDARY (recognizer frontier exhausted; residual root
    = nested-def closure = boundary A, multi-session).
(2) string-keyed-set κ-inference — CERTIFIED-BOUNDARY (module-const κ-gap BROKEN+mined out; worklist-BFS needs a
    bounded-universe axiom = ledger-3 boundary).
(3) cert (_check_noreturn/SRaise) — ALREADY COMPLETE (landed baaebd51 + Phase2d_StmtIR axiom-free certs, ledger 3).
(4) string-parse modeling — CERTIFIED-BOUNDARY (str-op lib mined out; regex-cursor + int(str) parse both facades).
(5) opaque ast/IO modeling — CERTIFIED-BOUNDARY (only candidate is an all-opaque vacuous skeleton, Gate-C reject).
Count 804, ledger 3. Autonomous frontier at confirmed floor for this run — hold, do not spin.

## 2026-08-04 — 96h run, boundary A (nested-def closure walk) SPIKE PASSES → build greenlit

Make-or-break isolation spike on `_func_returns_string_seq` (preamble.py) — the cleanest nested-`def`+
`found=[False]` closure that threads a local dict `svt`. Result: FEASIBLE, non-vacuous, axiom-free (7/7 VCs
Valid <0.2s, ledger 3, only device = blessed VC-free `val pystr_eq`). This OVERTURNS the repeated boundary-A
"un-modelable" classification — it was a COST/SCALE hypothesis, not a correctness wall. How the 3 feared
constructs lower:
1. nested `def rec` closure → standard mutual `frss/frss__v/frss__d` catamorphism (SAME shape as the landed
   `emit_bool_existence_group`/`_has_dynamic_exec`); nested-def-vs-while-worklist is pure surface difference.
2. `found=[False]` out-of-scope mutable cell → `||` short-circuit disjunction (`leaf(d) || descend children`).
   NO heap ref, NO opaque val — the existence fold subsumes the cell exactly.
3. local dict `svt` + `svt.get(v.get("name"))=="string"` → `svt` threads as a REAL `pydict` param (extracted
   once via pget_dyn "seq_value_types", passed unchanged, kept OUT of the variant), leaf is REAL nested field
   navigation (pget_dyn "stmt"/"value"/"type"/"name") + a computed-key read `pget_dyn nm svt`. pystr_eq only at
   terminal string compares. CRITICAL build note: `svt`'s VALUE is inspected → thread it as a real pydict read,
   NOT as the opaque membership-set `map string bool` (that would drop the leaf to a facade / Gate-C reject).
CAVEAT (isolation_spike_not_whole_file): this proves FEASIBILITY only; the authoritative gate is the whole-file
pycsl proof over preamble.py (E-matching over full wf_dict/wf_ir_binds may saturate — the trio-fusion risk).
→ build the recognizer, then supervisor runs the authoritative whole-file proof.

## 2026-08-04 — 96h run, boundary A clean follow-ons DRAINED (804→801, 3 conversions)

Both recognizer variants landed + drained the clean existing-device follow-ons:
- `_func_returns_string_seq` (711c3b33, existence bool-fold, preamble.py)
- `_contract_referenced_names` (c28e1b83, StrSet set-collect, ir_resolve.py)
- `_contract_referenced_var_names` (0b335205, StrSet set-collect two-arm Var/Attribute, ir_resolve.py) —
  NOTE: this fn is defined TWICE (dead first def + effective source-last def, Python shadowing); the emitter
  dedups via scc.py::sort_functions_by_scc (keeps LAST). Convert ONLY the effective def; the dead def stays
  trusted (never emitted) → count drops by exactly 1. Not a landmine.
REMAINING boundary-A tier needs a NEW DEVICE (surveying + spiking next): de-Bruijn depth-threading int
accumulator (`_body_references_bvar_0`); list-of-(str,str)-pairs accumulator (`_scan_node_for_subscript_calls`,
+ opaque `_type_str`); self-state pydict model (method-form folds `_returns_string_seq`/`_has_keywords_iteration`/
etc. read `getattr(self,"_seq_value_types"/"ssf"/"_module_func_raises")` — self-state is a long-classified
boundary; the mixin self is not a modeled value → likely REFUTE unless a faithful pydict source exists).
`_collect_critical_mutexes` = self.ir + sorted() (no faithful StrSet-sort model) = boundary.

## OPS HAZARD (recurred 2026-08-04) — byte-diff-sweep.sh MOVES corpus .mlw fixtures out of the tree
`bin/byte-diff-sweep.sh` does `mv <corpus>/pycsl-reference/NAME.mlw <out>/NAME.mlw` for every 0*.py it emits,
which DELETES the committed conformance fixtures (0893-0924*.mlw etc., the git-add-f fixtures) from the working
tree. These show as ` D` in git status. SAFE because they're never staged (I git-add only the specific
conversion files), so HEAD is intact — but the supervisor MUST `git checkout HEAD -- test-suite/corpus/pycsl-reference/`
after EVERY sweep, and ALWAYS verify `git status --porcelain test-suite/corpus/pycsl-reference/ | grep -c '^ D'`
is 0 before committing. Never `git add -A`/`git add .` (would stage the deletions). See feedback_parallel_sweep.

## 2026-08-04 — 96h run, _scan_node_for_subscript_calls (list-of-pairs device): CERTIFIED-BOUNDARY (whole-file E-matching scale wall)

The list-of-(string,string)-pairs accumulator device is FEASIBLE in isolation (spike 17/17 Valid) and my own
goals prove (`--fun` 32/32; the whole-file run's ONLY timeout is a SIBLING, never a `_scan`/`_type_str` goal).
But the conversion is BLOCKED at whole-file scale by a razor-edge sibling in the same module,
`_subst_type_in_ir__list'vc` (a heavy pyval-recursion IR rewriter that proves clean at HEAD):
- Attempt 1 (list-concat `++`): added `use list.Append` to the shared theory → 5 sibling goals timeout (77M steps).
- Attempt 2 (threaded-accumulator, Cons/Nil only, `use` block BYTE-IDENTICAL to HEAD): 5→1 timeout, but
  `_subst_type_in_ir__list'vc` STILL times out (324M steps). So it is NOT the theory import — merely ADDING my
  new recursive pyval functions (`__scan`/`__dfold`/`__lfold` + inlined `_type_str`/`_sanitize`) to the module
  expands the E-matching search space enough to tip the razor-edge sibling over. monomorphize.py proves clean at
  HEAD; +my conversion → the sibling saturates.
This is the isolation_spike_not_whole_file / trio-fusion terminus class: an isolation spike proves FEASIBILITY,
not whole-file PROVABILITY; a sibling goal already at the solver-search razor edge is tipped by ANY module
addition. The re-encode (contamination-free) is the right autonomous fix and it HELPED (5→1) but cannot clear the
last razor-edge goal. Reopening needs modular verification (verify_module to isolate the new functions from the
sibling's proof context — but verify_module is review-gated AND can make razor-edge goals worse, per the driver
frontier floor lesson) — OUTSIDE the autonomous envelope. LEFT TRUSTED. Device banked for a review-gated retry.
This CLOSES the boundary-A drain: 4 converted (804→800: _func_returns_string_seq, _contract_referenced_names,
_contract_referenced_var_names, _body_references_bvar_0); _scan = whole-file-scale boundary; the rest of the
tier is self-state (hard boundary). Autonomous boundary-A floor = 800.

## 2026-08-04 — 96h run: AUTONOMOUS FLOOR CONFIRMED at 796 (8 conversions this run, 804→796)

After breaking boundary A (nested-def closure walks) and the self-state tier, the clean banked-device frontier
is drained. Final string-op-gated vein MEASURED and confirmed BOUNDARY:
- `collect_escaping_exceptions` (ir_scanner.py) — gated on the trusted opaque `handler_catches` predicate which
  IS the classification (modeling it opaque swallows the classification → non-vacuity violation) + split-ITERATION
  (`for ep in exc.split("|")`, not an element-index read; str_split_op is an abstract over-approx). BOUNDARY.
- `find_array_and_dict_vars` (ir_scanner.py) — needs a `rsplit(".",1)[-1]` last-component op that DOESN'T EXIST
  (str_split_op splits forward into an abstract array; `[-1]` of unknown-length split not expressible) + a
  Tuple[Set,Set] 2-tuple-of-sets return (unbuilt shape). BOUNDARY.
Available faithful string ops (confirmed): startswith/endswith/find/split_elem/split(abstract)/strip/replace/case/
join. MISSING: rsplit/rpartition/last-component; int(str)/regex-cursor (known boundaries).

CONVERSIONS THIS RUN (all axiom-free ledger-3, full supervisor battery):
1 _func_returns_string_seq (711c3b33) 2 _contract_referenced_names (c28e1b83) 3 _contract_referenced_var_names
(0b335205) 4 _body_references_bvar_0 (b2ea3474, de-Bruijn depth) 5 _returns_string_seq (a851f95f, self-state)
6 _collect_struct_pack_assign_targets (9a5ed0ef, +E-matching fix) 7+8 _collect_map_typed_locals + _has_set_op_on_map
(fec790cb, auto_trust cluster). REJECTED (whole-file-scale wall): _scan_node_for_subscript_calls (tips razor-edge
_subst_type_in_ir sibling). BOUNDARY records: any_function_trusted (facade), string-op vein (above).

RESIDUAL ~796 = genuine floor for the AUTONOMOUS single-session envelope. Every remaining value-fold stub is:
heterogeneous value-model ROOT (find_iteration_mutations/_collect_mutations — accumulate whole IR dicts; needs new
ADT + §10.5 co-landing cert + Gate-R review = MULTI-SESSION, review-gated), OR self-mutation frame
(_collect_tuple_var_assigns — writes self.field, self=opaque int not a record), OR facade (_call_return_whyml_type),
OR fixpoint-invariant (_collect_array_var_assigns while-changed — new device), OR string-op boundary (above), OR
whole-file-scale E-matching (review-gated modular verification). The ~780 rest = raw-ast parser (pure_ast 223),
surface parsers (Module2/proof2why3 sexp), subprocess I/O (sertop/coqc/lean), hashlib, string-builder/stateful
emitters. NONE in the autonomous envelope → HOLD at 796, do not spin. Reopening any needs user authorization
(value-model root / self-as-record modeling / modular verification are the standing review-gated reopenings).

## 2026-08-08 — 96h run #2, value-model ROOT feasibility SPIKE: PASSES (axiom-free-feasible)

Scratchpad make-or-break spike on the biggest review-gated lever (ir_scanner._collect_mutations +
find_iteration_mutations). VERDICT: axiom-free-feasible; corrects a prior ledger over-statement.
- (a) RECORD embedding a full pyval node (find_iteration_mutations `{loop_target,iterable_name,mutating_stmt:pyval,
  loop_line}`) — CLEARED. A NON-recursive record over already-certified pyval+string+int carries NO independent
  well-foundedness obligation → NO new ADT, NO new §10.5 co-landing cert (ledger line ~1570 was imprecise).
- (b) class-constant splice `method in IRScanner._MUTATING_METHODS` (10-elem Set[str] class const) — CLEARED.
  pystr_eq disjunction over the literal members via the already-built class_str_set_constants collector;
  axiom-free, mutation-sensitive, non-facade (NOT opaque-membership).
- (c) whole-file E-matching SCALE — the ONLY real wall. Size-postcond reader encoding (`get_list_field`'s
  `size_list result <= pv_size stmt`) times out in isolation (worker#17's __Lbody/__Lorelse razor-edge, reproduced
  exactly, 60s/65M steps). The STRUCTURAL-variant encoding proves 16/16 fast under Z3+Alt-Ergo, zero axioms —
  removes the size-postcond reader entirely. But clearing it requires re-emitting the LANDED find_assigned_vars.
KEY INSIGHT (contained path): the razor-edge goal shape (`size_list result <= size_dict d` on a K_dyn typed-key
list reader) is EXACTLY what the banked pget_dyn+pget_list reader-SPLIT (option-search + non-recursive composer)
cleared for struct-pack's Lhandlers last run (9a5ed0ef). Applying that split to find_assigned_vars' readers is
PROOF-ENGINEERING (body unchanged, verbatim mirror, byte-inert, re-proven per §10.4) — NOT the risky structural
rewrite with the per-tag-selectivity faithfulness trap. If the reader-split clears find_assigned_vars' razor-edge
whole-file without tipping a sibling, _collect_mutations + find_iteration_mutations convert within the autonomous
envelope. If it does NOT clear it → flag the structural-rewrite build (re-emits a landed proven fn + Gate-R review)
for user authorization. MEASURING the contained path next.

## 2026-08-09 — 96h run #2: value-model ROOT BROKEN (796→794); _scan boundary reconfirmed

VALUE-MODEL ROOT (deepest documented wall) BROKEN, 2 conversions axiom-free ledger-3:
- _collect_mutations (c6557971): ref (list pyval) whole-node accumulator + class-const-splice
  (_MUTATING_METHODS → pystr_eq disjunction) + reader-split. ENABLER: reader-split on the LANDED
  find_assigned_vars cleared its whole-file razor-edge (de-risk gate: Timeout→Valid, no regression,
  §10.4 re-prove). CAPABILITY: class_str_set_constants Module5 registry for fields-less classes (byte-inert).
- find_iteration_mutations (fdbccc77): NON-recursive record embedding a WHOLE pyval node (mrec) — NO new
  §10.5 cert (the ledger's "needs new cert" was an over-statement, corrected by the spike); calls the
  converted _collect_mutations; caller-coupling free (consumer is a live-only trusted stub).
METHOD BANKED: spike→de-risk-gate→build. A "review-gated multi-session" verdict is a HYPOTHESIS — spike the
CONTAINED path (banked reader-split on the razor-edge sibling) before flagging for authorization; it turned an
autonomous win out of what run #1 had flagged as needing user auth.

_scan_node_for_subscript_calls RE-MEASURED (reader-split does NOT generalize): its whole-file blocker
`_subst_type_in_ir__list'vc` is a structural-PRESERVATION VC (`ensures wf_list_deep result /\ frag_list result`),
NOT a `size_list result <= size_dict d` list reader — no key-projection reader to split, and _subst_type_in_ir
comes from general body-lowering (not a recognizer group) so its VC can't be reshaped byte-inertly. The 324M-step
blow-up is E-matching SCALE over the recursive wf_*/frag_*/size_* predicate family enlarged by _scan's new
functions. LESSON: the pget_dyn+pget_list reader-split clears size-postcond list-reader razor-edges (find_assigned_vars,
struct-pack Lhandlers) but does NOT apply to structural-preservation VCs from general body-lowering. _scan stays
CERTIFIED-BOUNDARY → review-gated modular verification (isolate _scan's recursion from the sibling's proof context).

## 2026-08-09 — 96h run #2: AUTONOMOUS FLOOR CONFIRMED at 789 (7 conversions this run, 796→789)

After the value-model-root break + its map-accumulator cascade, a thorough measure+BUILD survey (2 candidates
built and reverted after honest --fun failure) confirms the autonomous single-session floor at 789.
CONVERSIONS THIS RUN (all axiom-free ledger-3, full supervisor battery): _collect_mutations (c6557971),
find_iteration_mutations (fdbccc77), _build_method_writes_map (b161952d), and the cluster x4 _collect_record_fields
+ _build_method_result/field_result/field_old_ensures_map (967e1b79). Broke the DEEPEST documented wall
(heterogeneous value-model root) via spike→de-risk-gate→build; banked __setk (map-to-list accumulation),
class_str_set_constants Module5 registry, mrec record-embedding.

REMAINING (each measured, BUILD-tested where reachable):
- collect_escaping_exceptions — REACHABLE-BUT-REVIEW-GATED: BUILT+REVERTED; inner_raised extraction falls to the
  opaque per-receiver stmt_get_N model (Gate-C reject) AND the Try arm is a hierarchy-aware SET-DIFFERENCE
  {e in inner_raised : not any handler_catches(b,e)} — needs a NEW recognizer arm (opaque-predicate set-difference),
  not a verbatim port. Review-gated recognizer build.
- _extract_array_lengths (auto_trust.py, map string int builder) — REACHABLE-BUT-PROOF-SCALE-WALL: BUILT+REVERTED;
  EMITS + TYPECHECKS CLEAN (str()/int() coercions, .setdefault, prefix-slice, map string (option int) all lower —
  NOT blockers) but 2 goals TIMEOUT at 30s (132M/369M steps); a 90s+ why3 split run didn't converge in 10min.
  Root: nested closures _field_of/_int_of → opaque int→int vals + option-int UNION-UNWRAP over the map =
  E-matching explosion. reader-split N/A (not a size-postcond list reader). Genuine proof-scale wall → needs
  review-gated modular verification / a targeted proof-engineering session (different closure encoding).
- find_array_and_dict_vars (missing rsplit-last-component); _collect_struct_unpack_array_targets (opaque
  StructFormat.slots int); _collect_tuple_var_assigns / _collect_string_elem_read_locals / _collect_field_decode_str_locals
  / _typed_local_vars (self-mutation frame — self opaque int, not a record); _collect_array_var_assigns (fixpoint
  while-loop + 10-arm classifier); Module5 _scan_2d_* (mutual-recursion + sorted + corpus-frontend); module_collect
  collect_module_constants/globals (raw-AST ast.walk boundary, the 223-\trusted pure_ast wall); rename-using
  _build_method_*_ensures_map (pyval structural rewrite, _subst_type_in_ir class). ALL boundary/review-gated.
HOLD at 789. Reopenings need new recognizer capability / proof-scale modular verification / self-as-record model —
outside the autonomous verbatim-conversion envelope. Meta-lesson banked (value_model_root_broken.md): breaking a
ROOT wall CASCADES; re-survey after each break; a "review-gated" verdict is a hypothesis — spike the contained path.

## 2026-08-09 — 96h run #2: _extract_array_lengths PROOF-SCALE WALL BROKEN by re-encoding (789→788) — NEW DEVICE

The measure+build survey classified _extract_array_lengths FLOOR/proof-scale (emitted+typechecked clean but 2
goals timed out 132M/369M steps; 90s+ split why3 no convergence in 10min). BROKEN (d032860e) by an ALTERNATIVE
EMIT ENCODING (body verbatim-unchanged) — a ~500× E-matching reduction (369M→701k steps, 0.53s). THE DEVICE
(banked, reusable — this is why "proof-scale boundary" is a HYPOTHESIS, not a floor):
1. OPAQUE VALS CAUSE E-MATCHING EXPLOSION. Abstracting a nested closure / helper as an opaque `val f (x):t`
   the solver keeps re-instantiating (firing its triggers) blows up. FIX: emit it as a FAITHFUL structural
   reader (pget_dyn/pystr_eq → option string/option int gated on the real discriminant tags). The solver stops
   firing the opaque val. This is the general form of the reader-split lesson.
2. PINNED MAP PRIMITIVE for option/map arithmetic. A manual option-int union-unwrap over a `map string (option
   int)` unfolds Map/option theory at EVERY fold step → explosion. FIX: capture the whole update in ONE pinned
   `val __setdefault (m) k nn : map string (option int) ensures { result = Map.set m k (match Map.get m k with
   None -> Some nn | Some x -> Some x end) }` (the __setk device generalized). The walker VC then carries an
   OPAQUE UPDATE and never unfolds the theory per step. Sound (conservative realization of total Map ops), NOT
   an axiom, ledger 3.
3. Module5-LIFTED closures → a PAIRS recognizer (mirror recognize_collect_map_typed_locals_pairs) pairs the outer
   wrapper with its adjacent lifted siblings by adjacency + suppresses them.
META: cost_scale_not_floor VALIDATED again — a MEASURED proof-scale wall fell to a re-encoding spike. Re-examine
EVERY "proof-scale/E-matching-timeout" boundary for opaque-vals-in-VC before concluding floor. Candidates to
re-check with this device: collect_escaping_exceptions (opaque per-receiver stmt_get_N = the SAME opaque-val
pattern → faithful readers; + set-difference fold over the CONVERTED handler_catches).

## 2026-08-09 — 96h run #2: collect_escaping_exceptions BROKEN (788→787) — pointwise set-difference device

Another prior boundary (opaque per-receiver Gate-C reject + hierarchy-aware set-difference "needs new recognizer
arm") BROKEN (65be306e). Two banked insights:
1. FAITHFUL READERS beat opaque per-receiver (the re-encoding device, d032860e): inner_raised from
   __get_stmt/__get_exc/__handlers_of structural readers, not opaque stmt_get_N.
2. SET-DIFFERENCE over a characteristic-map is POINTWISE, not enumerated. Set[str] = map string bool
   (non-enumerable), so `{e in S : not P(e)}` = `fun e -> andb (Map.get S e) (notb (P e))` — no enumeration,
   mirrors the certified free_vars set_diff (andb/notb). The predicate P (here handler_catches, absorbing
   exc.split("|") + subclass closure) = an opaque-but-real leaf-gate `val function P (a b: string): bool`
   (same legitimacy as parse_format's __pf_ok / handler_catches' __in_closure). NON-facade because the MAIN
   walk (inner_raised extraction via real fold) is real + the recognizer requires a real handler_catches call.
META: string-op "boundaries" (split/rsplit/subclass-closure) can be ABSORBED into an opaque-but-real leaf-gate
when the MAIN walk is real — the string op need not be modeled faithfully. Re-check find_array_and_dict_vars
(rsplit-last-component → opaque-but-real __last_component leaf-gate; 2-tuple-of-sets → record/pair of StrSets).

## find_array_and_dict_vars — BROKEN (925d5972, 787->786, run #2)
Prior "string-op boundary" (missing rsplit). Broke via **opaque-but-real-leaf-gate + real-classification**:
- 2-tuple return `(arrays, dicts)` → **pair of StrSets** (map string bool); collect via set_add of REAL target name.
- `__classify vd tgt` = a real if-else on value-type discriminants (ListLit/DictLit/BinOp op/SetLit/SliceAccess + real func names via pystr_eq). NON-facade, mutation-sensitive.
- Opaque leaf-gates `__last_component`/`__sw_*`/`__ends_split (s:string):bool` absorb ONLY the string-op-suffix arms (rsplit/encode/split) — the UNMODELABLE leaf, while the MAIN walk is real. Gate-C non-vacuity PASSES (39 real lines, 0 opaque spine).
LESSON: a "missing-string-op" boundary is breakable when the string-op is a LEAF GATE (its result only selects an arm), not the walked spine — reflect it as an opaque bool/string `val` and keep classification real. Same device as boundary-A's parse_format/_rhs_yields_map leaf-gates.

## _collect_struct_unpack_array_targets — BROKEN via spike->build (6533e681, 785->784, run #2)
Twin of the landed pack collector but a genuinely different shape: `for tgt,slot_t in zip(targets, parsed.slots)` (a ZIP over a targets LIST + a slots list). Prior classified "needs new zip-catamorphism + list-of-strings parse_format model = multi-session".
BROKEN via a make-or-break isolation spike (24 goals Valid) that found the CONTAINED encoding:
- Walk the REAL `targets: list pyval` spine (reuse the pack twin's certified pyval catamorphism + size-bounded list reader), thread a plain `int` zip-index.
- Model the per-target decision `slot_t=="array int"` as an OPAQUE per-index leaf-gate PREDICATE `val __is_array_slot (fmt:string) (i:int) : bool` — NOT a list-of-strings model of `.slots`. The slots parse is unmodelable; reflecting the per-index BOOL is enough (over-approx under ensures True).
- Both live branches (struct.unpack format path + the _call_return_whyml_type/_split_tuple_type else path) collapse to the same nested-fold shape; self-calls modeled opaquely (not emitted) => no coupling to the verified _split_tuple_type.
NEW DEVICE BANKED: **per-index leaf-gate predicate over a real zipped spine** — extends the scalar leaf-gate (parse_format/pf_ok) to a ZIP context. The zip's second operand need NOT be modeled as a list; model the per-index DECISION as `val __g (ctx) (i:int):bool`. NO new ADT/cert/axiom; sole new element = a nested index-threaded set-fold (structural variant).
META: "needs zip-catamorphism / list-of-strings model = multi-session" was a HYPOTHESIS; the spike found a contained per-index-predicate encoding. Spike the contained path before flagging multi-session.

## _collect_array_var_assigns — CERTIFIED-BOUNDARY (verbatim path), for-rewrite FLAGGED (run #2, at 784)
The transitive-closure `while changed:` fixpoint. Spike (spike_ava5.mlw) established a sharp two-encoding split:
- **Verbatim live body (`while changed:`) = REFUTE / CERTIFIED-BOUNDARY.** Every sub-VC discharges (invariant-preservation, bounds, postcondition, even a verbatim arithmetic assert of the decrease) EXCEPT the auto-generated **"Loop variant decrease" VC**, which floods BOTH alt-ergo (Timeout ~85k-150k steps) AND Z3 (Out of memory) via E-matching saturation over the stdlib `set.Fset` cardinal axioms. Factoring the inner loop into a helper does NOT clear it. Same class as the whole-file E-matching scale walls (isolation_spike_not_whole_file). NO axiom-free variant clears the literal while at prover scale.
- **`for _ in range(len(var_assigns)+1)` bounded form = PROVES** axiom-free (Why3 `for` carries NO variant VC — terminating by construction; the bound is the live while's own mathematical iteration count: ≤ len(keys) passes to fixpoint, further passes are no-ops ⇒ identical set ⇒ byte-diff-0). BUT this is NOT the verbatim live body ⇒ requires a semantics-preserving REWRITE of the LIVE emitter's control flow (while→bounded-for).
DECISION: the verbatim-conversion path is a CERTIFIED-BOUNDARY. The for-rewrite is a PRODUCTION control-flow change beyond a mirror conversion — FLAGGED for user authorization (safe_vs_risky_bricks: flag reorders/rewrites, don't auto-dispatch), NOT auto-built. If authorized, the move is: rewrite BOTH live+mirror to the bounded-for form + re-prove + byte-diff-0 (identical fixpoint licenses it).
BANKED DEVICE (for when authorized / for other fixpoints): a monotone-set closure over a FINITE key universe lowers to a Why3 `for _i=0 to len(keys)` (NO variant VC, sound, axiom-free) — the mathematical iteration bound made explicit. The literal `while` + set-cardinal variant is the E-matching trap; the bounded-for sidesteps it.

## _collect_string_elem_read_locals + _collect_field_decode_str_locals — CERTIFIED-BOUNDARY (self-collection-mutation-frame), multi-session build FLAGGED (run #2, at 784)
Both share an identical self-field map-write through a getattr alias:
`st = getattr(self,"_current_symbol_table",None); ... st[v]="str"` (live statements.py ~1960-2005 / ~2044-2048).
A faithful contract needs `assigns self._current_symbol_table` (value type Dict[str,Any], heterogeneous).
SPIKE = REFUTE for existing machinery, via THREE independent walls each sufficient:
1. **getattr-self reflection collapse**: `getattr(self,"_current_symbol_table",None)` is value-model-gapped — the alias `st` is NOT modeled as the mutable self field (documented; siblings `_handle_tuple_unpack_stmt`/`_handle_ghost_assign_stmt` were RE-TRUSTED for this exact pattern). So `st[v]="str"` cannot be framed as a self-field write.
2. **Zero-precedent**: the ONLY verified direct self-field writes in the entire mirror are SCALAR (`self.pos+=1`, `_fresh_var_counter`, `self.i`). NO verified method writes a self SET/MAP field; the concrete self-collection writes live only behind the \trusted `_stmts_to_whyml`.
3. **Heterogeneous Dict[str,Any]** value type (`"str"`/`"set"`/`"dict"`, tested `in (None,"Any")`).
DECISIVE ARTIFACT: a positive-control .mlw (self-record + mutable map field + program `val` map-set device + framed post) proves Valid (0.03s) — and `Map.set`/`fmap.add` are logic-only (rejected in program code, need a program `val` device). So **Why3 CAN prove a framed self-map write; the wall is EMITTER CAPABILITY, not proof power.**
CLASSIFICATION: COST / multi-session value-model build (FEASIBLE, not correctness-impossible). To PASS needs NEW emitter capability: (a) model `getattr(self,<field>,default)` as the mutable self field, (b) model local-alias mutation `st[v]=x` as a self-map-set via a program `val` device, (c) faithfully lower the Any map-value. Declaring `assigns \nothing` = unsound trusted-frame-drop (NOT a PASS). => FLAGGED for user authorization (getattr-self-mutable-field emitter capability); would unblock the whole self-collection-mutation-frame class. Ties to [[trusted_val_frame_unsoundness]].

## CONFIRMED AUTONOMOUS FLOOR at 783 (run #2, from 796; 2026-08-09)
Tree-wide read-only survey + auto_trust.py re-drain both return no_cheap_remaining. The value-model/
recursive-tree-walker frontier reopened by the value-model-ROOT break is now EXHAUSTED: every recursive-Any-
walker in the small utility files is already verified; the trusted residue is boundary-classed.
Run #2 ledger (796->783, 14 conversions + boundaries), all axiom-free / ledger-3 / full supervisor battery:
- BROKEN (converted): find_array_and_dict_vars, _collect_tuple_var_assigns, _collect_struct_unpack_array_targets
  (Phase-2 spike->build, per-index-leaf-gate device), _is_linear_expr (bool-existence fold), + the value-model-
  root cascade from the session's earlier window (_collect_mutations root, map-accum cluster, etc.).
- CERTIFIED-BOUNDARY (measured this run): _collect_array_var_assigns (while-changed variant-decrease E-matching
  flood), _collect_string_elem_read_locals + _collect_field_decode_str_locals (self-collection-mutation-frame:
  getattr-self-alias not modeled as mutable field), _build_witness_str (int-hash string facade + heterogeneous
  Dict[str,Any]), _should_auto_trust_tuple_return (set->int collapse, coupled to the array_var fixpoint boundary),
  _check_witness_vals (runtime eval()).
- FLAGGED FOR USER AUTHORIZATION (feasible but multi-session / production-rewrite / review-gated — NOT auto-built):
  (1) the getattr-self-mutable-field EMITTER CAPABILITY (positive control proves Why3 can frame a self-map write;
  unblocks the whole self-collection-mutation-frame class); (2) the fixpoint while->bounded-for LIVE-SOURCE rewrite
  (array_var_assigns); (3) verify_module modular verification for the _scan whole-file E-matching scale wall
  (memory: verify_module worsens razor-edge goals; 2 encodings already tried in prior runs).
Residual ~755 stubs by class (survey): raw-AST/parser ~267 (pure_ast 222), emitter-core scale/value-model ~206,
IO/prover-subprocess ~140, AST-visitor/desugar ~93, IR-resolution/fixpoint/scan ~45, opaque-stdlib/hash/regex/
graph-fixpoint/eval ~30. All previously-measured, review-gated or multi-session.
DECISION per driver ACTION (6): HOLD at floor; do NOT spin to burn clock; integrity-check each heartbeat until
deadline (~87h). Do NOT auto-push (~786 unpushed commits ready; push only on explicit user "push").

## _scan_node_for_subscript_calls — no_inline modular boundary REFUTE (run #2, reconfirmed CERTIFIED-BOUNDARY at 783)
Spiked the ONE untested lever this run: does `#@ no_inline` on the razor-edge sibling `_subst_type_in_ir`
(monomorphize.py:194) isolate its proof context from `_scan`'s added recursive helpers, clearing the
E-matching saturation of `_subst_type_in_ir__list'vc`? **REFUTE — byte-inert.**
ROOT CAUSE (banked): `#@ no_inline` governs ONLY whether a callee's BODY is spliced into CALLER contexts. It
does NOT relocate a function's own body VC out of module scope, nor remove sibling definitions from a goal's
proof scope. `_subst_type_in_ir`'s in-file callers are bodyless trusted stubs (nothing to inline) + self-recursion
is never inlined ⇒ the annotation emits byte-IDENTICAL WhyML (verified: `#@ no_inline` parses/Weaver-sets/Module5-
emits `"no_inline":True` but is a complete no-op here). The wall is proof-SCOPE saturation: converting `_scan` adds
recursive pyval helpers (__scan/__dfold/__lfold) to the single flat `module PyCSL_Program`, expanding the
E-matching space the sibling's structural-preservation VC proves within. no_inline leaves them all in scope.
The ONLY mechanism that isolates scope = `#@ verify_module` (separate module) — memory driver-frontier-floor says
it WORSENS razor-edge goals. Soundness OK (byte-identical ⇒ sibling VC fully retained, not dropped).
Also: converting `_scan` never creates a `_subst` call site (`_scan` calls `_type_str`, not `_subst`) ⇒ byte-identity
is STABLE under the full conversion. CONCLUSION: `_scan` whole-file E-matching scale wall = genuine CERTIFIED-BOUNDARY
needing review-gated modular verification (verify_module) infra; no_inline is NOT that infra. FLAGGED for authorization.
This is the LAST named lever — GENUINE confirmed floor at 783.

## _scan verify_module isolation REFUTE (run #2, DEFINITIVELY closes the _scan lever at 783)
Spiked the mechanism the no_inline spike pointed to: `#@ verify_module` (separate-module scope isolation) on the
razor-edge. REFUTE on both halves:
- **Victim-isolation (tag `_subst_type_in_ir`)**: FAILS TO TYPECHECK — `unbound function or predicate symbol
  'wf_ir_deep'`. verify_module emits 4 modules (Shared / <G>Sig abstract-val interface / <G> provider / Program),
  but the Sig-generation does NOT hoist a function's LOCALLY-defined deep contract predicates (wf_ir_deep,
  in_emitted_fragment — defined inside the provider) into `Shared` (which has only the shallow wf_ir). So
  verify_module cannot emit a well-typed isolation of `_subst` at all.
- **Aggressor-isolation (tag `_scan`)**: not autonomously reachable — needs the banked pyval-walker device (unsaved)
  + the SAME Sig-hoisting emitter fix + whole-call-graph co-tagging ({_scan,_type_str,_sanitize_type_name}).
- verify_module is EMISSION-CHANGING (4-module split) ⇒ review-gated regardless of proof outcome.
Corroborates worker#22 precedent (tagging a razor-edge victim find_assigned_vars regressed Valid 0.23s/490K →
Timeout 30s/280M) — verify_module WORSENS razor-edge goals, as memory warned. Soundness OK (Variant V never
typechecked ⇒ no proven-by-dropping; ledger 3). REOPEN path (review-gated §10.10): Sig-generation must hoist deep
contract predicates to Shared + resolve isolated→flat cross-module calls. FLAGGED for authorization.
NOW: every named lever spiked THIS run (no_inline + verify_module both REFUTE for _scan) ⇒ EXHAUSTIVELY-confirmed
autonomous floor at 783.

## pure_ast.py — THIN reopenable seam then genuine boundary (run #3, from floor 783)
The 223-stub in-tree Python ast-clone + lexer + recursive-descent parser. Measured per parser_vein_broken
precedent (raw-AST "boundary" can be false). Finding: the cheap cursor-reader layer is ALREADY spent (40 defs
converted: peek/cur/advance/at_op/at_name/at_kw/accept_op/accept_kw + _stmt_end/_testlist_end/
_looks_like_type_alias + ~28 _Unparser visitors). Thin remaining seam: `expect_op` + `expect_kw` convert (+2,
mirror-only, whole-file proof 186/186, frame `assigns self.i` load-bearing via self.advance()). Past that:
- ~130 node-building parse methods (return_stmt/test/atom/funcdef...) depend on the ast-clone NODE MACHINERY
  `_N(name)(...)` / self.node / self._fin — mutable AST objects with settable lineno/col via a METACLASS
  (_build_nodes / _ABC.__instancecheck__ / _new / mutable_state) = genuine reflection/metaclass boundary.
- lexer `_lex` / `comments` = char-level string scanning over tokenize = string-op boundary.
- _Unparser visit_* = string-building over node fields.
FLAGGED emitter-gap (would unblock +2 more: _line_ends_with_colon, _looks_like_match): a None-initialized
`Optional[record]` LOCAL later reassigned to the record lowers None->int 0 then conflicts (`last_sig=None; last_sig=tk`
=> "type _tok but expected int"). ASYMMETRY: Optional RETURN of None works (accept_op is green); only a
None-init Optional-record LOCAL reassigned fails. Isolated emitter feature (option _tok local), flag-for-authorization.

## Module5 _scan_2d trio — CONTAINED build via COMPOSED recognizer (58cbf3e7, 781->778, run #3)
The 48-stub Module5_IREmitter is mostly raw-AST/self-mutation BOUNDARY, but the `_scan_2d` trio
(_scan_2d_in_expr/_scan_2d_in_stmt/_collect_2d_params) operates on IR DICTS (not raw ast) = pyval-addressable.
No verbatim-into-existing win (generic lowering type-failed — Set params modeled inconsistently), but a NEW
recognizer that COMPOSES three ALREADY-LANDED axiom-free primitives cleared it:
- set-ref-param void mutation `assigns result` (from find_named_expr_targets)
- set-membership READ `x in param_names` (from _test_contains_map)
- typed IR-dict dispatch + mutual expr/stmt recursion (from find_assigned_vars)
for the COMPOUND shape: "typed IR-dict descent whose set_add into a ref-param is gated by a set-membership
test, across mutually-recursive expr/stmt walkers." Emitted `let rec {expr} with {expr_list} with {stmt}
with {stmt_list}` + `let {collect}`, real typed-vs-K_dyn key readers w/ size-postcondition termination, real
Map.get membership gate, one effect-free no-ensures `val __sorted : List.list string` (sorted() over-approx,
NOT axiom). Dead in mirror (no callers) = zero coupling. mirror-only effective change (name-gated) => byte-diff 0.
BANKED DEVICE: **compose landed primitives into a new recognizer for a compound shape** — when no single
recognizer matches but every sub-pattern is already landed+proven, the composition is a CONTAINED build (ledger 3,
no new ADT/cert). META: a "no cheap verbatim win" survey verdict is NOT a boundary if the primitives exist —
measure-by-building the composition. OPS: this file needs proof timeout >=7200s (48-stub scale, ~134min).

## core_ir_semantic typing-check trio — CONTAINED build, parked-pending-device (89a1c05c, 778->775, run #3)
_check_typeddict_access / _check_namedtuple_access / _check_union_narrowing: each collects a typed-var StrSet
over func["symbol_table"].items() gated by membership (or `startswith("_union_")`), then void-dispatches to an
ALREADY-CONVERTED walker (_typeddict_walk_subscripts/_namedtuple_walk_*/_union_c8_walk). NEW composed recognizer
recognize_symtab_set_dispatch reuses: pydict .items() set-collect + StrSet Map.get membership + opaque string-op
leaf-gate (startswith) + forward-ref deferred emission. LEDGER 3 (no new ADT/cert/axiom; effect-free no-ensures
vals for the irrelevant map param + startswith leaf). _namedtuple_check_call stays \trusted (int-model leaf).
DECISIVE: in-tree comments (generic_fold.py:10445, preamble.py:2227) had EXPLICITLY parked _check_union_narrowing
"pending exactly the opaque-string-op device" — now landed. So a "parked pending device X" note + device X landing
= a reopened candidate; grep the emitter for such park-comments after banking a new device.
OPS: whole-file proof SUCCESS 1506 Valid 0 non-Valid INCLUDING the vacuity phase, cleared within 7200s (this
file's known >70min scale wall — use timeout 7200; the vacuity re-proof phase is the slow part, sometimes needs
the ensures{false} per-driver fallback if it stalls, but here it completed). Corpus-inert (TypedDict/NamedTuple/
Union in 0 corpus programs).
RUN #3 so far: 783->775 (8 conv): pure_ast expect_op/expect_kw + Module5 _scan_2d trio + this typing-check trio.

## self-state bool recognizers (_is_emit_ir_expr/_is_string_expr) — CERTIFIED-BOUNDARY (run #3, at 775)
Survey flagged them as possible opaque-self-source + bool-fold candidates; REFUTE. The core Attribute/FieldGet
branch is a TWO-LEVEL heterogeneous-dict content inspection: `_current_symbol_table.get(name)` -> record-type
string -> `_record_types.get(rec)` -> descriptor dict -> value-READS `rt["field_types"].get(attr)` and compares
`in ("ExprIR","StmtIR",...)`. `_record_types: Dict[str,Any]` whose VALUES are the discriminant (not membership)
= the documented heterogeneous value-model wall. Opaque-but-real-self-SOURCE device is INADMISSIBLE here (the
field's CONTENTS are value-inspected, so opaquing = facade = Gate-C reject; `_record_types` is a self-collection
built during transpile, so a faithful model IS the self-collection-content model = the boundary itself). Plus a
15-helper self-state DAG (_record_get_field/_field_type_of/... absent from mirror). CENSUS NOTE: `_val_is_bool` is
already VERIFIED (not a stub) — strike from trusted-pending census. NON-VACUITY LINE reconfirmed: opaque-self-source
OK for MEMBERSHIP/read-source, NOT for value-INSPECTED content.

## RUN #3 FLOOR at 775 (from 783; 8 conversions)
Reachable veins drained via NEW devices this run: pure_ast expect_op/expect_kw (cursor seam, +2); Module5 _scan_2d
trio (compose-landed-primitives recognizer, +3); core_ir_semantic typing-check trio (parked-pending-opaque-startswith
cluster, +3). Boundaries confirmed this run: self-state bool recognizers (heterogeneous value-model wall). Remaining
frontier = the same documented multi-session/review-gated boundaries (heterogeneous Dict[str,Any] value model,
raw-CPython-ast readers, self-collection-mutation-frame, while-changed fixpoints, IO/s-expr/regex/hash/eval) — the
park-notes that remain (map-element inner mutation, dict-literal element-by-element Map.set, "Part 1 shape") need
NEW emitter capabilities = flag-for-authorization, not autonomous cheap wins. META (banked this run): (1) COMPOSE
landed primitives into a new recognizer for a compound shape = contained build; (2) grep the emitter for
"stays \trusted pending device X" park-comments after landing a new device X — they are pre-identified reopens.

## ir_resolve/ir_inline cluster — 1 cheap win, rest = pydict-CONSTRUCTION boundary (run #3, 775->774)
Measured the 28-stub IR-transformation cluster. ONE cheap win: _contract_referenced_var_names (certified
contract-walker, mirror-only, duplicate/dead-but-real de-trust). The REST is a genuine boundary gated on ONE
missing emitter capability. DECISIVE evidence: generic_fold.py exposes pydict READERS only (pget_dyn/pget_list/
size_dict/pv_size/K_dyn) and ZERO copy/set/put/with-field CONSTRUCTION primitive. Every remaining stub must
CONSTRUCT-or-mutate a heterogeneous Dict[str,Any] (dict(func)+set-field, {**a,**b} merge, deepcopy, insert/append),
run a while-changed fixpoint (_recursive_methods), or do IO (open+ast.parse). 
HIGH-LEVERAGE FLAGGED LEVER (authorize-first, multi-session): a CERTIFIED AXIOM-FREE pydict copy-and-set-field /
list-insert CONSTRUCTION primitive. It would reopen a LARGE cross-file cluster at once: ir_resolve (_strip_dir_scan_
proofs, apply_inheritance/composition, _inject_functions), ir_inline (_substitute, _Inliner.*, _inline_calls),
and every other heterogeneous-dict-CONSTRUCTION boundary (Module5 record-building, functions._build_method_*_map).
The pyval value model currently READS the heterogeneous dict; the missing half is a SOUND WRITE/construct op with a
co-landing §10.5 cert (ledger stays 3). This is the single highest-leverage authorize-first build identified this run.

## functions.py ensures-map param vein — REACHABLE (was "census artifact" boundary) (ac705a0a, 774->770, run #3)
The "WhyML string-emitters / value-model wall" verdict for functions.py was a CENSUS ARTIFACT. 4 of a 5-stub
param-referencing ensures-map vein converted (774->770): _build_method_param_result / _field_param_result /
_field_param_post / _result_frame_ensures_map (#5 w/ Forall/Exists/ForallItems binder threading + propagate_frame gate).
NEW DEVICE (banked): **param-threaded ensures-map scaffold** _emit_ensures_map_scaffold_pt + _emit_lmem — reads
formal_params off the func dict as a `list pyval`, threads it through a real mutual cv/cdf/clf catamorphism, uses a
real __lmem string-membership to decide param-vs-local. KEY DISCIPLINE (the unlock): the live bodies' `rename` closure
rebuilds pydict nodes (= the pydict-construction boundary) BUT that value transform is NEVER OBSERVED by the `ensures
True` output — so the recognizer emits the FILTERED clauses VERBATIM while faithfully computing the SPINE (which clauses
kept). Over-approximation: drop the unobserved construction, model the observed filter. This is why "value-model-wall"
files still have reachable veins — the wall's construction step may be output-irrelevant. Ledger 3 (only pv_size/size_*/
pystr_eq + pinned setk). BUILD NOTE: _BMEM_KINDS entries must list ALL nested-def bases (incl. rename/refs_param) so every
hoisted sibling is suppressed via walk_ids — an un-suppressed nested def emits as generic int-model code and fails proof.
BOUNDARY: #4 _build_method_field_param_frame_ensures_map — cross-mixin blocker (body calls self._frame_trigger_term
living in expressions.py, absent from mirror functions.py; verbatim port would break mirror-sync; needs a declared
#@ requires_method/opaque-val interface). Secondary unmeasured functions.py candidates: _build_method_param_whyml_types
_by_name (nested map string (map string string) construction — needs nested-map recognizer), _compute_scope_sets
(3-StrSet-return set-collect). RUN #3: 783->770 (13 conv).

## statements.py — GENUINE BOUNDARY confirmed structurally (run #3, at 770)
No reachable cheap vein (REFUTE). Three sub-classes, all boundary:
1. ~20 CROSS-MIXIN stubs — real bodies live in expressions.py/types.py/preamble.py (_expr_to_whyml/_e/_coerce_to_int/
   _field_type_for/_const_dict_value_seq). check-self-annotate-mirror-sync.py enforces un-\trusted mirror funcs be
   byte-identical to a live func at the SAME relative path; giving these bodies = mirror-only funcs with no live anchor
   = unsound. Needs declared-interface (#@ requires_method / opaque-val) machinery.
2. 3 SELF-MUTATION collectors (_collect_string_elem_read_locals/_collect_field_decode_str_locals/_typed_local_vars) —
   write self._current_symbol_table[v]="str" (+ _typed_local_vars mutates ~8 heterogeneous self fields). **The
   output-irrelevant-construction lens does NOT apply here** — it works only when the dropped construction is a LOCAL
   value; here the write is OBSERVED self-state (callers read it) + verbatim-body can't drop it. Self-collection-
   mutation-frame boundary (ties [[trusted_val_frame_unsoundness]]).
3. ~13 STRING-EMITTERS (_seq_init_expr/_handle_*/_emit_*/_stmts_to_whyml/_emit_frame_condition) — output IS the observed
   WhyML string. Root-caused to TWO emitter-CORE string-model limits (spike REFUTE on _emit_frame_condition, the cleanest):
   (a) `x not in field_targets` over a List[str] lowers to `contains_check (str_hash_op x) field_targets` = int vs seq
   string type clash; (b) f-string literal segments lower to hashed INTS (str_concat type error). Both need either
   src/pycsl emitter-core changes (out of mirror-only scope) or forbidden source divergence.
LESSON (output-irrelevant lens LIMIT): applies to dropped LOCAL-value construction, NOT to observed-self-state writes
or observed-string-output. TWO NEW FLAGGED emitter-core levers (would reopen the ~13 string-emitters cross-file):
faithful string-membership lowering (List[str] contains without int-hash) + f-string-literal string preservation.

## functions._compute_scope_sets — 3-StrSet set-collect (9f06039f, 770->769, run #3)
Secondary functions.py candidate #1 landed via a new recognizer emitting a (map string bool)^3 triple:
params StrSet (set_add real PStr formal-param names), must-assigned (top-level stmts, const-false STOP at first
control stmt via isctrl, else set_add real gtarget), all-assigned (set_union over assigned-vars list). Real
catamorphism, real gtarget/isctrl accessors, no opaque manufacture. Ledger 3. OPS NOTE: this landed from a SPIKE
agent's WIP that ended mid-proof (completion != dead) — supervisor took over, INSPECTED the recognizer diff to confirm
non-vacuity (real set_add/set_union, not opaque val) BEFORE trusting it, then ran the full battery. A spike's dirty
WIP can be promoted IF the supervisor independently verifies Gate-C by reading the emitted recognizer, not just the proof.
#2 `_build_method_param_whyml_types_by_name` (nested map string (map string string) construction) UNMEASURED — the
flat _recognize_flat_strdictfold is single-level; needs a new nested-map-construction recognizer (flagged build).
RUN #3: 783->769 (14 conv). functions.py now well-drained: 5 landed (4 ensures-map + compute_scope_sets); residual
= WhyML-string-emitters + heterogeneous-dict construction + cross-mixin + the nested-map #2.

## preamble.py bool-fold vein — nonlocal-scalar frss twins (f511033b, 769->767, run #3)
_class_inv_refs_axiom_func + _inductive_refs_global_or_axiom_func: bool-existence catamorphism, the
NONLOCAL-SCALAR `hit` twin of _func_returns_string_seq (which used a liftable found=[False] list cell). nonlocal hit
-> || short-circuit disjunction. Opaque-but-real StrSet self-source `val __axset(self):map string bool` (populated by
\trusted _precompute_axiom_logic_funcs). #2 adds a globals-set built from ir["module_globals"] + real recursive
__ginmg list search. LESSON: the nonlocal-scalar shape MASKS a stub as boundary — the DEFAULT lowering is semantically
broken (ir->map int-leak, nested _walk->abstract val, hit severed into 2 refs) which READS as un-modelable, but a
recognizer SUPPRESSES the broken default and emits the certified catamorphism. So "default lowering is broken" != boundary
when a recognizer can suppress+replace it. preamble.py proves CHEAP (~28s wall — NOT a scale wall like core_ir_semantic).
Remaining ~22 preamble stubs = genuine string-emitter (_emit_*) + observed-construction (_scan_preamble_needs) +
self-mutation (_precompute_axiom_logic_funcs) + observed-list-output (_collect_critical_mutexes) boundaries.
RUN #3 TOTAL: 783->767 (16 conv). Devices banked this run: compose-primitives, per-index-leaf-gate, param-threaded
ensures-map scaffold, 3-StrSet set-collect, nonlocal-scalar bool-fold. Key META: "census artifact" — files classified
"value-model wall / boundary" repeatedly reopen under fresh devices/lenses (Module5, functions.py, preamble.py all did).

## Module6_WhyMLTranspiler.py — TRIPLE-MASKED review-gated package (run #3, CIE #3 blocked, at 766)
Attempting the raises-registry vein sibling #3 `_callee_implicit_exceptions` (CIE) exposed that
Module6_WhyMLTranspiler.py is RED AT HEAD (confirmed by a clean-worktree baseline proof: [-] Verification
FAILED, "type int expected string"). CIE itself is SOUND (built complete, proven 42/42 in isolation with the
blocker neutralized, mutation-tested, ledger 3) but CANNOT reach whole-file SUCCESS. Three stacked blockers:
1. **`_union__hdr_name_5` type-error [BYTE-INERT FIX READY]**: `_sig_val_from_let`'s nested `def _hdr_name`
   returns a string ternary lifted to Optional[str]=union `Arm_5_0 string|Arm_5_None`, but `_handle_ifexpr_expr`
   (expressions.py) only str-typed ternary arms under `_str_ctx` (@mutable_state OR return=="string"); a `_union_*`
   return hit neither, so `else ""` hashed to int 313406155 + arms unwrapped. FIX (characterized, byte-inert,
   verified byte-identical on all 4 Optional[str] corpus files 0946/0947/0942/0892 + pure_ast no-regression):
   add predicate `_func_ret_union_some_str()` OR-ed into the ternary `_str_ctx` gate + the IfExpr branch of
   `_is_string_expr` → wrap the whole ternary in `Arm_5_0`, emit real `""`. RISKY-CLASS (conditional-lowering) so
   FLAGGED not auto-landed; but this file had NEVER type-checked at HEAD so no solver goal had ever run.
2. **`_collect_variant_var_assigns'vc` proof-scale TIMEOUT [REVIEW-GATED]**: once the type error clears, exactly
   one goal times out (23.5s/5.59M steps) — recursive pydict/pyval fold variant-decrease E-matching saturation
   (isolation_spike_not_whole_file terminus; needs modular verification, NOT a timelimit bump). types.py-sibling,
   byte-inert to both CIE and the union fix.
3. **SOUNDNESS FLAG**: this file (RED at HEAD, never solver-proven) has ~3 contracted-and-NOT-trusted
   (claimed-CONVERTED) methods whose "verified" status is NOT backed by any passing whole-file proof = illusory-
   verified (ties [[trusted_val_frame_unsoundness]]). Needs investigation (were they committed pre-bug, or is this
   a latent gate hole?).
NET: CIE (#3) + the whole ~17-stub Module6_WhyMLTranspiler.py file are gated behind this package. FLAGGED
authorize-first: land the byte-inert union-arm fix + resolve the proof-scale timeout (review-gated modular
verification) + audit the 3 illusory-verified methods. Raises-registry vein autonomous yield = #1 only
(_callee_raised_direct, landed fb3d60b3); #4 _callee_raised_in also lives in the try/except walk (own recognizer)
but any Module6-file sibling shares the file blocker. DECISIVE OPS LESSON: when a build's whole-file proof won't
go green, prove the file at CLEAN HEAD in a worktree FIRST — a RED-at-HEAD baseline = masked blocker (not your bug).

## _try_local_decl_kind — CERTIFIED-BOUNDARY (or-int-collapse caller coupling) + RUN #3 FLOOR at 766
Raises-registry vein sibling #2. Body is sound (subset of the converted _first_assign_kind; _record_types is
MEMBERSHIP-only not value-inspected; _rhs_yields_map is a verified anchor). REFUTE via CALLER COUPLING: the verified
caller _handle_try_stmt passes the arg as `_first_assign_value_ir(...) or _first_assign_value_ir(...)`. The emitter
models Python `or` in body context as an INT truthiness collapse (expressions.py:1830-1834: `A or B` -> `if (A<>0)||
(B<>0) then 1 else 0`). Once the converted callee requires an `emit_ir` param, the caller's `or`-int no longer
type-matches -> whole-file type-fail "int expected emit_ir". Converting the feeder doesn't help (the wall is the
or-lowering, not the feeder's trustedness). FIX = NEW emitter capability (value-preserving short-circuit or over
emit_ir + emit_ir truthiness predicate) touching the and/or lowering every corpus file depends on = byte-diff-risk,
authorize-first. LESSON: a verified caller passing the arg through an `and`/`or` collapses it to int; converting a
callee to need a structured param then type-fails the caller = a distinct CALLER-COUPLING-via-truthiness-collapse
boundary class.

RUN #3 CONFIRMED FLOOR at 766 (from 783; 17 conversions). Reachable veins all mined: pure_ast cursor (2), Module5
_scan_2d (3), core_ir_semantic typing-check (3), ir_resolve (1), functions.py ensures-map + compute_scope_sets (5),
preamble.py bool-fold (2), stmt_control_flow raises-registry #1 (1). Boundaries this run: statements.py (cross-mixin/
self-mut/string-emitter), self-state _is_emit_ir_expr (heterogeneous), ir_inline (construction/fixpoint), array_var
(while-fixpoint), _try_local_decl_kind (or-collapse coupling). Residual ~730 = raw-ast (~111), proof2why3 (~140),
IO (~67), string-emitters (~30), opaque-stdlib (~30), all boundary/review-gated. AUTHORIZE-FIRST flagged levers (each
reopens a cluster): (a) pydict copy-and-set-field construction primitive; (b) faithful string-membership + f-string-
literal preservation; (c) getattr-self-mutable-field; (d) cross-mixin declared-interface; (e) value-preserving or/and
over structured types; (f) Module6_WhyMLTranspiler triple-masked package (byte-inert union-arm fix + proof-scale
timeout + 3 illusory-verified methods audit).

## proof2why3 canonical.py/normalize.py — GENUINE BOUNDARY (run #3 periodic re-measure, floor 766 HOLDS)
Anti-false-floor re-measure of the SExp/Term-walker residual. REFUTE, 0 cheap wins. Nuance: the Term ADT IS modeled
(ir.py frozen dataclasses Var/App/BinOp/Forall/...); Term-CONSTRUCTION works; 2 Term->Term rewriters already verified
(_flip_comparisons, alpha_normalize via recognize_term_isinstance_transform, generic_fold.py:27054). So NOT a
construction boundary — a RECOGNIZER-GRAMMAR boundary. The 10 remaining canonical.py Term-rewriters each use a
capability OUTSIDE that recognizer's grammar: compound isinstance+field guards (isinstance(t,BinOp) and t.op=="->"),
2-param / Dict-mapping signatures, side-condition arrow-chain CONSTRUCTION (mk_arrow_chain + fresh-BinOp comprehension),
nested closures / while-spine loops, string-fn field transforms (_camel_to_snake(t.name)), cross-ctor value-guarded
rewrites with subscript (App->BinOp on t.head=="iff", t.args[0]). SPIKE _iff_app_to_binop = REFUTE (canonical.mlw:127
"type binop but expected int" — recognizer rejects the cross-ctor+field-guard+subscript shape, falls to Term=int model).
The 9 string-rewriters (2 canonical + 7 normalize) = char-level regex/str->str (re.sub/re.split) = str_to_int-parser
boundary. FLAGGED authorize-first: term-transform recognizer grammar extensions (compound-guard arms / subscript-positional
field builder / cross-ctor rebuild / arrow-chain-construction builder / 2-param+Dict threading) + faithful string-op model.
FLOOR 766 DOUBLY-CONFIRMED (broad survey + this targeted deep-spike).

## Constructor vein — 11 __init__ harvested (fb92b638 + c5852e8d, run #3, ->755)
The floor-confirmation re-measure of Module1_Ingestor (raw-ast class) unexpectedly surfaced a CROSS-FILE
CONSTRUCTOR VEIN: a class's `__init__` is convertible EVEN in a raw-ast/boundary file because the constructor
only FIELD-INITS — it does NOT read the raw-ast node it stores (_Target stores an opaque `node` unread). Harvested
11 total (Module1_Ingestor 3 + a cross-file sweep 8) matching the accepted _Tok/PyCSLError precedent: verbatim
field-init + `#@ requires True / ensures True / assigns \nothing`, lowering to a record type-decl with NO standalone
__init__ VC. WEAK-CONTRACT (str fields int-leak, no behavioral content) — legitimate de-trusts by precedent, recorded
honestly per VALUE-not-count (NOT wall breaks). Files: Module1_Ingestor(3), pure_ast(1), Module3_Weaver(2), Module5(1),
ir_inline(1), ConcurrencyChecker(1), parser.py(1), pycsl.py(1). SKIP criteria (left \trusted): constructor needs a
PRECONDITION to establish a class invariant (_ContractParser EOF-inv, pure_ast._Parser i<len — can't prove under
requires True); setattr/zip/raise (pure_ast.AST); curated non-verbatim Tier-5 stub (PyCSLToJSONEmitter); WhyML
name-collision (Comment.text/_Unparser). BLOCKED: Module6_WhyMLTranspiler's __init__ (behind the file's RED-at-HEAD
masked blocker). OPS: Module5_IREmitter whole-file proof ~76min (use timeout >=6000s). LEVER: a broader
constructor sweep is a count-reduction option but weak-contract — this run harvested the clearly-reachable ones;
further constructors need preconditions/emitter-work.

## RUN #3 FINAL: 783 -> 755 (28 conversions) — by far the strongest run.

## Module3_Weaver _const_int — isinstance-typed-record FAITHFUL reader device (2ad3f29e, 755->754, run #3)
ANTI-FALSE-FLOOR HIT at "confirmed floor" 755 — a periodic re-measure of Module3_Weaver (raw-ast dataclass weaver)
found _const_int reachable. NEW DEVICE (banked): **single `isinstance(x, <TypedRecord>)` guard + typed-field read +
scalar/int/bool return** slips through the raw-ast boundary — it's a REAL typed-record reader, not a raw-CPython-ast
walk. Verbatim body + REAL value contract `ensures \result == node.value` (NOT weak-contract like constructors —
mutation-tested: +1 REFUTES). The isinstance(Number) typed-record guard + int() truncation faithfully model
int(value)==value. Mirror-only, coupling-safe. This device may generalize to OTHER isinstance-typed-record+scalar-return
methods across the raw-ast files (Module5_IREmitter/Module2_Parser/etc.) — worth a targeted sweep.
BOUNDARY (measured): _extract_happy_properties — `contracts_map[line]=kept` in-place MAP-PARAM mutation has no
caller-visible by-ref frame ("in-place mutation of dict/set parameter out of scope") = emitter/tool-capability class;
needs a src/pycsl dict/set-param-mutation-frame (ties the pydict-construction-primitive + getattr-self-mutable-field
flagged levers). Module3_Weaver aggregate: ~34 boundary (raw-ast visitors + dataclass-reflection _subst_var/_dc_replace
+ output-record-construction + cross-module + string-op) / 3 constructors (done) / 1 isinstance-reader (_const_int, done).
META: the anti-false-floor periodic re-measure has now paid off THREE times past a "confirmed floor" (constructor vein,
then _const_int) — KEEP MEASURING in a funded window; each raw-ast/boundary file may hide a thin typed-reader/constructor seam.

## isinstance-reader device is INT-ONLY — _csl_to_str CERTIFIED-BOUNDARY (run #3, floor 754)
Correction to the isinstance-typed-record-reader device: it works ONLY for INT-returning readers. The CSLNode ADT is
modeled as opaque `int` with int-only auto-generated field accessors (get_name/get_op/get_value all :int) + opaque
isinstance (isinstance_op 0 0, constant args). `_const_int` proved ONLY because it's int->int (`\result == get_value
node`, faithful for the VALUE — mutation-tested, stands). `_csl_to_str` (recursive CSLNode->str) REFUTES: string-typed
field reads (get_name/get_op needed as string) type-fail against the int accessors ("type int expected string",
Module2_Parser.mlw:1566). The str-build lowering itself is fine (str_of_int/str_concat) — the wall is purely the
opaque-int field-accessor model. FIX = authorized emitter build: (a) per-field typed accessors off the isinstance
narrowing (get_name->string), OR (b) CSLNode-as-genuine-Why3-variant + route through recognize_term_string_pp
(generic_fold.py:28069, but that's 2-param (term,prec) over a variant spec["ctors"] — CSLNode is 1-param, no variant).
Both multi-session src/pycsl. FLAGGED authorize-first (typed-record-field-accessors / CSLNode-as-variant), ties the
canonical.py Term-construction vein. So the isinstance-reader vein = _const_int ONLY (int-returning).
FLOOR CONFIRMED at 754 (run #3, 29 conversions from 783).

## pycsl.py — ALL BOUNDARY (run #3 anti-false-floor confirmation, floor 754 SOLID)
Periodic re-measure of the 34-stub CLI file: 21 subprocess/file-IO (unmodelable) + 12 record-processors, ALL boundary.
The ONE reachable model-addressable reader (`_record_is_valid`, bool over the proof-record pydict) is ALREADY converted.
`_record_answer` (Dict[str,PyVal]->str) REFUTES at the documented int-vs-string ceiling (pyval read is int-modeled, str
return type-fails). Everything else = str-build (_synthesize_*), container CONSTRUCTION (_record_key->Tuple, _json_goal
_records->List[dict], _merge/_finalize), char-level str-parse (_parse_goal_blocks), nested-closure (_is_false_goal),
or subprocess/IO. The campaign already optimally split reader(bool, converted) from value-layer(str, boundary).
FLOOR 754 SOLID: three consecutive periodic re-measures (_csl_to_str opaque-int-accessor, _extract_happy_properties
dict-param-mutation, pycsl.py str-construction+IO) all hit GENUINE CAPABILITY BOUNDARIES — the reachable autonomous
frontier is exhausted. RECURRING CEILING across the tail: str-returning readers over int-modeled records/pyval need
the typed-record-field-accessor emitter build (authorize-first lever #7); container/record CONSTRUCTION needs the
pydict-construction primitive (lever #1). RUN #3 DEFINITIVE FLOOR: 754 (29 conversions from 783).
## for-loop tuple-unpack (pytuple-projection form) — CERTIFIED-BOUNDARY 2026-08-15
- WALL: `for a,b in <List[Tuple[τ,τ]]>` unpack targets emit UNBOUND.
- SPIKE: PASSED (loop proves trivially; emitter already emits pytuple record + skeleton, only `.fieldK` bindings missing).
- BUILD: binder built + proven end-to-end (no new axiom). BUT make-or-break END-TO-END gate FAILED: census of 721 stubs → 0 consumers iterate a `List[Tuple]` param / record-literal local (all `.items()`/`zip`/`enumerate`/`Set`/const/opaque-cross-call). REVERTED (unused-facade).
- LESSON (trigger-tested): a proven binder with ZERO trusted consumers is a Gate-C reject, not a conversion — ALWAYS census consumer COUNT before building a shape-specific binder (the spike proving is necessary but NOT sufficient; the make-or-break is consumer existence, not loop provability). Bank the cap; do not land it.
- NEXT VEIN: items-over-`Dict[str,str]` binder (native `map string (option string)` via keys_get/values_get over-approx) — SEPARATE build; measure un-co-blocked consumer count first.

## items-over-Dict[str,str] (native-map items-binder) — THIN VEIN, no-go 2026-08-15
- MEASURED (read-only census, no build): 62 `.items()`-consuming trusted stubs; only 1 has a faithful-scalar-value receiver annotation (`substitute`, Dict[str,str]) and it is multi-blocked (recursive Term-ADT walk + dict-comp CONSTRUCTION + raise); ~54 others are Dict[str,Any]/hval/record-info (the deep generic-dict wall). UN-CO-BLOCKED consumer count = 0.
- VERDICT: below the >=2 escalation threshold -> NOT escalated. Same shape as the pytuple precedent (provable binder, empty consumer population).
- LESSON (reinforces the pytuple lesson): the tuple-unpack/items FRONTIER is mined out for shape-specific binders — BOTH the pytuple-projection and native-map-items binders have 0 un-co-blocked consumers. The residual .items() consumers are co-blocked by DEEPER capabilities: recursive variant-ADT walks (Term/AST), dict-comp CONSTRUCTION (builds a new filtered map, ≠ read-only keys_get/values_get over-approx), heterogeneous Dict[str,Any] int-erasure, string/regex facades, nested-def closures. The next real veins are these deep multi-session capability builds, NOT another binder.

## pydict copy-and-set / dict-comp CONSTRUCTION (#2) — CERTIFIED-BOUNDARY (0 sole-blocked) 2026-08-15
- Primitive faithfulness CONFIRMED (Map.set + filtered fold prove under Z3, no axiom). Half already EXISTS: `d[k]=v` lowers via `map_update_some` (statements.py:1217, `ensures result=Map.set m k (Some v)`). Only general dict-comp / dict(d,**u)/.copy/.update / method-param frame missing.
- CONSUMER CENSUS: 696 mapped stubs, 99 construct maps, 74 use a missing shape, **0 SOLE-BLOCKED**. Best candidate `_render_callee_condition` has 3 other blockers (Any->int-erased callee, bare `with Exception` raise, `_in_spec` unbound-frame L3-tc gate). substitute co-blocked by Term walk; _collect_* refuted; _extract_happy_properties needs method-param frame + CSLNode ADT.
- VERDICT: GATE-C REJECT (provable, 0 consumers) — filtered dict-comp is a FOLLOW-ON of wall #1, build demand-driven after it.
- INCIDENTAL emitter findings banked (§5.3 of response): (i) `writes { self._in_spec }` emits UNBOUND for a mixin where _in_spec isn't a declared @mutable_state field -> whole-file L3-tc gate on conversion (per-mixin field-decl bug, narrow); (ii) `Optional[str] is not None` lowers via `str_hash_op != 0` (int-hash faithfulness leak).

## FRONTIER READ 2026-08-15: THREE consecutive contained-capability escalations = 0 sole-blocked consumers
- pytuple-projection binder, native-map-items binder, pydict-construct primitive: ALL proved, ALL 0 sole-blocked consumers. The 721 floor is a COMPOUND-BOUNDARY: residual stubs are MUTUALLY co-blocked (each needs 2-5 deep capabilities simultaneously — Term-ADT walk + dict-comp + Dict[str,Any] faithful-value + string-facade + method-param frame). No single contained build converts anything.
- ONLY unmeasured contained lever left: wall #1 (Term/AST recognizer-grammar arms, per-arm additive). Measuring its consumer-existence is the LAST contained-lever check before declaring compound-boundary floor.

## Term/AST recognizer-grammar arms (#1) — CERTIFIED-BOUNDARY (0 sole-blocked) 2026-08-15
- Term cluster ALREADY drained (recognize_term_isinstance_transform built 2026-07-24; _flip_comparisons was the ONLY clean member; mk_arrow_chain/flatten/free_vars leaves converted in ir.py). Every remaining transform has >=2 disjoint blockers (compound isinstance guards + cross-ctor App->BinOp rebuild + list-comp-term-build + term_eq/F3F4-theory + nested-def + proof-scale timeout). Cross-module co-blocker: mk_arrow_chain/flatten re-stubbed as opaque int vals in canonical.py.
- canonical.mlw:127 = record<->variant int-collapse type clash (unrecognized transform falls to record/int value model; BinOp record literal vs int-expected). Fixable-in-principle grammar gap, NOT single-arm.
- VERDICT: CERTIFIED-BOUNDARY. Cluster reachable only via multi-cap review-gated build (term-theory F3/F4 emitter + term_eq + list-comp-term + map-param + cross-module term-typed imports).

## FLOOR DETERMINATION 2026-08-15: contained-lever frontier EXHAUSTED at 721 (4x0)
- FOUR contained capabilities measured, ALL 0 sole-blocked consumers: pytuple-projection binder, native-map-items binder, pydict-construct primitive, Term recognizer-arms. Each is capability-PROVABLE but consumer-EMPTY at single-capability granularity.
- ROOT CAUSE: the residual 721 stubs are MUTUALLY co-blocked — each needs 2-5 deep capabilities at once (Term-theory + dict-comp + Dict[str,Any] faithful-value + raw-ast-variant + string-facade + method-param frame + nested-def). No SINGLE contained build converts anything; only a CLUSTER of caps landed together converts a mutually-co-blocked batch.
- REMAINING = review-gated multi-session COST/SCALE builds (NOT correctness floors, per feedback_cost_scale_not_floor): #6 pyval-heterogeneous root (~97, existing ADT to EXTEND), #5 raw-ast-as-variant (~81, new ADT+cert), Term-theory cluster. Next per funded-window doctrine: SPIKE the highest-leverage deep vein (measure-before-build on the EXISTING certified pyval ADT = lower-risk than a new cert) before flagging the risky cert-build.

## _callee_raised_in — CERTIFIED-BOUNDARY (correctness/caller-coupling) 2026-08-15
- Sits on a MODEL SEAM: already-converted callee _callee_raised_direct is `map string bool` (non-enumerable); verified caller _handle_try_stmt consumes _callee_raised_in as `seq string` (snapshot/arr_union). Modeling on collect_escaping_exceptions emits map-string-bool -> type-clashes the VERIFIED caller (out of scope to edit); staying seq-string -> the core Try set-difference `{e in inner : not any(handler_catches(b,e) for b in exc_type.split("|"))}` needs set-diff/filter/split primitives absent in the seq-string plane -> opaque = Gate-C facade.
- CORRECTNESS wall (not cost/scale). Reopen = flagged multi-method retype to ONE plane (convert _handle_try_stmt + collect_escaping + _callee_raised_direct to map-string-bool) OR a faithful enumerable seq-string set-primitive family. Both review-gated.

## FRONTIER at 718 (2026-08-15, session 736->718 = 18 conv): autonomous single-stub floor; residual = review-gated campaigns
- ALL banked-device + spike-able single-stub veins drained. Every residual lead SPIKED/MEASURED to a specific review-gated MULTI-METHOD campaign:
  1. self-state-as-key-iterable-pydict retype (unlocks _module_binding_names/_collect_shared_symbol_decls; BROAD, sibling-regression risk)
  2. lifted-def catamorphism / nested-def re-coupling (unlocks _collect_str_decode_locals + _collect_* family; Module5 decouples captured accumulator into abstract val = unsound-masked)
  3. seq-string faithful set-primitive family OR map-string-bool plane consolidation (_callee_raised_in + Try cluster)
  4. raw-AST Ingestor/CSL-Weaver IR-builder modeling (_build_function_ir/_csl_*/_py_expr_*/_match_pattern_to_ir; hardest)
- 3 "review-gated/new-device" verdicts REFUTED this window by spiking contained paths (termination-VC, type-string producers, self-ref-map-key-enum) => always spike before flagging; but these 4 are now spike-confirmed as genuinely multi-method/review-gated.

## self-state field retype to key-iterable pydict — WALL (CERTIFIED-BOUNDARY) 2026-08-15
- De-risk gate on the most-bounded target (_module_constants): retype Dict[str,str]->Dict[str,Any] makes the value non-string, breaking the VERIFIED reader _handle_var_expr at L3-tc (`_whyml_string_literal(_cv)` + f"({_cv})" expect string). String-valued self-fields FEED verified string-consuming readers -> a retype regresses the sibling at typecheck (harder than a proof failure).
- SECOND obstacle: the target _module_binding_names's real block is `self.ir = json.loads(json_ir)` — the heterogeneous Dict[str,Any] IR ROOT, NOT modeled as a record field at all. Retyping the two small fields is necessary-not-sufficient.
- The machinery (hval_keys_get/values/as_map) EXISTS; the obstacle is caller-coupling regression + the unmodeled self.ir IR-root.
- VERDICT: WALL. Reopen = model self.ir as pyval (reuses existing cert, NO new cert) BUT it's read by many methods incl. verified _handle_var_expr -> a broad multi-method retype campaign (regression-heavy), OR the string-field-plane needs consistent retype of every string-consuming reader.

## FRONTIER at 717 (2026-08-15): autonomous no-new-cert / no-verified-regression frontier EXHAUSTED (19 conv this window, 736->717)
- Every remaining lead MEASURED to: (a) verified-method-regression retype (self-field, map-string-bool consolidation) — breaks siblings at L3-tc; or (b) big review-gated value-model campaign (self.ir heterogeneous IR-root modeling [reuses pyval cert but broad multi-method regression-heavy retype]; raw-AST-as-variant ADT for _py_stmts_to_ir/_process_dependency [likely new cert]).
- These are the DOCUMENTED deep walls (frontier_exhaustion_map / isolation_spike_not_whole_file "authorize first"). NOT clean autonomous increments.
- 4 boundaries REFUTED this window by spiking contained paths; the remaining 3 are now spike-confirmed as genuinely multi-method/regression-heavy/new-cert.

---

## 2026-08-26 — 96h run: STALE-WALL lesson (Gate S-lesson, PASS + carve-out into the driver skill)

**Wall it came from:** `fav-structural-robustification` (the `find_assigned_vars` structural-variant
rewrite, queued as ladder item #1 and pre-authorized as flagged build (a) in the 2026-08-26 authority
amendment).

**The `L`-input that revealed the divergence:** Gate R's independent fable review ran the whole-file
proof of `ir_scanner.py` and reported **409 `_collect_mutations` subgoals and 71
`find_iteration_mutations` subgoals all proved**. A `\trusted` stub emits as a bodyless `val` and
therefore has NO subgoals of its own — so the proof output itself was proof that the target was no
longer trusted. Confirmed directly:
`grep -cF '#@ \trusted' src/self-annotate/src/module6_whyml/ir_scanner.py` -> **0**.

**What was actually true.** The wall HAD been broken — by the heterogeneous value-model root, in a
later window: `c6557971` (`_collect_mutations`, 796->795), `fdbccc77` (`find_iteration_mutations`,
795->794), summarized in `4700f558`. At `0eb601ca` — the commit that recorded "FINAL FLOOR CONFIRMED
@ count 804" — `ir_scanner.py` still had 4 trusted markers. Nobody retired the `wall-lessons` entry,
so the reopening chain `no_inline (#18 REFUTED) -> verify_module-Sig-fix (#21) -> verify_module
(#22 REFUTED) -> "the ONLY remaining path is find_assigned_vars structural robustification"` kept
propagating a reopening for a wall that no longer existed, and carried it all the way into a
standing user authorization.

**Gate S-lesson classification: DEFER-TO-ORACLE, validity test PASSES.** The lesson is "on case S
(about to escalate a wall) take the `L`-sanctioned action (grep the target's trusted status)". Does
`L` actually distinguish S? Yes, decisively and in one command — `grep -cF '#@ \trusted' <mirror>`
separates "still trusted" from "already converted" with no judgement involved. So it is written as a
rule, not carved.

**The rule (also carved into `self-tcb-reduction-driver` SKILL.md Gate W as the FRESHNESS
PRECONDITION, because a behavioral rule that lives only here does not bind the next run):**
before escalating ANY wall, re-verify the target is still `\trusted` at HEAD. If it is not, the item
is **REFUTED AS STALE** — payoff 0, NOT a CERTIFIED-BOUNDARY — strike it, record the commit that
actually converted it, and advance the same turn. Generalized: **re-measure, never inherit** — this
applies to every count and every target a backlog entry carries. (The same window found the running
`\trusted` count had drifted too: commit messages said 687 while the canonical
skill-§18 command said 675, because a prior worker had silently widened the scope.)

**What it cost, and what saved it.** A wall report and a full fable review were spent on a
zero-payoff item, and the RISKIEST of the three amendment-authorized builds was queued first. Gate R
earned its keep exactly as designed: the reviewer refuted the report's premise from an independent
evidence base instead of endorsing its prose. A prose-only review would have waved it through and the
build would have re-emitted an already-proven function for nothing.

---

## 2026-08-26 — 96h run: THREE lessons (Gate S-lesson applied to each)

### (1) MOVING-DENOMINATOR — the `\trusted` count is not net TCB. **PASS, write as a rule.**
*Wall it came from:* the L2 `csl-dispatch-expansion` review, which found the mirror's `_CSL_HANDLERS`
stale at 77 vs live 79.
*The `L`-input:* `bin/check-self-annotate-mirror-sync.py` documents that the mirror is intentionally
a SUBSET and that a live function missing from the mirror is NOT drift — *"≈147 are, off the
verification path"*. Measured with `getting-better/measure-unmirrored-surface.py` over detached
worktrees: **287 (@0eb601ca, trusted 804) -> 362 (@HEAD, trusted 672)**, mirrored population flat
(1299 -> 1301). So `\trusted` fell 132 while off-path live functions rose 75.
*Validity test:* does `L` distinguish the case? Yes — the script is a direct, seconds-long
measurement, and it disagrees with the documented figure by ~2.5x.
*Rule:* **the campaign converts stubs largely BY BUILDING new emitter capability, and that new live
code is itself unmirrored, unverified and uncounted.** Quote the `\trusted` count WITH the
unmirrored-live count, and never report `-N trusted` as `-N net TCB`. Demonstrated concretely on this
window's own `dfed484b`: `_call_record_constructor` is mirrored, but `_bind_listfield_from_seq` and
`_call_irnode_constructor` are live-only. Changing the headline metric is the USER's call — the
driver's duty is to report the pair, not to redefine the target.

### (2) CONSTANT-TABLE BLIND SPOT — the fidelity gates cannot see class-level tables. **PASS.**
`self-annotate-mirror-check.sh` compares `(kind, name, n_params)`; the sync check compares
un-`\trusted` function BODIES. **Neither inspects class-level constant tables**, so a mirror can
carry a stale dispatch table indefinitely with both scripts green — exactly what `_CSL_HANDLERS`
(77 vs 79, `NestedSubscript` / `SubscriptFieldAccess` missing) has been doing.
*Rule:* any build that REFLECTS a class-level constant table into WhyML must diff that table against
live as an EXPLICIT extra gate. The standard battery will not catch it, and with `ensures {true}` a
wrong mapping is also invisible to Gate C — so a hard-coded table in an emitter template is
categorically unacceptable (the reviewer's point, and it is right).

### (3) COUNT THE CLEARANCES BEFORE PROMISING A YIELD. **CARVE-OUT, not kept whole.**
*Candidate lesson as first written:* "a census of stubs sharing one blocker gives the lever's yield."
*Refuted by:* the L9 build. A census found 15 stubs blocked by the Tier-A list-field restriction, and
the impl plan asserted `_parse_for_block`'s "return route already works". **That premise held for NO
target, including that one** — with no annotation the return type came out `int`, and the conversion
also needed a mirror-only `-> ForExpand` annotation plus an `_emit_ir_seq_locals` element-type signal
(Module 5's `seq_value_types` only ever records `"string"`).
*Carved rule:* a shared-blocker census gives an **UPPER BOUND**, never a yield. Before quoting a
number, enumerate every clearance each target needs — for a record-construction conversion that is
**three**: the field binding, a return-type route, AND a truthful frame (`assigns \nothing` over a
body that mutates self-state is a FALSE FRAME, wall-lesson (f), and must be REJECTED not patched).
State the bound as a bound.

### (4) 2026-08-26 — ANTI-FACADE GATE FALSE GREEN: `check-emitted-vacuity.py` without `--emit`. **PASS.**
*How it was found:* the driver ran the vacuity gate immediately after the sanctioned
`find src/self-annotate/src -name '*.mlw' -delete` cleanup and got
`[+] no NEW erasure (0 known param-erasures gated; 0 input-blind methods)`, **EXIT=0**. With
`--emit` and a real population of 52 the SAME tree gives **EXIT=1** with 6 known gated erasures,
2 input-blind methods, and 1 un-ledgered erasure.
*Validity test:* `L` distinguishes the two runs decisively — same tree, opposite verdicts, the only
difference being whether a population existed.
*Rule:* **the script REUSES existing `.mlw` and does not emit unless told to.** Always invoke it as
`bin/check-emitted-vacuity.py --emit` and ASSERT the emitted population == 52. This is lesson (k)
("a 'no differences' gate is meaningless without its POPULATION count") recurring on the
anti-facade gate specifically — the gate whose whole job is to catch a body that proves while
ignoring its inputs. A green from an empty population is the worst possible false green here.
*Corollary, and the reason this is written down:* the driver had ALSO propagated "vacuity exit 0"
into two executor briefings, having inherited it from an agent report without re-measuring — the
same day the "re-measure, never inherit" rule was banked. An executor caught it and reported the
real baseline. **Baseline facts in a briefing must be re-measured by the driver before being
handed down, exactly like agent claims.**

---

## Lesson (q) — a `writes` clause has TWO jobs; dropping it from a bodyless `val` silently STRENGTHENS the caller's assumption

**Wall it came from:** the `proof2why3` cursor nest (L13). Found while closing the blocker set, not by
looking for it.

**The divergence `L` revealed.** `module6_whyml/functions.py` emitted a method's `#@ assigns self.f` as
a WhyML `writes { self.f }` clause ONLY when `not emit_as_val` — i.e. only for a CONCRETE `let`. The
in-source rationale was sound as far as it went ("so Why3 CHECKS the frame against the body — a wrong
or `\nothing` assigns on a mutating body FAILS: the soundness fix"). But a `writes` clause does two
things, and only one of them was being reasoned about:
  1. it CHECKS the frame against a body — meaningless for a bodyless `val`, which is why it was skipped;
  2. it DECLARES the frame to CALLERS — and a Why3 `val` with NO `writes` is assumed to write NOTHING.
So every `\trusted`/`\abstract` stub declaring `#@ assigns self.f` handed its callers an assumption
STRICTLY STRONGER than the mirror's own contract: not "may assign self.f" but "does not touch self.f".

**Trigger test (this is an ignore-signal lesson: "a missing writes on a val is harmless") -> REJECT,
and the replacement rule is PASS.** Perturb X = restore the declared frame; does `L`'s verdict move?
DECISIVELY YES. `getting-better/cursor-nest/trusted-frame-oracle.mlw`, Alt-Ergo 2.6.3: for a trusted
stub with `ensures True` + `assigns self.i`, the caller's `ensures self.i >= \old(self.i)` is
**Valid as emitted** and **Unknown (fails) once `writes { self.i }` is restored**. Three landed
Module2_Parser conversions were proving frames and a loop VARIANT on that false premise, the worst
being `_parse_lock_order`, whose TERMINATION rested on assuming the sub-parser does not move the cursor.

**The rule.** Whenever a contract clause is emitted CONDITIONALLY on "is there a body to check it
against", ask separately what that clause tells CALLERS. If the answer is "something", the condition is
wrong. Generalizes beyond `writes`: any clause that is simultaneously an obligation and an assumption
must be emitted on the assumption side unconditionally.

**Carve-out (what is NOT the lesson).** An EMPTY frame is genuinely different: `writes { }` on a `let`
CHECKS that the body writes nothing, while on a `val` it says exactly what a missing clause already
says. Suppressing it on the val path is correct AND is what keeps the fix corpus byte-inert. So the
rule is "declare a NON-EMPTY frame unconditionally", not "always emit the clause".

## Lesson (r) — gate the re-proof set by an EMISSION DIFF, not by "every file that could be affected"

An emitter change to a gated path looks like it needs every file matching the gate re-proved (here: all
11 `@mutable_state` mirrors, including the two slowest, one of which exceeds 9 minutes). EMIT FIRST and
DIFF: emitting all 52 mirrors in the base and patched worktrees showed exactly **8** files change, and
that the change is a PURE ADDITION of 231 `writes` lines with nothing removed and nothing incidental.
The 44 unchanged files provably need no proof. This is cheaper AND stronger than a blind sweep, because
the diff itself is evidence that nothing unintended was emitted — a blind all-green sweep would not have
shown that. **Do the emission diff before the proof sweep, always.**

## Lesson (s) — a hand-written spike can OVERSTATE a capability gap by modelling a construct differently from the emitter

The cursor-nest spike modelled Python's `while True: ... break` with a boolean flag, which forced a
LEXICOGRAPHIC loop variant (a plain one FAILS `Loop variant decrease` on the flag-clearing branch), and
that was written down as a required new capability. The EMITTER does it differently and better:
`while True/break` lowers to `try while true do ... raise PyCSL_Break ... done with PyCSL_Break -> ()`.
The break path raises before the end of the body, so it carries NO variant obligation and a PLAIN
`#@ loop variant` suffices. The "capability" did not exist. **Before naming a gap from a spike, emit the
construct and read what the emitter actually produces.** A spike proves the TARGET is reachable; only the
emitter tells you the DISTANCE to it. Applying this to the same wall turned a 7-item gap list into a
4-item one: `raise` in a value-returning method, `int(s)`, seq accumulation, `\old` in a loop invariant,
mutual recursion, `let rec` and the variant were ALL already supported.

## Lesson (t) — two silent-erasure hazards in the `#@` surface, both measured

1. **Loop annotations placed INSIDE the loop body are SILENTLY DROPPED.** `#@ loop invariant` /
   `#@ loop variant` must precede the `while` line. Put them after it and the emitted loop has no
   invariant and no variant, with NO diagnostic — and a loop with no variant then fails (or worse,
   silently weakens) the termination story. Cross-check against a known-good example, e.g.
   `_parse_lock_order` in the Module2_Parser mirror.
2. **`#@ \variant (` with a LEADING PAREN is parsed as the `(expr, ordering)` structural-variant form**
   and errors with "expected name". Write a lexicographic-by-encoding measure with the multiplier first:
   `#@ \variant 16 * (\length(self.toks) - self.pos) + <level>`.

## Lesson (u) — a gate result committed without the code it gates is a CLAIM, not an increment

The L14 frame-soundness fix was reported as landed by two consecutive relaunches. It was not. The
window that built it committed the ORACLE (`trusted-frame-oracle.mlw`) and a nine-line progress-log
entry reciting green gates — corpus byte-diff 0, fidelity identical, ledger held — while the actual
three-file patch existed ONLY in a detached worktree under the session scratchpad, staged and never
committed. HEAD still contained `if (is_method and not emit_as_val`, i.e. the bug, verbatim.

The failure is seductive because the progress log READS like completion: it is specific, it cites
populations, it names the repaired functions. Nothing in it is false. It simply describes work that
exists somewhere other than the repository.

**The rule.** Before believing any prior window's "fixed/landed/green", READ THE SOURCE AT HEAD for
the specific line the fix changes. `git show HEAD:<file> | grep <the changed condition>` costs
seconds. A commit that touches only `getting-better/` has, by definition, changed no behaviour —
so a soundness fix whose commit shows `1 file changed` in the docs directory did not land.
Corollary for the writing side: commit the CODE and the EVIDENCE in the same commit, never the
evidence first.

## Lesson (v) — a frame is about the FINAL state, so an assignment-statement detector over-reports

Auditing the mirror for `\trusted` stubs whose declared `#@ assigns` understates their live writes,
an AST scan for "does the body contain `self.f = ...`" returned 20 hits. Only ONE was real. Two
whole classes of false positive:
  1. **SAVE-RESTORE.** `_saved = self.f; self.f = x; ...; self.f = _saved` assigns the field twice and
     leaves it unchanged. A Why3 `writes` clause bounds which fields may DIFFER IN THE FINAL STATE,
     not which are transiently touched, so omitting such a field is SOUND. (`expressions.py:5267-5270`.)
  2. **MODEL-INVISIBLE FIELDS.** 15 of the 20 wrote only fields the emitted record DROPS. A field the
     WhyML record does not contain cannot be observed, relied on, or framed — and "fixing" those would
     emit `writes` on unbound symbols, the exact failure the field-label filter prevents.
Narrowing 20 -> 1 was the whole value of the audit; reporting 20 would have been alarmist and acting
on 20 would have broken the build. **Filter a frame audit by (a) final-state effect and (b) whether the
field survives into the emitted model, before counting anything.**

## Lesson (w) — a stale prover pin degrades a dual-prover gate to single-prover, silently and fail-closed

`_DEFAULT_PROVERS = ["Alt-Ergo,2.6.2,", "Z3,4.13.3,"]` against an installed Alt-Ergo **2.6.3**. Why3
answers `No prover in ~/.why3.conf corresponds to "Alt-Ergo,2.6.2,"`, the run produces no goal records,
the best-of-N merge is unchanged, and the residual goal stays Unknown. The error text is printed under
"Warnings/Errors from Why3" and changes no verdict. Two consequences that pull in opposite directions:
  - It is FAIL-CLOSED — the gate under-proves, so nothing unsound was ever accepted because of it.
  - But a re-proof sweep that must decide "revert this conversion or keep it" would FALSE-REVERT
    anything only Alt-Ergo can discharge. A fail-closed instrument is still the wrong instrument when
    the decision it feeds is destructive.
Also: `_run_vacuity_gate` loops every prover with no early exit, so a correctly-pinned run costs ~2x —
historical per-file timings were measured with the second prover effectively disabled.
**Check that each prover id you pass actually resolves (`why3 prove -P <id>` on a one-line goal) before
trusting any gate that claims to be dual-prover.**

## Lesson (x) — "reuse the existing pattern" can hide a closed algebra; count the emitted signatures

L13's capability (2) was scoped in the backlog as "`_call_term_constructor` on the LANDED
`_call_irnode_constructor` pattern, spec-driven off `compute_term_adt_spec` — no new table, no new
certificate, no axiom". Every clause of that is TRUE, and the conclusion it invites — that this is a
routing change — is FALSE.

The `term` carrier is reached only by whole-function RECOGNIZERS: a body is matched against a grammar
and handed to its own `emit_*_group`. Nothing composes. The one-command check that settles it is to
count the emitted signatures rather than read the emitter: in `parser.mlw`, **6 of 80** `let`/`val`
are term-typed, and all six are recognizer-generated helpers of three algebra functions. Every method
of the nest the capability was supposed to unlock emits `: int`.

So "a table/spec already exists for X" answers only *what X's shape is*. It says nothing about whether
there is a PATH by which an ordinary body acquires X. **Before costing a capability as reuse, count how
many emitted signatures already carry the target type and check whether any of them came from the
general path. If they all came from special-case recognizers, you are opening a closed algebra, not
reusing a pattern** — and the risk profile inverts too: recognizer groups are byte-inert by construction
because no corpus body matches their grammar, while a general-path change makes the corpus byte-diff a
real gate.

## Lesson (y) — a general-path capability inverts the byte-inertness argument; gate the DECLARATION on demand, not just the USE

Every capability the campaign had landed before L13 lived in a whole-function RECOGNIZER, and those are
byte-inert BY CONSTRUCTION: no corpus body matches their grammar, so the corpus cannot reach them. The
term-carrier work is the first that edits the GENERAL typing path, and the risk profile flips — the
corpus byte-diff stops being a formality and becomes the gate that actually bites.

It bit exactly once, and the shape is worth remembering. Six of the seven sub-capabilities were gated on
a USE site (`@mutable_state` + `_term_adt_spec` + a specific annotation) and were perfectly inert. The
seventh emitted a DECLARATION — `exception Return_term term` — inside a block that was already
`needs_term`-gated, which felt sufficient. It was not: 14 of 813 corpus programs emit `type term`, and
all 14 gained the two lines. **A declaration is reachable by every file that reaches the block it sits
in, regardless of whether anything uses it.** Gating it on an actual demand (some function really has a
term-typed early return) restored byte-diff 0.

Two corollaries paid for themselves in the same hour:
- **Fail LOUD when the gate is wrong.** The demand gate was first written comparing
  `func["self_type"]` (the PYTHON class name, `_Parser`) against `_mutable_state_classes` (WhyML
  identifiers, `_parser`). It matched nothing and suppressed a declaration the body still raised —
  surfacing immediately as `unbound exception symbol 'Return_term'` rather than as a silent facade.
- **Run the corpus byte-diff BEFORE the mirror proof sweep**, not after. It is ~7 minutes per side and
  it falsified the build in one shot; the mirror sweep is close to an hour.

## Lesson (z) — read your own backlog's amendments before searching the source

The single blocker that held the L13 term-carrier build for hours was "which predicate decides whether
`self.<m>()` lowers to the CONCRETE sibling or degrades to the opaque `self__<m>_<arity>` avatar". I
went looking for it in the emitter and refuted three candidates the expensive way:
`_module_method_return_types` (it records `_parser__peek: int` although `peek` demonstrably emits
`: _union_peek_0` — the registry is simply wrong for union returns), "is the callee defined in this
mirror" (both candidates are), and `_composed_provider_methods` (probed **empty** for `_Parser`, while
`peek` still lowers concretely).

The answer was `_record_array_fields`, and it was already written down — in this same backlog, in the
Gate-R amendment list: *"concrete `self.<m>()` sibling resolution is gated on `_record_array_fields`; a
`List[int]`-field class silently degrades to vacuous opaque `self_*_0` vals — a facade hazard to gate
against in any L13 build."* An independent reviewer had handed over the exact predicate, filed under
"hazard to gate against" rather than "predicate to reuse", and it read as a warning instead of an
answer.

**The rule.** A reviewer amendment phrased as a HAZARD is usually also a MECHANISM. Before grepping the
emitter for "how does X get decided", grep the backlog for X — amendments, struck items, and
carve-outs included. And when recording a future amendment, say which of the two it is.

---

*The lettered series continues from (z) here; (aa)–(ii) were banked in `driver-backlog.md`
§L13-CLOSED during relaunch #3 and are not repeated. (jj)–(ll) are from relaunch #4.*

## Lesson (jj) — a Phase-0 spike written with HAND-WRITTEN types answers a question the EMITTER cannot ask

The `pyast_expr` Phase-0 spike passed 19/19 and was handed forward as "the shape is not a
correctness boundary; the rest is emitter plumbing". That was true and still misleading, because the
spike gave itself ADT arms of its own design. The emitter has no such freedom: the 21 emitted
`_py_expr_*` handlers take **auto-derived records** (`ir_resolve._PURE_AST_FIELD_TABLE` ->
`type binop = { mutable binop_left: emit_ir; ... }`), several with `array emit_ir` or
`option emit_ir` fields. A Phase-0b spike at the *emitted* shape (`getting-better/pyast-expr/
pyast-expr-shape-spike.mlw`, 16/16 Valid) changed the plan in three places within an hour:

 1. **A Why3 mutual `type A = ... with R = {...}` group CAN mix a VARIANT and RECORDS.** So the
    plan's "retype all 23 handlers onto one ADT parameter" was never necessary — each handler keeps
    its own record signature and only the record's expr-child FIELD TYPES move. That is a far
    smaller emitter delta than the one that had been scoped, and a far smaller regression surface.
 2. **...but only if the records are PURE.** `mutable` is rejected outright — *"This field has
    non-pure type, it cannot be used in a recursive type definition"* — and by the same rule
    `array` fields are illegal inside the group. The emitter puts `mutable` on every field of every
    pure-ast record today, so a recursive `pyast_expr` needs a gated `mutable`-free emission AND a
    pure cons-list to replace `array emit_ir`.
 3. **The encoded PAIR was not enough.** See (kk).

**The rule.** Before funding a build off a Phase-0 spike, re-spike at the shape the emitter can
ACTUALLY produce — same types, same mutability, same field kinds. The cheap version of this is:
open the emitted `.mlw` and copy the real type declarations into the spike. A Phase-0 spike bounds
the CORRECTNESS question; only a Phase-0b spike bounds the BUILD.

## Lesson (kk) — count the LEVELS in an encoded-pair variant; a list mapper is a third level

The handoff's device was `2 * size e + <level>` with level 1 for the dispatcher and 0 for the
handlers, and it is correct for a dispatcher that hands the same node to a handler which then
recurses on a strict sub-node. The REAL shape has a third participant: a list-carrying arm's handler
(`_py_expr_tuple`) calls a **list mapper** which calls the dispatcher once per element. With
multiplier 2 there is no room for it and the mapper's own VC **times out at 23M steps** — which
looks exactly like an E-matching wall and is really an unprovable goal (wall-lessons (ee), again).
The arithmetic is worth writing down because it generalizes: from `2*size_pxlist l + 1` the element
call needs `size h < size_pxlist l`, and `size_pxlist l = size h + size_pxlist t`, so it needs
`size_pxlist t > 0` — FALSE for a one-element list. With `4 * <size> + <level>` and level 0 =
handlers, 1 = dispatcher, 2 = list mapper, every obligation is Valid in hundredths of a second.

**The rule.** The multiplier must exceed the number of levels, and the number of levels is the
length of the longest chain of mutual calls that does NOT strictly shrink the structure — count it
by walking the emitted call chain, not by assuming two.

## Lesson (ll) — a SYNTHESIZED call needs a synthesized ORDERING EDGE, or Why3 rejects the file

A bespoke whole-body emitter that manufactures calls the IR does not contain is invisible to
`find_calls_in_ir`, and therefore invisible to `sort_functions_by_scc`. The `_py_expr_to_ir`
dispatcher's body names only the handler LOCAL; the 23 method calls appear for the first time in the
emitter. It sorts alphabetically before `_py_expr_tuple` / `_py_expr_unaryop` / `_py_expr_walrus`
and Why3 rejects the whole file with `unbound function or predicate symbol`. The fix is the existing
explicit-citation channel — `func["uses"]`, which `sort_functions_by_scc` already honours for
`#@ uses <lemma>` — populated before sorting.

**The rule.** Whenever a recognizer emits a call that is not in the IR, ask in the same breath what
guarantees the callee is DECLARED FIRST. This failure is loud, which is the good news; the bad news
is that it surfaces only at whole-file L3-tc, i.e. after the rest of the build already looks done.

## Lesson (mm) — "converting the dispatcher makes its handlers mutually recursive" is FALSE unless the sibling-resolution GATE says so

The backlog had `_csl_to_ir` filed as the hardest L2 member, "strictly larger" than its siblings
because converting it "makes 75 already-verified handlers mutually recursive, which needs a
structural `#@ \variant` over CSL nodes". That is the intuitive reading of the source — the
handlers do call `self._csl_to_ir(...)` — and it is wrong about the EMISSION. A handler's
`self.<m>()` call lowers to the CONCRETE sibling only when the concrete-sibling resolution admits
it (`_record_array_fields`, or an explicit `#@ sibling_concrete`); otherwise it degrades to the
abstract `self__<m>_<arity>` val. Neither dispatcher qualifies, so all 73 handlers kept calling
the abstract val after the conversion: **no SCC formed, no variant was needed, no structural
measure over CSL nodes was needed.** The item that had been carried as session-scale for several
windows was a few hours' work once the census was run.

**The rule.** Before scoping a build around "this will create mutual recursion", read the emitted
`.mlw` and check whether the sibling call is CONCRETE or an abstract val today. The source's call
graph and the emitted call graph are different graphs, and this campaign's gating machinery is
precisely what separates them.

## Lesson (nn) — a capability's SECOND instance is where its hidden assumptions surface; budget for four, not zero

Carrying the type-keyed dispatch expansion from `_PY_EXPR_HANDLERS` (23 entries) to
`_CSL_HANDLERS` (77) needed four extensions, none of which was visible from the first instance:

 - the Module 5 collector accepted only DOTTED class keys (`ast.Name:`), so a table written with
   BARE imported names (`CSLBinOp:`) had been silently invisible to the registry since it was
   built — the capability did not fail on the second table, it simply never saw it;
 - the arm payload type must come from the HANDLER's declared parameter class, not the table key:
   four `ContractWrapper` SUBCLASSES share one base-typed handler, and keying on the entry emits
   a subclass record against a base-typed parameter;
 - the dispatcher body had a second SHAPE (`if handler is None: raise` + unconditional dispatch)
   — and it is the STRONGER one, because its default arm is the source's own raise;
 - the emitted body must DECLARE the union of every exception its arms propagate, or Why3 rejects
   the file.

Every one was found by a measurement (a census, a type error, a Why3 error), and every one made
the capability more general rather than more special-cased.

**The rule.** When a landed capability is "obviously reusable" for a second instance, do the
census before the estimate: enumerate the second instance's keys, its handlers' emitted
signatures, and its body shape, and diff them against the first's. The generalization is usually
worth doing — but the estimate that says "it already works" is the one to distrust.

## Lesson (oo) — the campaign's headline count has been 25 too high since it started, and the cause is a docstring

Every window reports progress as `grep -rcF '#@ \trusted' src/self-annotate/src --include=*.py`,
summed. That counts LINES CONTAINING the substring, not MARKERS. Measured: **25 of the 617 hits
are one line of boilerplate MODULE DOCSTRING**, repeated verbatim in 25 mirror files —

    annotated `#@ \trusted reviewer: pycsl-self-annotate`; bodies ...

The true number of `\trusted` directives is **592**. Every DELTA ever reported is correct (the
offset is constant while the mirror file set is), but the ABSOLUTE figure is not — and every
statement of the form "the autonomous floor is N" inherits the error. `bin/count-trusted-directives.py`
now reports markers, the grep figure, and the itemised offset side by side, so a CHANGE in the
offset (a new mirror file, or a marker that stops being attached to anything) is visible instead
of being silently folded into the count.

**The rule.** A metric quoted in every report for months is exactly the metric nobody re-derives.
Reconcile the headline number against a structural count at least once per campaign — and when
the two disagree, keep quoting BOTH until the discrepancy is explained, rather than switching
silently to the new one.

## Lesson (pp) — measure the CONVERSE of every integrity gate; and beware the regex that eats a keyword

`check-untrusted-emitted.py` asks "is every UN-trusted function really emitted as a definition?"
(the auto-trust-valve hazard, which over-reported conversions). The converse — "is any TRUSTED
function nonetheless emitted as a real definition?" — had never been asked, and it is a live
possibility rather than a theoretical one: several `_py_expr_*` / `_py_stmt_*` handlers are
emitted by BESPOKE whole-body lowerings in `module6_whyml/functions.py` whose gates do not
consult the marker at all. A stale marker there would mean the count is OVERSTATED — the
directive claims an assumption that is not being made. Measured: **0**, so the count is honest in
both directions. A clean negative, but only because it was checked.

Two false-positive families had to be cleared to get that zero, both of the naming-trap kind:
 - a prose comment MENTIONING the marker ("...unlike the same clause on a `#@ \trusted` stub...")
   read as a marker during the upward block walk, and reported six converted `_Parser` methods as
   trusted-but-defined. Require the marker to be the line's FIRST token.
 - `[A-Za-z0-9_]*rec\b` after an optional ` rec` matches the **`rec` of `let rec <something>`**
   by backtracking, so a mirror function named `rec` (the lifted nested `def rec` in
   `module6_whyml/statements.py`) was reported twice. CAPTURE the identifier and test it against
   the Python name, never splice the name into the pattern.

**The rule.** When scanning emitted WhyML for a declaration, capture the identifier and compare
it; and reject the language's keywords explicitly. Splicing a name into a regex invites the
engine to find it inside the syntax rather than in the name.

## Lesson (qq) — a RAISE that models as a FALL-THROUGH is a facade, and only the emitted body shows it

`_Parser._name_str`'s live body is `if <reject>: self.error(...)` then `return self.advance().string`.
Converted, it emitted as

    if (<cur token is not NAME>) then begin let _ = (self_error_1 "expected name") in () end;
    (let _rec_ = (advance self) in _rec_._tok_string)

The guard branch does NOTHING and falls through: the model claims a NORMAL RETURN on exactly the
input where the live body RAISES. **L3-tc passed and the whole file proved.** Nothing false is
provable from it — the contract is `ensures True` — but the function that was verified is not the
function in the source. This is the raise-side twin of `isinstance_op 0 0` and `iter_length 0`:
the emission type-checks, proves, and models the OPPOSITE of the live control flow.

The cause was an emitter gap in the `-> NoReturn` recognition (the QUOTED `-> "NoReturn"` form was
read as an ordinary return type), and the fix makes the branch `(let _ = … in absurd)`.

**The rule.** For any conversion whose live body has a raising guard, READ THE EMITTED BRANCH and
confirm it ends in `absurd` (or a real `raise`). "It type-checks and proves" is exactly the state
this defect produces. Add the raise-side markers to the facade-detector list you grep for:
`in ()` where a raise should be, a `: unit` val where a `-> NoReturn` callee should be, and an
`ensures { false }` that is ABSENT from a diverging callee's declaration.

## Lesson (rr) — re-measure an inherited PROOF-SCALE wall before you inherit it

The backlog carried `frontend/pure_ast.py` as "TERMINUS = solver-context-saturation PROOF-SCALE
wall, reopen needs review-gated modular proof", and that record kept the largest single block of
TCB in the tree (186 markers, 31% of the total) off the ladder for many windows. Measured fresh in
minutes: the file proves **235 Valid, 0 non-Valid, SUCCESS** — it is one of the CHEAPEST files in
the suite to gate, not one of the most expensive. Whatever saturated the solver then is not
present now (the `wf_val_str_stable` option-a hardening landed after that record was written).

Proof-scale walls are the most perishable kind of finding in this campaign, because every
proof-hardening increment can retire one silently. A COST/SCALE or PROOF-SCALE record should be
re-measured before it is used to skip a vein — the measurement is one command.

**The corollary that actually mattered here:** run a PER-FILE census of the count at least once
per campaign. The ladder was working files with 30-40 markers while one file held 186.

## Lesson (ss) — `pure_ast`'s module globals ARE its AST-node namespace, so a `typing` import SILENTLY REPLACES an AST node class

I recommended, in this same window, "add the `typing` import to `pure_ast.py`" as a small safe
capability to unblock `List[...]` annotations there. **That recommendation was dangerously wrong,
and acting on it broke the parser.**

`pure_ast.py` builds its ~130 AST node classes at import time with `_build_nodes(globals())` —
the module's own globals are the node namespace, and `_N(name)` is literally `_g[name]`. FOUR
ASDL node names collide with `typing` names: **`List`, `Set`, `Dict`, `Tuple`**. So
`from typing import List` REPLACES the `List` AST node class, and the very next list literal the
parser meets calls `typing.List(...)` and dies with

    Type List cannot be instantiated; use list() instead

The failure surfaced as an "UNEXPECTED PIPELINE ERROR" with no traceback — the top-level handler
prints only `str(e)` — and it looked exactly like an emitter/monomorphizer limitation on
`List[<record>]` return annotations. It is not: it is a runtime name collision in the LIVE source
that my own edit introduced. I found it by hooking `typing.List.__call__` and printing the stack.

**The rules.**
 - In any module that installs generated classes into its own globals, an import is not
   namespace-neutral. Check a new import name against that generated namespace BEFORE adding it.
 - When an "UNEXPECTED PIPELINE ERROR" prints a message with no traceback, get the traceback
   before theorising: hook the failing callable, or re-run the stage directly. The message alone
   sent me looking in the emitter for a bug that was in the file I had just edited.
 - A live-source edit that is "obviously runtime-inert" deserves the same smoke test as any
   other. `import pure_ast; pure_ast.parse("x = [1]")` would have caught this in one second —
   and my earlier smoke tests used `x = 1` and `import a.b as c`, neither of which builds a
   `List` node. **Choose the smoke test to exercise what the edit could plausibly break.**

---

*(tt)–(vv) are from relaunch #5.*

## Lesson (tt) — a QUOTED parametric return annotation is not a monomorphizer gap, it is an UNPARSED STRING

Relaunch #4 measured `-> List[alias]` on `_Parser._import_as_names` and recorded

> BLOCKER 1: `List[<harvested record>]` as a RETURN annotation is a MONOMORPHIZER GAP — both
> `-> List[alias]` and the quoted form fail the whole pipeline with *"Type List cannot be
> instantiated; use list() instead"*.

Both halves of that are wrong, and they are wrong for two DIFFERENT reasons that happened to
land in the same window:

 - the BARE form's failure was lesson (ss) — the `typing` import that had been added to make
   `List` resolvable had REPLACED `pure_ast`'s `List` AST node class, and the error came from
   the parser, not the emitter;
 - the QUOTED form does not fail at all. Module5's `node.returns` dispatch has an
   `ast.Constant` branch that recognises exactly ONE string — `"NoReturn"` — and otherwise
   assigns the string VERBATIM as the return annotation. `"List[alias]"` is not a type name
   Module6 can resolve, so the return silently stayed the collapsed `int`, and the only symptom
   was an L3-tc clash (`seq py_alias` vs `seq int`) at the `materialize` call. **Nothing was
   "instantiating List".** The `ast.Subscript` branch — which already has the full
   `List[str]`/`List[float]`/`List[<record>]` element analysis — was simply never reached,
   because a quoted annotation is a `Constant`, not a `Subscript`.

**The rule.** When an annotation "does not work", first establish WHICH AST NODE the emitter
actually sees for it. A quoted annotation and its bare twin take different branches everywhere
in this pipeline, and a capability that exists on one branch is routinely absent on the other.
Corollary: the error message you are handed may belong to a completely different stage — get the
traceback (lesson (ss)) before you name the wall.

## Lesson (uu) — a METHOD's function-IR name is MANGLED, so every bare-name lookup into `ir_data["functions"]` silently no-ops for methods

`ir_resolve._resolve_same_file_node_spec_records` resolves the function IR for an AST `FunctionDef`
with `func_by_name.get(node.name)`. For a module-level function that works. For a METHOD the IR
name is `<classname-lowered>_<methodname>` — `_Parser._import_as_names` is
`_parser___import_as_names` — so the lookup returns `None` and the pass does nothing, with no
error and no warning. The pre-existing param-annotation branch in that same loop has the same
latent bug: it can only ever have fired for module-level functions, which is not where pure_ast's
node-typed parameters are.

The fix that is robust for both shapes is to match on the def's **line** plus a name-SUFFIX check,
not on the name alone.

**The rule.** A `dict.get(name)` against an IR built by a different stage is a silent no-op when
the two stages disagree about naming. Whenever a pass "does nothing" and the gate is a type error
three stages later, print the KEYS before theorising about the feature.

## Lesson (vv) — where to put a live-emitter change is decided by the §10.4 RE-PORT COST, not by taste

The seq→array return bridge is ELEMENT-TYPED and there were only two of them (`materialize` for
`seq int`, `materialize_str` for `seq string`); a RECORD payload type-clashes with both. The
clean-code placement is two new helper methods in `module6_whyml/statements.py`
(`_materialize_record_elem` as the gate, `_materialize_rec_bridge` as the emitter), called from
`_handle_return_stmt`. I built that first, and it was the WRONG placement — measured:

 - it changes THREE live functions with un-trusted mirrors instead of one, so §10.4 obliges three
   ports and re-proofs of TWO mirror files instead of one;
 - the mirror `stmt_control_flow.py` would need SIBLING STUBS for the two new helpers, and the
   record-type gate (`for rec in self._record_types.values()`) is a dict-of-dicts read that this
   mirror cannot lower faithfully — so at least one of them would have to be `\trusted`.
   **That would ADD a marker and cancel the conversion the whole increment exists to make.**

Re-placed INLINE at the single call site in `_handle_return_stmt` — which was going to diverge
anyway — with the gate rewritten in the string primitives the mirror body ALREADY uses for
`func_ret[len("option "):]`, the cost fell to one port, one mirror re-proof, and zero new markers.

**The rule.** Before choosing where a live-emitter change goes, count (a) how many un-trusted
mirror bodies it makes diverge, and (b) whether any helper it introduces would need a `\trusted`
stub in the mirror. In this campaign a refactor that adds a marker to save a marker is a net
LOSS, and "put it in a well-named helper" is exactly the instinct that produces one. The corollary
for the emitted code: prefer primitives the mirror already models over ones that read better.

## Lesson (ww) — the mirror emission SWEEP does not type-check; a re-ported body can be ill-typed and the sweep will report it as a clean 2-of-52 diff

`bin/byte-diff-sweep.sh` and every mirror-emission manifest in this campaign run with
`--no-typecheck` (they measure BYTES, and the why3 call is what makes them slow). I re-ported a
branch into the un-trusted `module6_whyml/stmt_control_flow.py` mirror, read the emission diff by
eye, confirmed it used only primitives that mirror's own converted body already uses, and moved on
to the proof. The proof failed at **L3-tc, in seconds**, on that exact line: the mirror models
`_add_abstract_op`'s argument as a **hashed `int`** (`self__add_abstract_op_1 (x0: int)`), because
every existing call site passes a string LITERAL and the emitter hashes those — so a COMPUTED
string argument is a type error there, and no amount of reading the diff shows it.

**The rule.** After a §10.4 re-port, run `--no-proof --typecheck` on the changed mirror BEFORE
queueing its whole-file proof. It costs a minute and it is the difference between a failed 30-minute
proof and a fixed increment. More generally: a byte-level gate is not a well-formedness gate.

The fix generalizes past this instance: **an abstract sibling val's parameter types are inferred
from the argument shapes the emitter has already seen at its call sites.** If your new call passes
a differently-typed argument, you must either give the sibling a typed stub (which costs a
`\trusted` marker) or MOVE THE CALL to a function whose mirror is already `\trusted`. Here the
declaration moved to `functions.py::_emit_function`, whose mirror is trusted, and the return site
kept only the NAME.

And a second measurement from the same move: declaring the bridge off the RETURN TYPE alone broke
byte-diff-0 — corpus driver `0839` returns `List[Point]` built from a list LITERAL and never calls
the bridge, so it got an unused `val`. The trigger has to be the EMITTED BODY actually naming it.
**"Which functions have this type" is a different set from "which functions emit this call".**

## Lesson (xx) — an inner loop's `assigns` says nothing about DIRECTION; give it a GHOST snapshot, not a real local

`comp_for`'s OUTER cursor-measure loop failed `loop variant decrease` even though its body calls
`expect_kw("for")`, which now exports an UNCONDITIONAL `ensures self.i > \old(self.i)`. The gap was
the INNER `while self.at_kw("if")` loop that runs afterwards: `assigns self.i` permits it to move
the cursor BACKWARDS as far as the prover is concerned, so the net effect of the outer body was
unknown. This is the (relaunch #4) `_name_str` lesson one level up — *a cursor-measure loop needs
monotonicity from every call in its body* — and a nested LOOP is one of those "calls".

The fix has to name the cursor's value at the inner loop's entry, and the obvious way (a real
local `i_before = self.i`) would put a statement in the mirror body that is NOT in the live body
and **break the fidelity plane**. `#@ ghost i_before = self.i` is the right tool precisely because
it is an ANNOTATION: the mirror body stays byte-identical to the live body, the sync gate is
untouched, and the emission is a real `let ghost i_before = ref self.i` that the inner loop's
`invariant { self.i >= !i_before }` then closes. 316 -> 363 Valid, 0 non-Valid.

**The rule.** When a proof needs to refer to a value the source does not name, reach for `#@ ghost`
BEFORE reaching for a new local. In this campaign a mirror-only local is a fidelity failure; a
mirror-only ghost is free.

## Lesson (yy) — a NEW METHOD on a widely-imported emitter class is not free: it becomes an abstract `val` in every mirror that imports the class

I factored the `_fin` recognizer's guard into a small `@staticmethod
_m5_is_class_by_name_ctor`. Measured effect on the mirror emission sweep: **1 changed mirror became
3**, because `frontend/__init__.mlw` and `frontend/ir_resolve.mlw` each gained the line

    val pycsltojsonemitter___m5_is_class_by_name_ctor (self: pycsltojsonemitter) (e: int) : int

— a declaration-only change, but one that obliges two extra whole-file re-proofs, for nothing.
Spelling the same predicate INLINE at its single call site put the sweep back to 1 of 52.

This is lesson (vv) again from a different direction: in this campaign the unit of cost is not
"lines of code" but "how many verified artifacts does this perturb". A helper method has a
NON-LOCAL price whenever its class is imported by other mirrors — and `PyCSLToJSONEmitter` is
imported by most of them.

**The rule.** Before extracting a helper on an emitter class, ask which mirrors import that class.
If more than the one you are working on does, inline it.

## Lesson (zz) — a per-class record model cannot type a PASSTHROUGH return, and that is where the pure_ast mass actually is

The class-by-name factory gives each ASDL node class its OWN WhyML record (`py_alias`, `arg`,
`comprehension`, …). That is faithful and it converts a stub whose every `return` builds the SAME
class. Measured on the 57 `_fin`-gated `_Parser` stubs: only **13** are that shape. **40** have a
PASSTHROUGH return —

    x = self.<sub>()
    if not self.at_op(<op>):
        return x                       # <- some other node class
    ...
    return self._fin(_N("BinOp")(...), t)

— the ordinary Pratt-parser shape. Under per-class records those two returns have DIFFERENT types,
so the function has no WhyML type at all; no amount of recognizer work reaches them.

**The rule.** When a value model gives each variant its own type, census the RETURN SHAPES of the
consumers before estimating the vein. A model that types constructions beautifully can still type
almost none of the FUNCTIONS, and the fix is a sum type, not a better recognizer. (Here that is
exactly the `pyast_expr` Stage-B item the campaign already has on the ladder — so the right move is
to fund THAT rather than to keep widening the field table.)

## Lesson (yy-ext) — a NESTED `def` and even a MODULE-LEVEL function ripple exactly like a new method

(yy) said "a new method on `PyCSLToJSONEmitter` becomes an abstract `val` in every mirror that
imports it — inline it instead". Extracting the same predicate as a NESTED `def` inside the method
did NOT help: the emitter LIFTS nested functions, and

    val pycsltojsonemitter___q (self: pycsltojsonemitter) (e: int) : int

appeared in `frontend/__init__.mlw` and `frontend/ir_resolve.mlw` just the same. Moving it to
MODULE level did not help either:

    val _m5_quoted_irnode_arm (e: int) : int

appeared in exactly the same two files. Only literal INLINING at each of the three call sites put
the mirror sweep back to 1 of 52.

**The rule.** In a module whose class or namespace other mirrors import, *any new named callable* —
method, nested def, or module-level function — is a new declaration in their emissions. When the
alternative is two extra whole-file re-proofs, duplicate the three lines and say so in a comment.

## Lesson (ab) — the `Optional[X]` COLLAPSE is right for a param/field and wrong for a LOCAL, and the seams are disjoint

`_irnode_ann_name` deliberately maps `Optional[ExprIR]` to plain `ExprIR` ("emit_ir is total"), and
the code carries a scar explaining why: commit b18932b8 typed EVERY `Optional[ExprIR]` FIELD as
`option emit_ir` and broke every consumer mirror that reads such a field as a bare always-present
node. That history makes the collapse look untouchable.

It is untouchable **at the param and field seams**. At the LOCAL-declaration seam it is exactly
wrong: `val: Optional["ExprIR"] = None` collapses to a bare `emit_ir` ref initialised to
`IrOther ""`, so the value-less path models as a NODE — the None-reads-as-a-value erasure — and
binding the local to a genuinely `option emit_ir` record field is an L3 type error. Synthesizing
the union in `_build_function_symbol_table`'s AnnAssign branch ONLY leaves the param/field seams
byte-identical, so b18932b8's regression cannot recur; `return_stmt` then emits
`Arm_2_None` / `Arm_2_0 (testlist self)` and projects to a real `Some`/`None`.

**The rule.** When a recorded regression says "typing X as an option broke everything", check
WHICH SEAM it broke. `param`, `field`, `local` and `return` are four different code paths in this
emitter, and a fix confined to one of them does not re-open the others. Read the scar before you
believe it covers your case — and confine the change to the seam you measured.

## Lesson (ac) — when a list-FIELD binder declines, the field silently becomes an EMPTY array

`_call_record_constructor` handles a `list`/`array` field by calling `_bind_listfield_from_seq`
and, if that returns None, `continue`-ing — which leaves the field at its typed default
`Array.make 0 0`. So every gate the binder applies (element type known, `@mutable_state` class,
bare-positional initialiser, `!<seq local>` actual) is, on failure, a SILENT DROP of the caller's
list. It type-checks; it proves; and the constructed node has an empty child list.

This bit twice in one window — once for a `seq` local whose element type came from a CALL rather
than a literal ADT constructor (increment 3), once for a RECORD element type the binder did not
accept at all (increment 7). Both were found only by reading the emitted record literal and seeing
`Array.make 0 0` where the accumulator should be.

**The rule.** Any conversion whose constructed node has a LIST field: read the emitted record
literal and confirm the field is bound from the actual list. `Array.make 0 0` / `Seq.empty` in a
record literal whose source passes a non-empty accumulator is a facade marker — add it to the grep
list beside `iter_length 0`, `isinstance_op 0 0`, and `in ()` where a raise belongs.

## Lesson (ad) — the sum type the parser needed ALREADY EXISTED: it is `emit_ir`, and the recorded Stage-B plan was the expensive way to get it

Lesson (zz) measured that 34 of the 42 still-`\trusted` `_fin`-gated `_Parser` methods have a
PASSTHROUGH return (`return x` beside `return self._fin(_N("Await")(value=x), t)`) and concluded
"the fix is a sum type, not a better recognizer — so the right move is to fund the `pyast_expr`
Stage-B item". Stage B is a large build: a NEW recursive `pyast` ADT, a purity retrofit of every
harvested pure_ast record, a bespoke `pxlist` cons-list, eight opaque node types converted, and a
new structural measure. Its own entry says "DO NOT attempt Stage B as one increment".

None of that was necessary. **The `-> "ExprIR"` RETURN INTERFACE — the zero-marker lever from
relaunch #5 — already gives every un-converted sibling the type `emit_ir`.** So the passthrough
half was solved before the wall was written; only the CONSTRUCTION half was missing. And
`emit_ir` is already recursive, already pure, already certified, and already carries `size`.

The whole capability is one table — `frontend/ir_resolve.py::_PYAST_IRNODE_CTORS`, mapping a
pure_ast node class to an `emit_ir` constructor plus its payload in ASDL field order — driving
four consumers that therefore cannot drift: the ADT arms, the `kind_of` arms, the by-name payload
binding, and the structural `init_params` harvest. Twelve conversions in four increments
(577 -> 565 markers), each one a real `IrPy*` construction with every child carried.

**The rule.** When a wall says "this needs a new value model", first ask whether an EXISTING
certified model already has the shape, and whether some other lever has already solved half the
problem. Here the answer was hiding in the campaign's own toolbox: a return-interface lever
written for a different purpose had silently made the hard half free.

## Lesson (ae) — a 0-field ASDL singleton is faithfully modelled by its CLASS-NAME STRING; the enum-variant plan was over-engineering

The backlog's item 3 said "0-field ASDL singletons need a base-category ENUM VARIANT ... a 0-field
WhyML record is not expressible ... COST/SCALE: the `ctx`/`op` field tags move from `int` to the
category type." The first half is right and the second half is unnecessary.

A 0-field class carries NOTHING beyond its own IDENTITY: `_N("Load")()` is a constant and every
construction of it is interchangeable with every other. So its class NAME, as a `string`, is a
COMPLETE model — nothing is erased — and it drops straight into a `string` payload slot of an
`emit_ir` ctor (`IrPyStarred emit_ir string`, `IrPyUnaryOp string emit_ir`). No enum type, no new
ADT, no axiom, and no field-tag migration through every already-converted handler.

Two measurement notes. (i) Harvest the membership from the compiled file's OWN `_NODE_SPEC`, not
from `_PURE_AST_FIELD_TABLE` — the field table lists only the classes WITH fields, so the first
attempt produced an EMPTY singleton set and the lowering silently did not fire. (ii) Prefer a
DEDICATED arm over a generic one that drops the slot: `IrStarred emit_ir` already existed and
would have DROPPED `ctx`; `IrPyStarred emit_ir string` carries it.

**The rule.** Before building a type to represent a finite set of tags, check whether the tag's
NAME already is the whole of its content. It usually is, and a string costs nothing.

## Lesson (af) — a new `emit_ir` constructor silently makes `kind_of` NON-EXHAUSTIVE, and the failure looks like a hard goal somewhere else

`kind_of` enumerates EVERY `emit_ir` arm and ends at `| IrOther k -> k` — there is no `_`
catch-all. Adding two ctors therefore left the match non-exhaustive; Why3 inserted an
unreachable-point VC, and the run came back with ONE unproven goal: `Sub-goal unreachable point of
goal kind_of'vc`, a 30-second Timeout at 39,491,039 steps. Nothing in the diagnostic points at the
new constructors, and the failing goal is nowhere near the function being converted.

The same failure MODE recurred from a different cause in the next increment: `pattern`'s
`ensures self.i >= \old(self.i)` ran through `_capture_name`, which exported no monotonicity
clause. Again not `Unknown` — a 30s Timeout at 29,241,942 steps.

**The rule.** A multi-million-step Timeout in this codebase is almost never "a hard goal". Read
the goal NAME first: `<theory function>'vc` means a totality/exhaustiveness obligation you broke
by extending an ADT; a cursor postcondition means a callee is missing its monotonicity export.
Both are one-line fixes and neither is visible in the emitted diff.

## Lesson (ag) — (ww) again, and the fix belonged in the DESIGN, not in the mirror

`_call_irnode_constructor` reads `init_params` out of `self._record_types`, so the first version of
the pyast ctor family gave each member a `_PURE_AST_FIELD_TABLE` entry. The mirror sweep went from
1 of 52 to 2 of 52 with a FOUR-LINE, entirely innocuous-looking diff in `Module5_IREmitter.mlw`:

    >   type boolop = { mutable boolop_op: int; mutable boolop_values: array emit_ir }
    -     | PEx_BoolOp py_boolop_node
    +     | PEx_BoolOp boolop

That file was ILL-TYPED. The field-table entry retyped the `PEx_BoolOp` arm of Module5's
`pyast_expr` ADT to the harvested record while `_py_expr_boolop`'s own signature kept its bespoke
opaque `py_boolop_node`. Caught only by `--no-proof --typecheck` on the changed mirror.

The patch would have been to retype the handler too. The FIX was to remove the coupling: a family
member's `init_params` now come from a STRUCTURAL `_NODE_SPEC` harvest, because the shared
`AST.__init__` binds positional args to `cls._fields` in order — so the field tuple IS
`init_params`. The mirror diff went back to 1 of 52, the `wanted`-harvest widening became
unnecessary, and the harvest CARRIES A DRIFT CHECK: an entry is published only when the ctor
payload's field names equal the `_NODE_SPEC` tuple exactly, so a renamed or reordered ASDL field
silently removes the entry and the construction FAILS CLOSED.

**The rule.** When a change leaks into a mirror you did not mean to touch, the leak is usually a
COUPLING, not a bug. Ask what made the other file care; removing that dependency is often both
cheaper than the patch and strictly safer.

## Lesson (ah) — a local first assigned inside a CONDITIONAL BRANCH is scoped to the branch, and a list field bound from it silently becomes `Array.make 0 0`

`import_from` assigns `names` in THREE `if`/`elif`/`else` branches and reads it AFTER the `if`.
The Assign emitter `let`-binds a list local at its FIRST assignment, so each branch emitted its own
`let names = ref … in` — dead at the closing `end` — and the constructed node's list field fell to
its typed default. That is lesson (ac)'s facade, reached by a completely different route.

The repair is the pre-declaration idiom `_emit_body_code` already uses for strings (`ref ""`),
emit_ir (`ref (IrOther "")`), option-string (`ref None`) and records: one more per-kind set, here
`seq <record>` -> `ref (Seq.empty: seq py_alias)`. The same is true of an emit_ir local that a loop
REBUILDS (`node = _N("Attribute")(value=node, …)`, the dotted-name fold): without the pre-decl the
loop emits `:=` against an immutable `let` and fails L3-tc.

**The rule.** Any converted body that assigns a non-scalar local inside a branch or rebuilds one in
a loop needs that local in a pre-declaration set. Check the emitted code for a `let <x> = ref …`
INSIDE an `if` arm — it is always wrong, and when the local is a list it is a silent facade.

## Lesson (ai) — do NOT stack whole-file mirror proofs in parallel; they are already prover-parallel and four of them DEADLOCK the box

Increment 10 changed four mirrors and I launched all four whole-file proofs at once to save wall
clock. Load went to 20 on 12 cores and **all four stalled with no log output for 17 minutes** —
not slow, STOPPED. Killed and re-run one at a time, every one completed normally
(753 / 655 / 883 / 706 Valid, all SUCCESS) in roughly the time one of them takes alone.

A `pycsl.py --provers` run already fans out over goals, so N concurrent runs is N× oversubscription
of a pool that is already saturated. And a stalled proof is indistinguishable from a slow one from
the outside, which is exactly the state a supervisor cannot read.

**The rule.** One whole-file proof at a time, waited on inside your own turn. If a bundle needs
four, that is four sequential runs — budget ~15 minutes each and say so in the progress log.

## Lesson (aj) — a §10.4 re-port refused once is worth RE-COSTING once the same blocker reappears

Increment 8 refused `power` because it needed two live-emitter pieces whose mirrors are
un-trusted: fidelity measured 4 DIVERGED and the price was two first-ever whole-file mirror
re-proofs. That was the right call *at the time* — the yield was one marker.

Two increments later the SAME two pieces were blocking `power`, `_subscript`, `_binop`,
`atom_paren`, `strings`, `_fstring`, `_dict_rest` and both comprehension targets. The price had
not changed; the YIELD had. Measuring the two baselines first (`types.py` 631 Valid,
`statements.py` 871 Valid, both clean, ~15 min each) turned an unknown into a budget, and both
re-ported mirrors then proved STRONGER than their baselines (655 and 883) rather than needing any
repair.

**The rule.** Record a cost-refused item with its EXACT price and its exact two pieces, not just
"too expensive". When the same pieces show up blocking a third and fourth item, re-cost — and
measure the baseline proof of the mirror you would have to re-port BEFORE deciding, because
"unmeasured whole-file re-proof" reads as infinite and is usually fifteen minutes.

## Lesson (ak) — an ASSUMED clause on a `\trusted` stub is a TCB ADDITION; it must unlock a conversion in the SAME increment

The `-> "ExprIR"` RETURN INTERFACE is the campaign's cheapest lever: a stub that STAYS `\trusted`
can be given a faithful return type at zero marker cost, and that is what unlocks its callers. But
the same move usually carries `ensures self.i >= \old(self.i)` as well, and on a `\trusted` stub
that clause is ASSUMED, not proved — it is new trust, invisible to `count-trusted-directives.py`
because the marker count does not change.

Twice this window I added a batch of interfaces speculatively — five in one attempt, nine in
another — because the conversion they were meant to serve looked one step away. Both times the
conversion turned out to be blocked on something else, and both times I reverted them. Had I
committed instead, the tree would carry fourteen assumed cursor clauses buying nothing, and the
NEXT worker would have had no way to tell which of them were load-bearing.

**The rule.** Add a return interface (and especially a monotonicity clause) only in an increment
whose gate battery proves it was consumed. If the conversion refuses, revert the interface with it.
The count does not police this; only the discipline does.

## Lesson (al) — a DROPPED KEYWORD ARGUMENT is invisible to every gate and changes what the verified artifact means

Module 5's bare-name call branch has captured `expr.keywords` since WL-07. Its `ast.Attribute`
branch never did. So for every dotted call in the tree, `f(x, flag=True)` reached Module 6 as
`args: [x]` with the keyword simply gone.

Two effects, and the second is the one that matters. (i) The emitted application is a PARTIAL one —
`self.for_stmt(async_=False)` became `(_parser__for_stmt self)` of type `int -> emit_ir` — which
ill-types wherever the result is used, so it fails loudly and blocks a conversion. (ii) Where the
callee is an abstract op the arity is padded, and the missing argument is filled with the int
default: `stmt_control_flow`'s `self._render_match_pattern(pat, negate=True)` emitted
`self__render_match_pattern_2 !pat 0`. **The verified artifact modelled `negate = False` where the
source says `True`.** Nothing false was proved (the callee is an abstract op with no contract), but
the file that was proved was not the file on disk — and NO gate reported it: the byte-diff is 0
because nothing changed, fidelity is green because the mirror body matches the live body verbatim,
and the vacuity probe only looks at whole-parameter erasure.

**The rule.** When an argument-passing path is added or widened, check BOTH branches of the call
shape (bare name AND dotted). And treat "the emitted call has fewer arguments than the source" as a
correctness bug, not a typing nuisance — the typing failure is the lucky case.

## Lesson (am) — "the annotation has no effect" almost always means you measured the wrong half. PROBE the emitter before you patch it

Relaunch #6 recorded a hard finding: a `\trusted` stub annotated `-> bool` still emitted
`val … : unit` even after an EXACT copy of the `-> str` disjunct that works was added to
`_compute_return_type`, "so `_compute_return_type` is NOT the decision point". That conclusion was
wrong, and it cost the next worker's first hour to overturn. Two separate things were true:

1. **The stub being measured had no `-> bool` annotation at all.** A four-line probe printed what
   the emitter actually sees — `ann = None`, `return_type = unit`, `trusted = True` — so the new
   disjunct could not fire, no matter how correct it was.
2. **A method's own `val` type and its `self.<m>()` CALL-SITE type are decided by two DIFFERENT
   functions.** `functions._compute_return_type` types the `val`;
   `functions._build_method_return_type_map` types the abstract op the caller applies. Patching one
   and reading the other is a guaranteed null result. Both carry the `-> str` disjunct; both needed
   the `bool` one.

**The rule.** Before concluding "X is not the decision point", put a one-line stderr probe INSIDE X
and print its inputs on the real file. It costs 30 seconds against an emit-only run (`--no-proof
--keep-mlw`, ~30s, no why3) and it is the difference between a measurement and a guess. And when a
type appears in two places in the emitted WhyML (a definition and its call site), assume two
producers until you have seen otherwise.

## Lesson (an) — promote a stub's return type to the FILE's convention, not to the source language's type

The obvious fix for a `\trusted` `-> bool` stub is `return_type = "bool"`. It type-checks the `val`
and then breaks everything downstream, because this emitter models a Python bool as the **int 0/1**
end to end: every CONVERTED `-> bool` method in the same mirror emits `: int`
(`_with_parenthesized`, `_looks_like_type_alias`), every boolean test lowers to `(<e>) <> 0`, and
the `Return` exception carries an int. A `bool`-typed stub is then the only bool-typed predicate in
the file, and the caller that was supposed to be fixed fails on `Return <bool>` instead.

Promoting to `int` also had a free dividend: `int` is in `_handle_dotted_call`'s admissible set for
the CONCRETE sibling application, so the call lowered to `(_parser___line_ends_with_colon self)` —
the real receiver-passing form — instead of a receiver-less `self__…_0 ()` facade.

**The rule.** Read what the CONVERTED siblings in the same file emit for the same Python type, and
match that. The annotation is the authority on WHAT the stub returns; the file's existing lowering
is the authority on HOW that is spelled.

## Lesson (ao) — the empty-list literal lowers to a 1024-long ZERO array, and it pattern-matches as an array argument

`[]` emits `(Array.make 1024 0)` (expressions.py, list-literal path) — the emitter's "no elements"
stand-in, which is neither empty nor typed by its use. Two consequences bit in the same increment:

* It starts with `"(Array.make "`, which is in `_handle_dotted_call`'s `ARRAY_INT_PREFIXES`, so
  passing `[]` to a callee INFERRED `array int` for a parameter the callee's own already-emitted
  `val` declares `int`. The first `_add_abstract_op` text wins, the two disagree, and the file
  fails L3-tc with `array int @rho but is expected to have type int`.
* Even with the inference fixed, the ARGUMENT still has to be coerced, or the same clash reappears
  at the application.

Both are gated on the EXACT placeholder literal, so a genuine array flowing into an int parameter
still fails loudly. Note what this is NOT: substituting the int witness `0` is not a new erasure,
because `(Array.make 1024 0)` is not `[]` either and the callee is a `\trusted` `val` with
`ensures true`.

## Lesson (ap) — a gap-free keyword binding does not have to reach full arity

Increment 13's keyword binder only applied when it could fill EVERY formal
(`len(_bound) == len(_formals)`). `self.funcdef([], async_=False)` against
`funcdef(self, decorators, async_, start=None)` binds slots 0 and 1 and leaves `start` unbound, so
the whole binding was discarded and the emitter fell back to the PARTIAL application
`(_parser__funcdef self <decorators>)` — the very defect increment 13 existed to fix. Accepting any
gap-free PREFIX (provided it covers every keyword, so none can be silently dropped) lets
`_handle_dotted_call`'s existing R7 default fill complete the tail from the callee's own defaults,
which is exactly Python's rule.

**The rule.** When a fail-closed guard is written as "all or nothing", check whether "as much as is
unambiguous, then hand off to the next stage" is equally safe. Here it was, and the all-or-nothing
form was silently re-introducing the erasure it was written to prevent.

## Lesson (aq) — an `Optional[τ]` local built by a TERNARY is not the same shape as one built by `= None` + reassignment, and it fails SILENTLY

The campaign's `Optional[ExprIR]` local carrier (relaunch #6 increment 5) handles exactly one
source shape:

    val: Optional["ExprIR"] = None        # PEP-526 annotation at the top of the body
    if <cond>:
        val = self.testlist()             # conditional REASSIGNMENT

`_sequence_pattern` has the other shape, and it defeats the carrier twice over:

    if <cond>:
        name: Optional[str] = None if nm.string == "_" else nm.string
    else:
        self.error(...)                   # diverges
    elts.append(self._fin(_N("MatchStar")(name=name), star_t))

1. **The ternary's `None` arm erases INSIDE the Some arm.** The emission is
   `Arm_9_0 (if str_eq_op (!nm)._tok_string "_" then "" else (!nm)._tok_string)` — the union
   constructor is applied to the WHOLE ternary, so the absent name became the EMPTY STRING and
   `case [a, *_]` would have modelled as carrying a name of `""`. The arm selection has to happen
   per-ternary-branch (`Arm_None` / `Arm_0 v`), and it does not.
2. **The annotated local is BRANCH-SCOPED** (lesson (ah) again): `let name = ref … in ()` inside
   the `if`, then `unbound function or predicate symbol 'name'` at the use site after it. The
   working shape never hits this because its annotation sits at the TOP of the body.

Reopening capability, named: lower an `IfExpr` with a `None` arm assigned to an `Optional[τ]`
local to the union's arm constructors per branch, AND pre-declare such a local at function top
rather than let-binding it where it is first assigned.

## Lesson (ar) — a CONCRETE sibling application coerces its arguments against `_resolve_dotted_signature`, which does not resolve `Optional[τ]` PARAM types

`async_stmt` is three passthroughs and an error, and every callee already has its return
interface — it should have been free. It is not: `self.funcdef([], async_=True, start=t)` passes a
real token into `start`, and

* leaving `start` un-annotated makes the `val`'s parameter `int`, so the `_tok` actual ill-types;
* annotating it `Optional["_Tok"]` makes Module5 synthesize a `_union_funcdef_9`, the `val`'s
  parameter becomes that union — and the ARGUMENT is still emitted bare, because
  `_handle_dotted_call` coerces against the `param_types` that `_resolve_dotted_signature`
  returns, and that function does not resolve a synthesized-union parameter type. A coercion arm
  added to `_coerce_dotted_args` therefore never fires.

Reopening capability, named: `_resolve_dotted_signature` must resolve a `_union_*` (i.e.
`Optional[τ]`) PARAMETER type, at which point the `Optional`-actual coercion arm (present actual →
the variant's unique arity-1 arm; omitted/None → its nullary arm) can do its job.

**And the tempting shortcut is the wrong one.** Coercing the token actual to the int witness `0`
because the parameter is int-erased anyway is exactly the class of defect lesson (al) describes: it
would make the verified artifact model an argument the source does not pass. `[]` → `0` was
admissible because `(Array.make 1024 0)` is not `[]` either — there was no faithful value being
discarded. A real token is a faithful value. Refused.

## Lesson (as) — a QUOTED forward-reference `Optional["X"]` synthesizes a union with the Some arm MISSING, and it fails SILENTLY

`funcdef(self, decorators, async_, start=None)`'s `start` was annotated `Optional["_Tok"]`
in the mirror stub — the quoted spelling, because that is what `-> "ExprIR"` interfaces use.
Module5 synthesized the per-function union and emitted

    type _union_funcdef_10 = Arm_10_None

— **the Some arm is simply absent**. No warning, no decline; the type exists, and the only
symptom is at the CALL site (`This expression has type _tok, but is expected to have type
_union_funcdef_10`), which reads like a coercion gap rather than a missing constructor.
`_variant_types['_union_funcdef_10']['constructors']` really does contain only
`Arm_10_None`, so any coercion arm keyed on "the union's unique arity-1 arm" finds nothing
and declines.

The UNQUOTED spelling `Optional[_Tok]` — which the same file already uses on
`accept_op`/`accept_kw` — does not go down the union path at all: Module5 tags it
`option:_Tok` and Module6 renders the native `option _tok`. That is the working shape.

**Rule.** For a RETURN interface the quoted forward reference is right (`-> "ExprIR"`). For
an `Optional[<class>]` PARAM, use the UNQUOTED class name, and read the emitted `type
_union_*` line before believing any coercion diagnosis. Quoted works for `Optional[str]`
(the payload is a builtin) — it is specifically a quoted CLASS reference that loses its arm.

## Lesson (at) — `_param_type_str` and `_build_method_param_types_map` are TWO PRODUCERS of the same parameter type, and the repair belongs on the CONCRETE path only

The callee's real emitted `val` signature comes from `functions._param_type_str`. The types
a CALL SITE coerces against come from `functions._build_method_param_types_map` (via
`_resolve_dotted_signature`). They are computed independently and they disagree whenever
`_param_type_str` has a special arm that `_symtype_to_whyml` does not:

| symtype | `_param_type_str` (the val) | the registry (the call site) |
|---|---|---|
| `option:<R>` | `option <record>` | `int` |
| `list` + `param_list_flat_elem = emit_ir` | `array emit_ir` | `array int` |

Lesson (am) in its purest form: "the coercion arm never fires" was a symptom of the
registry lying, not of the coercion.

**And the repair must be gated on CONCRETE resolution.** For a call that degrades to the
abstract self-call avatar (`self__<m>_<n>`), the registry IS the signature — the avatar's
`val` is generated from it — so "correcting" the registry there just moves the mismatch to
the argument. Measured: upgrading `_bool_ir_to_int_wrap`'s `Optional[BoolWrapIRView]` param
retyped the avatar to `option boolwrapirview` while the call still passed a bare `emit_ir`,
breaking `stmt_control_flow`'s L3-tc. Only a CONCRETE application (`(<cls>__<m> self …)`,
whose callee's `val` really is `_param_type_str`'s) can have two disagreeing producers, so
the upgrade uses the same `_module_func_names` + `_record_array_fields` /
`_sibling_concrete_methods` gate the concrete lowering itself uses.

**Corollary that paid for itself twice: a LIVE-ONLY method is free.** Neither fidelity
script compares a live method with no mirror counterpart, so a new helper on the live
mixin costs no re-port and no re-proof — which is how both of these repairs avoided the
§10.4 price of editing `_build_method_param_types_map` (an un-trusted mirror body:
`module6_whyml/functions`, 1175 goals, ~45 min + a vacuity tail).

## Lesson (au) — a function-top pre-declaration must be gated on the local ESCAPING its branch, and the gate has to be iterated against measurement

The `Optional[τ]`-local pre-declaration built for lesson (aq) was correct on the first try
and BYTE-INERT only on the third. Each version was measured with the 52-file mirror
emission sweep:

1. "pre-declare every union local whose assignment is nested" — moved THREE mirrors
   (`Module5_IREmitter`, `proof2why3/parser`, `pure_ast`).
2. "…and that is read by a LATER SIBLING at the same statement-list level" — still moved
   `proof2why3/parser`, whose `t = self.peek(0)` is assigned inside TWO successive `while`
   loops and read in both.
3. "…and the later sibling does NOT itself re-assign the local" — moves exactly ONE.

A later sibling that re-assigns rebinds the local in its own scope, so it is not an escape
and neither is anything after it. **The general rule: a capability that changes where a
binding is emitted must be gated on the DEFECT (the use that cannot see the binding), never
on the SHAPE (a nested assignment) — and the difference between the two is only visible in
the sweep.**

## Lesson (av) — converting one member of a recursive-descent chain makes its whole Why3 `let rec … with …` group need a VARIANT, including members that were already green

Twice in one window, a conversion that type-checked and looked finished failed its FIRST
proof on goals the converted function does not even mention:

* converting `factor` put it in a group with the ALREADY-CONVERTED `power` → three
  unproven `'vc` **termination** sub-goals;
* converting `lambdef` put it in a group with the ALREADY-CONVERTED `test` → an L3-tc
  error before that (`All functions in a recursive definition must use the same
  well-founded order for the first component of the variant`), then two unproven
  `_parser__lambdef'vc` sub-goals.

While a callee is a `\trusted` `val`, the caller is not recursive and Why3 asks nothing.
The moment the callee becomes a `let`, the pair is one mutual group and EVERY member needs
a measure — in the SAME well-founded order.

**The measure is the `proof2why3/parser` phase-offset form**, and the offset is decided by
the calls that do NOT move the cursor:

    factor  : 2 * (\length(self.toks) - self.i) + 1     # calls power without advancing
    power   : 2 * (\length(self.toks) - self.i) + 0     # calls factor only after advance()
    test    : 2 * (\length(self.toks) - self.i) + 1     # calls lambdef without advancing
    lambdef : 2 * (\length(self.toks) - self.i) + 0     # calls test after advance()+expect

**And the variant DECREASE chains through the callees' monotonicity clauses exactly like a
postcondition does.** `lambdef`'s two unproven sub-goals were its postcondition AND its
variant decrease, both fixed by the ONE missing `ensures self.i >= \old(self.i)` on
`lambda_parameters`. Budget one extra proof round per chain conversion, and read the
sub-goal NAME: `postcondition` means a missing callee clause, `variant decrease` means the
same clause is missing on a callee reached before the recursive call.

## Lesson (aw) — a dispatcher can be blocked by its SIBLINGS' already-converted return types (HETEROGENEOUS CONVERTED RETURNS)

`small_stmt` is a 13-way dispatcher and every arm was reachable — the three
`node("Pass"/"Break"/"Continue", t)` singletons build real nodes once the `node` helper is
recognized, and the other ten are sibling passthroughs. It is blocked anyway, and not by
anything in its own body:

    This expression has type PyCSL_Program.py_return @rho,
    but is expected to have type PyCSL_Program.emit_ir

Five of its siblings (`return_stmt`, `raise_stmt`, `assert_stmt`, `import_stmt`,
`import_from`) were converted EARLIER with HARVESTED PER-CLASS RECORD returns (`-> "Return"`
emits the record `py_return`), while a dispatcher must return the `emit_ir` SUM — and WhyML
has no type for a function whose arms return different types.

**This is a new KIND of wall: the blocker is a past CONVERSION, not a `\trusted` stub.** Two
consequences worth carrying:

1. When a class of nodes can appear in a dispatcher's result position, convert it onto the
   SUM (`_PYAST_IRNODE_CTORS`) from the start, not onto a harvested record. The record is
   right only for a node that is always consumed at a known type.
2. Repairing it is COST/SCALE, not correctness, and the count does NOT move until the LAST
   of the five re-ports lands — a migration whose entire yield is one conversion at the end.
   Named reopening capability: `IrPyReturn iropt_ir`, `IrPyRaise iropt_ir iropt_ir`,
   `IrPyAssert emit_ir iropt_ir`, `IrPyImport irlist`, `IrPyImportFrom iropt_str irlist int`,
   plus `alias` (their child) on an arm.

## Lesson (ax) — a CORRECTNESS boundary on a CALLEE does not propagate to its CALLER

The relaunch-#7 handoff recorded that `for_stmt`/`with_stmt` were blocked because they
"need `_for_target`/`_with_item`, which are behind the `_set_ctx` CORRECTNESS boundary".
Both converted in twenty minutes. They never needed those stubs CONVERTED — only their
INTERFACES (`-> "ExprIR"` plus `ensures self.i >= \old(self.i)`).

A caller needs a callee's TYPE and FRAME. It needs the callee's VALUE SEMANTICS only if it
inspects the returned value, which a recursive-descent parent almost never does — it just
threads the node into a constructor slot. So when triaging a wall, ask which of the three
the caller actually consumes before recording the callee's boundary as the caller's.

## Lesson (ay) — a CONVERSION can land, prove, and pass every gate while NO CALLER can see its body (SHADOWED SELF-CALL)

`check-untrusted-emitted.py` asks whether an un-trusted function is EMITTED AS A
DEFINITION rather than re-abstracted to a `val`. That is necessary and **not
sufficient**. Module 6 lowers `self.<m>(...)` two ways:

* the CONCRETE sibling application `(<class>__<m> self args)` — the caller gets the
  callee's real body and contract; and
* a synthesized receiver-less abstract op `val self__<m>_<n> … : <ret>`, whose result is
  **unconstrained**.

`expressions._handle_dotted_call` picks the concrete route only when the callee's resolved
return type is in an ALLOWLIST — `emit_ir`, `int`, `string`, `_union_*`, or a declared
record. **`array <t>` was missing.** So every method returning `List[τ]` took the abstract
route, and the consequence is invisible to every plane:

    let  _parser___if_tail (self: _parser) : array emit_ir  = …real body, PROVED…
    val  self__if_tail_0   (self: _parser) : array emit_ir      ← what if_stmt actually calls
    …
    let orelse = ref (snapshot (self__if_tail_0 self)) in

`if_stmt` is converted and proven; its `orelse` child is an ARBITRARY array. The `let` is
emitted (untrusted-emitted GREEN), the proof succeeds, the corpus byte-diff is 0, fidelity
is unchanged, field parity is unchanged, and emitted-vacuity sees nothing — the erasure is
not in any FUNCTION's parameters, it is in the CALL EDGE between two of them.

This is **not unsound** — an unconstrained result is an over-approximation, exactly like a
`\trusted` stub. It is a **LOST CONVERSION**: the proof was paid for and the faithfulness
gain never reached a caller. The `\trusted` count moves, the model does not.

MEASURED CAMPAIGN-WIDE (2026-08-28, 52 mirrors): **55 converted methods, 267 call sites,
ZERO concrete applications** — including the whole pure_ast STATEMENT CLUSTER (`block`,
`statement`, `_if_tail`, `_else_block`, `_import_as_names`) and Module 5's `_csl_to_ir`
(92 sites) and `_py_expr_to_ir` (44).

Two things follow:

1. **A new oracle exists and is now wired**: `bin/check-shadowed-selfcalls.py` counts
   exactly this and ratchets at 55. Run it every increment alongside
   `check-untrusted-emitted.py`; the two answer DIFFERENT questions.
2. **Adding `array <t>` to the allowlist is a two-producer change** (lesson (am) again) —
   BUILT AND LANDED the same day; the numbers below are the measurement that motivated it,
   and the gate now ratchets at 50 / 259.
   The twin is `Module6_WhyMLTranspiler._record_return_sibling_methods`, which supplies the
   SCC callee-before-caller ordering edge; without it the newly-concrete application is
   emitted before its callee is declared (measured: `unbound function or predicate symbol
   '_parser__block'`). With BOTH halves in place pure_ast's fourteen statement-cluster
   methods collapse into ONE Why3 `let rec … with …` group and the file fails L3-tc with
   `All functions in a recursive definition must use the same well-founded order for the
   first component of the variant` — lesson (av) at fourteen-member scale. The reopening
   capability is therefore NAMED AND COSTED: a phase-offset variant
   `M*(\length(self.toks) - self.i) + off` over the whole cluster with `M > max off` and
   `off(statement) > off(decorated) = off(async_stmt) > off(<compound handler>)`, because
   `statement` dispatches WITHOUT advancing, `decorated` may take its `@`-loop zero times
   as far as the prover knows, and `async_stmt`'s leading `advance()` only moves the cursor
   when the class invariant rules out the last index.

### (ay) RESOLVED for the `array <t>` half — what it cost

Both producers, then the variant work:

* `expressions._handle_dotted_call`: `array <t>` added to the concrete-sibling allowlist.
* `Module6_WhyMLTranspiler._record_return_sibling_methods`: the same predicate, because it
  supplies the SCC callee-before-caller ordering edge. Without it: `unbound function or
  predicate symbol '_parser__block'`.
* Then pure_ast's FOURTEEN compound-statement parsers become ONE `let rec … with …` group
  and every member needs the same well-founded order. The phase-offset assignment that
  works, multiplier **3** because the cluster is three levels deep:

      statement                                        3*(N - self.i) + 2
      block, decorated, async_stmt                     3*(N - self.i) + 1
      if_stmt while_stmt for_stmt try_stmt with_stmt   3*(N - self.i) + 0
      funcdef match_stmt case_block _if_tail _else_block

  `statement` dispatches to a handler WITHOUT advancing, so it must sit above them.
  `decorated` may take its `@`-loop zero times as far as the prover knows and `async_stmt`'s
  leading `advance()` only moves the cursor when the EOF-sentinel invariant rules out the
  last index — so both sit above the handlers they call. A handler reaches `block` only
  through `expect_op(":")`, whose UNCONDITIONAL `ensures self.i > \old(self.i)` pays for the
  offset RISE. `block` reaches `statement` only after consuming NEWLINE and INDENT, neither
  of which is ENDMARKER, so the class invariant makes both `advance`s strict.

  **It proved on the FIRST attempt** — 1460 Valid / 0 non-Valid (1363 before). Budget one
  authoring pass, not the usual extra proof round, when every offset rise is already paid
  for by an `expect_*` strictness clause you can point at.

Blast radius, measured: **2 of 52 mirrors** changed emission — pure_ast and
`frontend/Module2_Parser` (whose `_parse_act_names` / `_parse_opt_except` were shadowed the
same way). Both re-proved SEQUENTIALLY (lesson (ai)), 1460 and 714 Valid, 0 non-Valid.
Corpus byte-diff 0/813: the `_record_array_fields` proxy gate holds it off every corpus
program.

**The residue is the OTHER admission gate, not the type.** The remaining 50 are shadowed
because `_handle_dotted_call` admits the concrete route only when `_record_array_fields` is
non-empty OR the callee carries an explicit `#@ sibling_concrete` marker — and the emitter
mirrors (`statements`, `stmt_control_flow`, `expressions`, `functions`, `types`) have no
List-of-record field, so the proxy gate is empty for them even though their callees return
`string`/`int`, types that have been in the allowlist all along. Named reopening capability:
replace the `_record_array_fields` PROXY with a direct one, or mark the callees.

## Lesson (az) — `_Parser.trailers` is a FOUR-PIECE cost/scale boundary, and the pieces are the general ones

`trailers` looked like a one-hour port: three arms, every callee already interfaced, and the
POSITION-ATTRIBUTE plane already handled (`n.lineno = start_line` emits `();` — the model
carries no position payload, exactly as `_fin` / `_fin_pos` are already elided; `_subscript`
was converted on that basis). It is blocked by FOUR separate emitter gaps, each measured in
a 30-second emit run:

1. **A reassigned `emit_ir` FORMAL PARAMETER is never shadowed as a ref.** `trailers`'s
   accumulator IS its parameter (`atom = n`). `typed_local_vars` contains `atom`, and every
   pre-declaration set excludes `self._formal_params`, so no `let atom = ref atom in` is
   emitted; the reassignment lowers to a BRANCH-SCOPED `let atom = ref !n in ()` that is
   discarded at the end of the branch, and the body's `!atom` reads are ill-typed against
   the immutable binder (`This expression has type PyCSL_Program.emit_ir, but is expected
   to have type ref 'mu`). BUILT AND MEASURED WORKING in the spike: add the assigned
   `emit_ir` params to `pre_decl_vars` but NOT to `_emit_ir_predecl`, so the initializer
   falls through to the existing `init = safe_var if var in self._formal_params else pfx`
   branch — the `(IrOther "")` sentinel would silently ZERO the incoming node.
2. **A TUPLE-OF-LISTS return is int-erased.** `args, keywords = self._call_args(")")`.
   BUILT AND MEASURED WORKING: `-> "Tuple[List[ExprIR], List[ExprIR]]"` recognized in BOTH
   producers (`functions._compute_return_type` and `_build_method_return_type_map`, lesson
   (am) yet again) gives `val self__call_args_1 … : (array emit_ir, array emit_ir)`.
3. **The tuple-unpack TARGETS are not typed from the callee's tuple return.** `args` and
   `keywords` still pre-declare `ref 0`, so the correctly-typed pair cannot be stored.
   NOT BUILT.
4. **The `irlist` payload binder does not accept an `array emit_ir` local.** Even typed, the
   `Call` arm's `args`/`keywords` slots need `seq_to_irlist (snapshot !args)`. NOT BUILT.

Recorded as **CERTIFIED-BOUNDARY [COST/SCALE]** — every piece is mechanical and named, none
is a correctness or value-model limit. Pieces 1 and 2 were REVERTED WITH THE SPIKE rather
than left as dead capability; they are worth rebuilding only together with 3 and 4, in one
increment that ends in `trailers` converting. Two new arms were written and reverted with
them: `IrPyCall emit_ir irlist irlist` and `IrPySubscript emit_ir emit_ir string`.

**And the transferable part**: the position-attribute plane is NOT a wall. `n.lineno = …`
already emits nothing, because `emit_ir` has no position payload — the same pre-existing
decision that makes `_fin` an elision. Do not record a position write as a blocker; it is
only `ctx` (a MODELLED field, lesson on `_set_ctx`) that cannot be dropped.

## Lesson (ba) — an `Optional[<record>]` LOCAL is a different, unsupported shape from `Optional[<emit_ir>]`

`_line_ends_with_colon` scans the token array with a local cursor and keeps
`last_sig: Optional[_Tok] = None`, then tests `last_sig is not None and last_sig.type ==
_tokenize.OP`. The `_union_*` carrier the campaign built for `Optional["ExprIR"]` (which
gives a real `Arm_2_0 emit_ir | Arm_2_None` and a TRUE absent value) does NOT fire for a
RECORD element type. Measured emission:

    last_sig := 0;                                        (* int-erased *)
    …
    (if (!last_sig <> 0) && ((get_type !last_sig) = 55) && ((get_string !last_sig) = 424321936) …

— an opaque `get_type`/`get_string` pair over an int, and the `":"` comparison collapsed to
a STRING HASH. Refuted in one 30-second emit run; spike reverted clean. Reopening
capability: extend the synthesized `_union_<fn>_<n>` carrier to a declared RECORD arm
(`Arm_n_0 _tok | Arm_n_None`), which is the same construction one type-class over.

## Lesson (bb) — a change's HOME is decided by the mirror's fidelity obligation, not by where it "belongs"

`trailers` needed a `-> "Tuple[List[ExprIR], List[ExprIR]]"` return type honoured by BOTH
Module6 return-type producers (lesson (am)). The obvious edit — one branch in
`_compute_return_type`, one in `_build_method_return_type_map` — was made, and
`bin/check-self-annotate-sync.sh` immediately went from the standing **2 DIVERGED to 4**:
both of those methods are CONVERTED in the mirror, so a live-emitter edit to either is a
FIDELITY-plane failure until the identical text is ported into
`src/self-annotate/src/module6_whyml/functions.py`.

The fix was not to port twice. **`_refine_tuple_return_type` is called by BOTH producers**,
so ONE insertion there serves them both — the two-producer trap paid once, and only ONE
converted mirror body had to change (and be re-proved).

Two corollaries worth carrying:

* **Run `check-self-annotate-sync.sh` immediately after ANY live-emitter edit**, before
  spending proof time. It costs seconds and it told me the edit was in the wrong place.
* The mirror body must be EMITTABLE, not merely equal. The first port used
  `return func.get("return_tuple_whyml")`, which lowered to
  `raise (Return_str (Map.get func …))` — an `hval` in a `string` position, L3-tc REJECTED.
  Rewriting it as `if func.get(K) == "<literal>": return "<literal>"` routes the read
  through the certified `hstr_of` projector and returns a real literal — provable, and
  strictly MORE faithful (the equality pins the returned literal to the recorded value).

## Lesson (bc) — the shadowed-selfcall gate is fixed by MARKING CALLEES, and the proxy-gate spike is a finding in its own right

`_handle_dotted_call` admits the CONCRETE sibling lowering on two routes: a non-empty
`_record_array_fields` (a PROXY that holds only for the parser-cursor shape) or the opt-in
`#@ sibling_concrete` marker. The emitter mirrors have no List-of-record field, so ~40
CONVERTED, PROVED methods had EVERY call site going through the receiver-less abstract
`val self__<m>_<n>` (lesson (ay)).

**The spike, done first and reverted: dropping the proxy disjunct outright changes only 6
of 813 corpus files, and every one of those six replaces an opaque abstract `val` with the
real concrete application** — including two where the abstract route had SILENTLY DROPPED
the callee's `requires self.session_authenticated = 1`. That is a genuine faithfulness hole
in the LIVE TOOL, but fixing it changes emission for USERS, not just the mirror, so it is
FLAGGED FOR THE USER rather than taken by a self-TCB-reduction increment.

What the campaign takes instead is the other route: **mark the callees.** Corpus byte-inert
BY CONSTRUCTION (no corpus program writes the directive), and `scc.find_self_method_calls`
already supplies the callee-before-caller ordering edge for a marked callee.

**Method that worked: cumulative per-file triage.** Mark one method, run the 1-second emit
oracle, KEEP on L3-tc, UNMARK on failure, move on. 26 markers tried, 15 effective; the 11
that emitted cleanly but did NOT remove their `val` were REMOVED rather than left as dead
annotation. Result: shadowed **50 -> 35 methods, 259 -> 208 call sites**.

**Four reasons a marker cannot fire — each a named boundary, not a grind:**

1. **`Optional[<τ>]` return compared to a bare value at the CALL SITE.** `_field_type_of`
   is used as `self._field_type_of(x) in ("list","tuple")`. The abstract route returned
   `int`, so the int-hash comparison type-checked (badly); the concrete route hands back the
   real `_union__field_type_of_1` and the comparison is REJECTED. Reopening: union-vs-value
   comparison at the call site. This is the SAME `_union_*` capability family as lesson (ba)
   and it is worth 14 call sites across `statements` and `types`.
2. **A SELF-RECURSIVE callee** (`_rhs_yields_map`) becomes a real `let rec` under the
   concrete route and needs a `#@ \variant` it does not declare.
3. **A `@staticmethod` can never take the concrete route**, which passes `self` as the first
   argument — correctly fail-closed, and the reason four candidates dropped.
4. **An arity-0 `-> None` bridge** (`_materialize_bridge`) has no admissible return type.

**And the blast radius is second-order**: marking a method in a MIXIN re-emits every mirror
that mixes it in. Measure it with the mirror sweep — `Module6_WhyMLTranspiler` and `pycsl`
both changed and both had to be re-proved.

## Lesson (bd) — a conversion that moves a hole from a COUNTED register to an UNCOUNTED one is count theatre; decline it

`_fin` (the pure_ast parser's position stamper) converts cleanly. The full spike was built
and measured GREEN: the position-write elision extended from an emit_ir LOCAL to an emit_ir
FORMAL PARAM, a ternary arm reading an `array <record>` self-field element typing the local
as that record, the emitted body coming out as the literal identity on `node` with NO call
site moved, and `frontend/pure_ast` proving **1612 / 1612**.

It was reverted anyway. `bin/check-emitted-vacuity.py --emit` reported

    _parser___fin  erased=['start_tok'] of ['node', 'start_tok', 'end_tok']

and it is RIGHT: `_fin`'s only use of `start_tok` is to write two of the four ASDL location
attributes, `emit_ir` carries no position payload (lesson (az)), so with the stamps elided
the model really does ignore that input.

So the conversion would have TRADED a **counted** `\trusted` marker for an **uncounted**
known-erasure ledger entry — and bought nothing, because every call site ALREADY elided
`_fin`. No caller would see one thing it did not see before. **Decline that trade.** The
marker count is a proxy for trust removed; growing the erasure ledger to shrink it is
moving a hole from one register to another.

Corollaries:

* **Revert the spike's capabilities WITH it.** The two emitter extensions `_fin` needed
  fire nowhere else, so keeping them would be dead capability (the same discipline lesson
  (az) applied to the `trailers` pieces).
* Reopening capability, named: an `emit_ir` that CARRIES the four location attributes as
  payload — the same decision `_set_ctx` needs one field over.
* Generalisable test before porting ANY body: *what would a caller see that it cannot see
  today?* If the answer is "nothing", the conversion is bookkeeping.

## Lesson (be) — a class name chosen at RUN TIME lowers to a dispatch DERIVED FROM THE TABLE, with an EXACT tail

`global_stmt(self, kind)` builds `_N(kind)(names=names)` where `kind` is a `str` FORMAL
PARAMETER — the caller passes the literal `"Global"` or `"Nonlocal"`. Neither of the two
existing recognizers fires: it is not a string literal, and it is not the ternary
class-name LOCAL (`cls = "TryStar" if is_star else "Try"`).

The lowering that works, and stays drift-proof:

    (let _cnk = kind in
      (if (str_eq_op _cnk "Global")   then (IrPyGlobal !names)
       else (if (str_eq_op _cnk "Nonlocal") then (IrPyNonlocal !names)
             else (IrOther _cnk))))

Two things make it honest:

1. **The candidate set is DERIVED, never hand-written**: exactly those
   `_PYAST_IRNODE_CTORS` entries whose payload FIELD-NAME SET equals the construction's
   KEYWORD set. Add or remove a family member, or drift an ASDL field name, and the chain
   follows automatically — the drift-proof-table discipline the handoff asked to be weighed
   is *satisfied*, not traded away.
2. **The tail is EXACT, not a fallback.** `kind_of (IrOther k) = k`, so off the candidate
   set the model says "a node whose kind is precisely this string". It never names a WRONG
   class. (Python raises `KeyError` there; it is unreachable from every call site.)

And the payload type matters: `Global.names` is a list of IDENTIFIER STRINGS, so the slot is
the `seq string` payload the `Compare.ops` arm introduced — **not** `irlist`, which would
model an identifier as a NODE.

## Lesson (bf) — the OPTIONAL-ELEMENT child list, and the sharpened erasure-ledger test

Two recorded boundaries (`atom_list` / `atom_brace` / `atom_paren` / `_dict_rest`) named two
missing payload shapes. Both are now built, and each answer is worth carrying.

**1. A list of harvested RECORDS cannot be a payload — the class must JOIN THE FAMILY.**
`GeneratorExp.generators` is a list of `comprehension` nodes, and the obvious move is a
`seq comprehension` payload slot (the `Compare.ops` arm already carries a `seq string`). It
does not type: `comprehension` holds `emit_ir` children, so `seq comprehension` INSIDE
`emit_ir` is non-strictly-positive and Why3 rejects the recursion outright. The answer is to
add `comprehension` as an ADT ARM (`IrPyComprehension emit_ir emit_ir irlist int`) and retype
its producer `comp_for` to `-> "List[ExprIR]"`; the clause list is then an ordinary `irlist`.
That single move freed `_call_args`, `atom_list` and `atom_paren`.

**2. A list with `None` ELEMENTS needs its own carrier.** `Dict.keys` really holds `None`
(`{**a, 'k': v}` parses to `keys=[None, 'k']`). An `irlist` would have to model the absent key
as a NODE — the sentinel the whole `iropt_*` family exists to remove. The carrier is

    with iroptlist = IONil | IOCons iropt_ir iroptlist

bespoke for the same reason `irlist` is, with DEFINED `iolen`/`ionth` and a pointwise-pinned
`seq_to_iroptlist` bridge (no axiom, no new leaf). Three emitter sites make a local carry it:
a prescan marks a seq local that receives a BARE `None` append, and its literal initialiser
and its appends both wrap (`IrOSome` / `IrONone`).

**3. THE SHARPENED TEST for the known-erasure ledger.** Lesson (bd) declined `_fin` because
its conversion moved a hole from the COUNTED `\trusted` register to the UNCOUNTED erasure
ledger. `_dict_rest` erases `t` for the IDENTICAL reason (location-only, `_fin_pos`'s
`start_tok`) and WAS admitted. The distinction is not the erasure — it is **what a caller
gains**:

* `_fin`'s ENTIRE body is location work, and every call site already elided it. A caller
  would see nothing new. Bookkeeping. **Decline.**
* `_dict_rest` parses the whole `{**a, k: v}` dict tail, and `atom_brace` calls it
  CONCRETELY. The conversion puts a real `IrPyDict` with real keys and values where an
  UNCONSTRAINED abstract `val` stood. **Admit, and record the entry with its reason.**

So: *convert when the body does real work beyond the erased input; decline when the erased
input is essentially all the body does.* And when you admit one, write the mechanical check
(an AST scan showing the parameter's only use) into the ledger entry, as
`_parser___sequence_pattern` already does.

## Lesson (bg) — converting one member can put SIXTEEN functions in one `let rec`, and the variant multiplier must exceed the deepest NO-ADVANCE chain

`_binop` is the precedence-climbing core of the expression parser. All three of its VALUE
facades were built and measured working (a third module-const-dict family member,
`str -> (str,int)`; see the refutation commit). The conversion still did not land, and the
reason is worth carrying:

    All functions in a recursive definition must use the same well-founded order
    for the first component of the variant

Converting `_binop` closes the cycle

    expr -> _binop -> factor -> power -> await_expr -> unary_postfix -> trailers ->
    _call_args -> test -> or_test -> and_test -> not_test -> comparison -> expr

so Why3 groups SIXTEEN functions into one `let rec … with …`. Four of them carry a
`#@ \variant` today, all at multiplier 2 (`2 * (\length(self.toks) - self.i) + 1/0`).

**The rule (lesson (av), sharpened): the multiplier must EXCEED the deepest NO-ADVANCE
chain in the group, because an edge that does not move the cursor can only be paid for by
a strictly smaller OFFSET.** The statement cluster needed multiplier 3 for a 3-deep chain.
The expression group's chain above is ~12 hops with no guaranteed advance, so it needs
multiplier ~13 and offsets assigned by TOPOLOGICAL DEPTH in the call graph — and every one
of the sixteen has to be re-phased together, in one increment.

Two practical consequences:

* **Before porting a body in a recursive-descent parser, ask which cycle it closes.** The
  emit oracle tells you in one second: if the emitted `let rec … with …` grows, you owe a
  variant to every new member.
* **A group re-phasing is a first-class increment, not a tail-of-session patch.** Sixteen
  interdependent clauses and a ~35-minute proof per attempt. Land it with fresh budget.

## Lesson (bh) — the group re-phasing, executed: cost the cycle, not the function, and L3-tc prices the variant for free

Lesson (bg) recorded `_binop` as CERTIFIED-BOUNDARY [GROUP VARIANT RE-PHASING] and named
the reopening capability. Relaunch #11 executed it and `_binop` CONVERTED. Three things are
worth carrying.

**1. THE ORDER IS DECIDED BY THE CYCLE'S ONE ADVANCING EDGE, and you can find it by hand.**
The sixteen-member expression group has exactly ONE cycle,

    test -> or_test -> and_test -> not_test -> comparison -> expr -> _binop -> factor ->
    power -> await_expr -> unary_postfix -> trailers -> _call_args -> test

and exactly ONE of its thirteen edges provably moves the cursor: `trailers -> _call_args`,
which consumes the opening delimiter (`at_op("(")` then `advance`, strict by the EOF
sentinel). Every other hop must therefore be paid for by a strictly SMALLER OFFSET, so the
offsets are the topological distance BACKWARDS from that edge and the multiplier must exceed
the deepest one:

    _call_args 12 · test/comp_for/or_test_no_cond 11 · or_test/lambdef 10 · and_test 9 ·
    not_test 8 · comparison 7 · expr 6 · _binop 5 · factor 4 · power 3 · await_expr 2 ·
    unary_postfix 1 · trailers 0,  all at `13 * (\length(self.toks) - self.i) + <depth>`

The three members OFF the cycle (`lambdef`, `or_test_no_cond`, `comp_for`) are placed by the
same rule, and every offset-RAISING edge in the whole group is paid by an unconditional
strict advance: `trailers -> _call_args` (the `(`), `lambdef -> test` (`expect_op(":")`),
`power -> factor` (the `**`), and each self-recursion (which sits behind its own `advance`).
Read the call graph, find the advancing edge, count backwards. It is a ten-minute analysis,
not a search.

**2. L3-tc PRICES THE VARIANT SHAPE IN ONE SECOND; only the DECREASE costs proof time.**
"All functions in a recursive definition must use the same well-founded order" is a
TYPE-CHECK error, so the 1-second emit oracle tells you whether the re-phasing is even
admissible before any prover runs. Use it to converge the SHAPE first, then spend the one
35-minute whole-file proof on the decrease VCs. (`--fun` is NOT an alternative here: slicing
a mutual-recursion group breaks it — the sliced group re-emits as `unbound function symbol`
or `unexpected 'variant' clause`. A group is proved whole or not at all.)

**3. SPIKE THE TERMINATION QUESTION WITH A PLACEHOLDER BODY.** The variant question depends
only on the CALL GRAPH, so a deliberately simplified `_binop` body that closes the same cycle
answers it without building one line of emitter capability. That is the refutation exit for a
group re-phasing, and it is cheap.

**And one hygiene rule the increment paid for: a projection lever that BYPASSES an opaque
abstract op must also stop REGISTERING it.** The pair-dict unpack replaced
`subscript_get_t2` with faithful per-slot ITEs, but the `elif val_ir["type"] == "Subscript"`
arm still called `_add_abstract_op`, leaving a DEAD `val subscript_get_t2 (x: int) (i: int) :
(int, int)` in the emission — TCB surface for a symbol nothing applies. Guard the registration
on the same condition that guards its use. Measured the right way: diff the emitted file's
`val` SET against the baseline's. After the guard the whole diff is one line —
`val _parser___binop` REMOVED, zero added.

## Lesson (bi) — `#@ sibling_concrete` makes a self-call REAL recursion, and a `kind_of` string guard cannot pay for it

The shadowed-selfcall gate is fixed by MARKING CALLEES (lesson (bc)). Relaunch #11 took
32 methods / 192 sites down to 27 / 176, and both halves of that are worth carrying.

**1. A `#@ sibling_concrete` method that calls ITSELF becomes a real `let rec`, and the
emitter did not know it.** `IRScanner.is_recursive` matches the IR name (`<cls>__<m>`) or
the bare name, but a self-call's IR node carries the DOTTED `"self.<m>"` — exactly the miss
`scc.py`'s `find_self_method_calls` documents for the ORDERING graph, never fixed for the
EMISSION side. So a marked self-recursive callee emitted as a plain `let` whose body
referenced itself: `unbound function or predicate symbol
'statementemissionmixin___rhs_yields_map'`, an L3-tc failure that reads like "the marker
does not work" and was recorded that way. Resolve the dotted form the same way the SCC
does, gated on the opt-in marker. `use_rec` AND the injected `variant { size <ir-param> }`
both follow from `is_recursive`, which is exactly what the emitted function then needs.

**2. `kind_of e = "K"` is not merely a slower guard than `is_K` — for a STRUCTURAL
RECURSION it is INSUFFICIENT, and the difference is a real value, not a prover mood.**
`_rhs_yields_map`'s ternary arm is `t = val_ir.get("type", ""); if t == "IfExpr": return
self._rhs_yields_map(val_ir.get("body", {})) or …`. Its `variant { size val_ir }` needs
`size (body_of val_ir) < size val_ir`, and the theory states that law as
`size_ifexpr_body_dec : forall e. is_ifexpr e -> …`. The string test does NOT imply
`is_ifexpr`: `IrOther "IfExpr"` satisfies `kind_of e = "IfExpr"`, and for THAT value
`body_of` returns the `IrOther ""` sentinel whose `size` is also 1 — the decrease is
genuinely FALSE. Measured as two 30-second, 62-MILLION-step Timeouts, which is what an
unprovable goal looks like from the outside.

**The sibling arm proved, and WHY it proved is the diagnostic trick.** `BinOp`'s guard
carries an extra conjunct — `op_of val_ir in {"|","&","^","-"}` — and `op_of` returns `""`
off `IrBinOp`, so a NON-EMPTY op PINS the constructor and `is_binop` follows. When one arm
of a two-arm structural recursion proves and its twin times out, look for the accidental
constructor-pinning conjunct rather than blaming the solver.

**3. The fix is a NARROW carve-out, not a wholesale flip.** The mirror deliberately keeps
the already-proven `kind_of` string path (the tier3 discriminant rewrite is gated `not
_mutable_state_classes`, with `is_K` deferred to a Phase 2); flipping that gate would
re-emit and re-prove every mirror. Instead the rewrite fires ONLY where the string path is
insufficient rather than merely different: the guard tests a LOCAL bound exactly once from
`<p>.get("type", …)`, and `<p>` is THIS function's own injected variant measure. Three
pieces — `_collect_kind_local_recv`, `_size_variant_param`, and the gated rewrite — and a
measured blast radius of 7 of 52 mirrors, 0 TC_FAIL, corpus byte-diff 0.

**4. The triage number to expect.** 23 methods tried on the 1-second oracle, 5 effective.
The 18 that failed split into the four recorded reasons plus one new one worth naming: a
`-> bool` callee emits as a `bool`-returning logic symbol while the call site coerces
`<> 0` for an int (`_is_final_annotation`) — a return-type coercion gap at the concrete
route, not a property of the callee. REMOVE the ineffective markers; do not leave dead
annotation.

## Lesson (bj) — the LITERAL-VALUE carrier, and a keyword argument that was silently replaced by the default

The f-string cluster (ladder 2's second half) gave up two of its three members. Three
things are worth carrying.

**1. `Constant.value` is the one Python-AST child that is neither a node nor a string, so
it needs its own carrier.** `ast.Constant` models EVERY literal — `"s"`, `3`, `3.0`,
`b"x"`, `True`, `None`. Typing the payload slot `string` would have been enough for the
f-string sites (their value is always a decoded `str`) and WRONG in the family sense: the
next site to convert is a number literal, and a table maps a class name to ONE arm, so a
`string` slot would have PINNED `Constant` to the string shape. The carrier

    with irconst = ICStr string | ICNone

names the literal's SHAPE instead, carries only what the converted sites build, and makes
every other value expression DECLINE — which is exactly what keeps `atom` /
`_pattern_number` / `closed_pattern` on their recorded [MODEL] boundary instead of
silently mis-modelling a number as a string. Childless for the `size` measure, so no size
arm and no decrease lemma. **When a family member's payload can be several unrelated
scalar shapes, carry the SHAPE, not one of the shapes.**

**2. A KEYWORD ARGUMENT ON A MODULE-LEVEL CALL WAS DROPPED AND THE DEFAULT EMITTED IN ITS
PLACE.** `_merge_str_constants(values, drop_empty=False)` emitted
`_merge_str_constants … 1` — the default `True`. The module-call path built its argument
list from POSITIONAL arguments only and then filled the trailing parameters from the
callee's defaults; `expr["keywords"]` was consulted for record/ADT constructors and nowhere
else. This is a WRONG-VALUE lowering, not a coarse one, and it is invisible unless you
look: the emitted term is well-typed and plausible.

**How it was caught, and the technique:** write the same call POSITIONALLY behind a
module-level probe constant and diff the emitted term. `f(x, kw=V)` emitting a different
argument than `f(x, V)` is the whole proof. Fixed generally (Python binds a keyword only to
a parameter no positional reached, so binding by name from `len(args)` onward IS Python's
rule) — and **the corpus byte-diff is 0 over 813**, so a genuine live-tool faithfulness
repair cost users nothing. Look for the same defect wherever an argument list is rebuilt
from positions.

**3. Where the cluster stops.** `_fstring_replacement` was ported and MEASURED, then
reverted with its `IrPyFormattedValue` arm (dead capability discipline). Its blocker is
`Optional[<node>]` / `Optional[str]` LOCALS: `format_spec = None` emitted as a bare
`ref (IrOther "")` and the guard `format_spec is None` lowered to the literal `false` — a
wrong branch condition. The synthesized `_union_*` treatment that `Optional[<record>]`
locals already have (lessons (ab)/(aq)) is the named reopening capability, plus a
tuple-typed parameter interface for `_slice(start, end)`, whose `(line, col)` actuals are
`pytuple_int_int` against an `int`-declared `val`.

## Lesson (bk) — a refutation that names its capability precisely can be reopened the same day; and a fix you cannot EMIT is not a fix

`_subscript_item` was recorded CERTIFIED-BOUNDARY [UNANNOTATED OPTIONAL-NODE LOCAL] and
converted about four hours later, by building exactly the capability the refutation named.
That is the whole argument for the discipline of naming the reopening capability at
refutation time rather than writing "blocked".

**1. THE OPTIONAL-NODE LOCAL, and why the gate is the SLOT.** A local BOUND INTO an
`iropt_ir` PAYLOAD SLOT of a `_N(<Class>)(...)` family construction IS an `Optional[<node>]`
— `ref IrONone` pre-decl, `IrONone` for the `None`, `(IrOSome e)` for a present value, the
slot binding the CARRIER itself, and a DEFINED total `iropt_val` projector for the one
position that reads it as a plain node. The obvious extra gate — "and it is assigned `None`
somewhere" — is both unnecessary (a local that flows into an optional slot is optional
regardless) and FRAGILE, for a reason worth its own entry below. Annotated
`Optional[τ]` locals are EXCLUDED: they already have a synthesized `_union_*` and taking
them over here would double-wrap them.

**2. A FIX YOU CANNOT EMIT IS NOT A FIX — lesson (bb), sharpened.** Module5's
`_py_stmt_assign` reads `stmt.targets[0]` only, so the SECOND AND LATER targets of a chained
assignment (`a = b = c = V`) are SILENTLY DROPPED — a real fail-open, the same shape as the
`p.x = v` no-op the file's own comment warns about. The repair is three lines (Python
evaluates the value ONCE and binds every target to THAT object, so `t0 = V; t1 = t0; …`) and
the corpus byte-diff is 0. **It was still reverted**, because the mirror's own emitted model
of `_py_stmt_assign` goes through the typed AST reader `assign_target0_ast`, which exposes
only `targets[0]`: the repaired body's new branch is silently dropped from the emission, and
the emitted `.mlw` was measured BYTE-IDENTICAL with and without the fix. A live change whose
mirror counterpart cannot be emitted does not get verified — it just widens the gap between
the body and the model. Flag it, name the reopening capability (`assign_targets_len` /
`assign_targetk_ast` in the reader model), and move on.

**3. A SECOND GROUP RE-PHASING, and the rule generalizes.** Converting `_subscript_item`
pulls `_subscript` and `test_or_star_slice` into the expression `let rec` group — NINETEEN
members — and deepens the no-advance chain from 13 hops to 15
(`_subscript -> _subscript_item -> test_or_star_slice -> test -> … -> trailers`). All
nineteen move to `16 * (\length(self.toks) - self.i) + <depth>`. **Expect the multiplier to
rise every time a new member joins**, and re-phase the whole group in one edit; the 1-second
emit oracle prices the shape before any prover runs (lesson (bh)).

## Lesson (bl) — the optional CARRIER pair, and why `x is None` on a sentinel-modelled local is a WRONG branch, not a coarse one

`_fstring_replacement` closes the f-string cluster's third member and completes a pair of
capabilities worth stating together.

**THE CARRIER PAIR.** An `Optional[<node>]` local is `iropt_ir` (`IrONone` / `IrOSome e`);
an `Optional[str]` local is `iropt_str` (`IrSNone` / `IrSSome s`). Each gets a `ref <None>`
pre-declaration, carrier-valued assignments, an `is None` guard that lowers to the carrier's
own `match … with <None> -> true | _ -> false` discriminant, and a DEFINED total projector
(`iropt_val` / `iropt_str_val`) for the ONE position that reads it as a plain node/string
under a guard that has just proved it present. No axiom; the ledger does not move.

**THE GATES ARE DIFFERENT, and each is right for its type.** The node carrier is gated on
the SLOT alone — a local bound into an `iropt_ir` payload slot IS an optional node. The
string carrier ALSO requires a `None` assignment, and that conjunct is load-bearing:
`text` in `_fstring` is bound into the very same `irconst` (`Constant.value`) slot and is
never `None`, so it must keep its plain `string` lowering byte-identically. Only a genuinely
optional local moves.

**WHY THIS IS A SOUNDNESS-SHAPED FIX AND NOT A POLISH ONE.** Before the carriers, both
guards lowered to LITERALS:

    format_spec is None      ->  false        (the "model the optional as always-present"
    debug_text is not None   ->  true          emit_ir simplification, and the I-B `""`
                                               sentinel for strings)

so the model ALWAYS took the debug-text branch and NEVER took the bare-`{x=}` conversion
default. Those are WRONG branch conditions — the emitted program computes a different node
from the one Python computes — and they type-check, prove, and look entirely plausible. **A
guard that lowers to a literal is the signature of a modelled-away optional; grep the
emitted body for `&& false` and `if true then` before believing a conversion.**

And the `""`-sentinel string model has a second, quieter failure the carrier removes:
`_slice` can legitimately return the EMPTY string, which the sentinel cannot tell apart from
absent.

## Lesson (bm) — the ELEMENT-TYPE FIXPOINT, and a phase offset the prover refuted

`lambda_parameters` + `parse_parameters` were the [LIST-ALIAS ELEMENT TYPE] boundary
relaunch #11 recorded, converted in the first increment of relaunch #12 by building the
capability that refutation named. Four things are worth carrying.

**1. AN ELEMENT TYPE IS A FIXPOINT OVER THE ASSIGNMENT GRAPH, NOT A PROPERTY OF ONE SITE.**
Every element-type producer in the emitter reads a local's OWN assignments — a typed list
literal, an `.append` of a ctor application or of a call with an IR return annotation, an
`.extend`, a tuple-unpack. Two shapes defeat all of them at once:

    a = self._lambda_arg(); args.append(a)     # appends a bare LOCAL, not a call
    posonly = args; args = []                  # an ALIAS carries no element info

so `args` AND `posonly` both stayed untyped, their `irlist` slots failed the
`_emit_ir_seq_locals` test, and the WHOLE `arguments` construction fell back to
`arguments_0 ()` — all seven children dropped. The fix is ONE fixpoint run to closure:
SEED `x.append(<local that is itself an emit_ir local>)` (the LOCAL spelling of the rule
the append site already applies to a DIRECT call) and EDGE `x = <other seq local>` (Python
binds the SAME list object, so an alias has its source's element type). Fail-closed both
ways: an unclassified source propagates nothing, and a local another producer already typed
is never overwritten.

**And the refutation had only HALF of it.** Relaunch #11 named the alias edge and said the
five other pieces were measured working. Rebuilding them showed `_emit_ir_seq_locals` was
EMPTY at the construction site — the seed was missing too. **Re-measure a refutation's
"already works" list before trusting it**; the named capability was right, its scope was
not.

**2. AN OPTIONAL LOCAL CAN BE OPTIONAL WITHOUT EVER REACHING AN OPTIONAL SLOT.** Lesson
(bk) §1 made the SLOT the gate for the optional-node carrier. `default` in
`lambda_parameters` never reaches one — it is APPENDED to a child list, not bound to a
field — yet it is exactly as optional as `Slice.lower`, and under the sentinel model
`if default is not None:` lowered to the literal `true`, so the model appended a default
for EVERY parameter. The second admission route is `None`-assigned AND PRESENCE-TESTED AND
already an emit_ir local, and all three conjuncts earn their place: `None`-assigned or it
is not optional; presence-tested or the two models are INDISTINGUISHABLE and moving it is
pure churn; emit_ir-classified or the value it carries when present is not a node.
**Presence-testing is the observability criterion** — it is what makes the difference
between the models something a proof can see.

**3. A CARRIER APPENDED TO A CARRIER SEQ COPIES THE CARRIER.** The `.append` twin of the
chained-assignment alias rule. Without it the plain Var read projects through `iropt_val`
and the surrounding `IrOSome` turns an ABSENT default into a PRESENT sentinel node. The
OTHER direction was already right and must stay right: `defaults.append(default)` PROJECTS
through `iropt_val`, under the guard that has just proved the value present. Same local,
two appends, two different correct lowerings — decided by the DESTINATION's element type.

**4. THE PROVER REFUTED THE PHASE OFFSET, AND THE REASON GENERALIZES: `advance` IS ONLY
CONDITIONALLY STRICT.** Its contract is `\old(self.i) < \length(self.toks) - 1 ==> self.i
== \old(self.i) + 1` — the EOF sentinel — so a leading `t = self.advance()` pays for a
variant rise ONLY in a body that has evidence the current token is not the last one.
`lambdef` has none (its CALLER did the `at_kw("lambda")` test), so placing the new group
member ABOVE `lambdef` raised the variant and left exactly two `_parser__lambdef'vc`
sub-goals Unknown: the postcondition and the variant decrease. **When a new member's
incoming edge is a bare `advance` with no token test in the same body, the member must sit
strictly BELOW its caller.** Its outgoing edges can still rise freely if a PROVED strict
advance (here `_lambda_arg`'s `self.i > \old(self.i)`, composed with the loop invariant
`self.i >= i0`) drops the cursor term by a full multiplier first. The 1-second oracle
prices the variant SHAPE but NOT the decrease — that one costs a proof, so derive the
offsets from each edge's *provable* progress, never from the progress the source obviously
makes.

## Lesson (bn) — census before you build a carrier; renaming a slot type is cross-cutting; and a no-advance CYCLE is a different animal from a bad offset

`_pattern_number` broke the recorded [MODEL] boundary on the `Constant` NUMBER arm, and the
two methods that did not convert refuted for reasons that had nothing to do with the reason
on record. Four things to carry.

**1. THE CENSUS FOUND A CERTIFIED MODEL WHERE THE PLAN SAID "BUILD ONE".** The refutation
on file said the number arm needed "an `ICNum`-shaped arm" on the bespoke `irconst` carrier
lesson (bj) had introduced. Asking the lesson-(p) question first — *does a value model for a
Python literal already exist?* — turned up `pyconst_val`, seven arms wide
(`PVNone|PVBool|PVInt|PVStr|PVBytes|PVComplex|PVEllipsis`), co-landed with an AXIOM-FREE
Rocq+Lean certificate pinning the py-scalar abstraction map as total and injective-per-kind.
It had only ever been used on the READER side, and nothing made it reader-only. So the right
move was not to extend the bespoke carrier but to **RETIRE** it: one bespoke type deleted,
one certified type reused, five arms free. **A carrier you invented last session is not
evidence that no model exists — it is evidence that nobody looked.**

**2. A RETURN INTERFACE IS THE CHEAPEST MODELLING LEVER THERE IS, AND IT COSTS NO MARKER.**
`_parse_number` stays `\trusted`; all that changed is `-> "PyConstVal"`, taking its emitted
`val` from `(s: int) : unit` — argument INT-ERASED, result discarded — to
`(s: string) : pyconst_val`. That alone is the difference between a facade and a faithful
construction at every call site. And an UNINTERPRETED function is exactly the right
abstraction for a result that can be an int, a float or a complex: equal arguments give
equal results and **nothing else is claimed in either direction**. It never asserts two
literals are equal, and never asserts they differ. Reach for an uninterpreted function
before inventing an ADT arm you cannot populate.

**3. RENAMING A SLOT TYPE IS CROSS-CUTTING — GREP THE OLD NAME EVERYWHERE.** Retiring
`irconst` for `pyconst_val` left ONE stale string comparison behind, in the optional-STRING
carrier gate. It silently dropped `debug_text` from `_iropt_str_local_vars`, and
`_fstring_replacement` — a method converted last session precisely to remove this defect —
got `if true then` back. The emitted program took the wrong branch again, and it type-checked
and would have proved. Two rules follow: grep the retired name across the whole emitter
before believing a rename, and **re-run the lesson-(bl) literal-guard grep (`if true then`,
`&& false`) after ANY change to a slot type**, not only after a conversion. Same increment,
lesson (am) also bit on the ORDINARY axis: the DECLARATION producer
(`functions._compute_return_type`) and the CALL-SITE producer (`_module_method_return_types`)
are two, and patching one emitted a correctly-typed `val` whose call site still read `unit`.

**4. A NO-ADVANCE CYCLE IS NOT A BAD PHASE OFFSET — IT IS A DIFFERENT KIND OF WALL.**
Lesson (bh)/(bk) §3 taught that a new group member forces a re-phasing. `atom` teaches the
next thing: converting a method can remove the abstract `val` that was CUTTING the group,
and the group does not grow by one but by NINE (19 members -> 28). Then the no-advance edges
stopped being a DAG:

    atom -> yield_expr -> testlist -> test -> or_test -> … -> unary_postfix -> atom

No assignment of strictly decreasing offsets exists around a cycle, so no amount of
re-deriving depths helps. **Diagnose the shape before you spend a proof: layer the
no-advance edges and look for a cycle.** The way out is not a better offset but a new PAID
edge, and here the payment is already lying on the floor: each of `yield_expr`,
`atom_paren`, `atom_list`, `atom_brace`, `_dict_rest` opens by consuming a token its CALLER
has just tested, so the strictness evidence exists and is merely in the wrong function. A
token-kind PRECONDITION moves it — dischargeable at every call site from the
`ensures \result != False ==> self.toks[self.i].type == …` clauses `at_op`/`at_kw` already
export, and composing inside the callee with the EOF-sentinel invariant exactly as
`_name_str` does. **A precondition is a proof obligation at the call site, not an
assumption**, so this class of fix adds no `\trusted` surface and no axiom. Corollary worth
its own line: `advance` in this parser is only CONDITIONALLY strict, so ANY method whose
first act is `advance()` has no provable progress of its own — the whole family shares one
missing precondition.

## Lesson (bo) — a precondition is free strictness; and a gate whose regex only reads `let` was blind to 14% of the surface

**1. THE NAMED CAPABILITY WORKED, VERBATIM, AND IT COST NOTHING.** Lesson (bn) §4 ended by
naming a token-kind precondition as the way out of `atom`'s no-advance cycle. It was built
exactly as written and the prover took it on the first serious attempt: `#@ requires
self.toks[self.i].type == _tokenize.OP` on `atom_paren`/`atom_list`/`atom_brace`/`_dict_rest`
and `== _tokenize.NAME` on `yield_expr`, discharged at every call site from `at_op`/`at_kw`'s
existing `ensures \result != False ==> …`. This is the campaign's cheapest structural lever
and it deserves a name: **when a callee's first act is an unconditionally-written but only
CONDITIONALLY-strict primitive, the missing evidence is usually already proved one frame up.
Move the evidence with a precondition instead of strengthening the primitive.** It is a proof
obligation at the call site, not an assumption, so the `\trusted` surface does not move and
the ledger does not move. Three boundaries in this campaign have now been broken by exactly
the capability their own refutation named — the naming discipline is the product.

**2. RE-DEPTHING IS THE REAL WORK, AND THE OLD NUMBERING CAN BE IMPOSSIBLE RATHER THAN BAD.**
Converting `atom` took the expression group from 21 members to 28 and every member has to
share one well-founded order. The recorded first-cut depths were not merely unlucky:
`unary_postfix` at 1 forced `atom` <= 0 and `atom`'s four no-advance callees strictly BELOW
0, i.e. negative — the scheme had no solution at all. The fix is a uniform shift, not a
tweak: keep the multiplier, put every method whose leading `advance` is now PROVABLY strict
at depth 0, and shift everything that was >= 1 up by one. Check the tightest edge explicitly
— here `trailers` (0) reaching `_subscript` (15) after ONE advance, a rise of 15 against a
16-unit drop. **Derive the whole assignment on paper and check the maximum rise against the
multiplier BEFORE spending a 45-minute proof.**

**3. A GATE THAT PARSES ONLY `let` CANNOT SEE A `with`.** `bin/check-emitted-vacuity.py`
announced that a long-KNOWN erasure (`_parser___dict_rest` erasing `t`) was "no longer
erased". Nothing had repaired it. Converting `atom` had moved that function from being a
`let rec` HEAD into a `with` CONTINUATION of the enlarged group, and the probe's head regex
matched only `  let …` — so every continuation member of every mutual-recursion group was
invisible to it: **531 of 3839 emitted functions, 14% of the surface, silently unchecked for
the entire campaign.** Two things follow. First, the specific repair: widening the head and
stop patterns to accept `with` re-detects `_dict_rest`, newly exercises `_cs_clause`, and
finds NO new erasure in the other 529 — a pure tightening that costs nothing, so it landed
in the same increment. Second, the general rule, which is the one to carry: **a gate
suddenly reporting GOOD news you did not work for is a bug report about the gate.** The
campaign already knows three instrument false-greens (`--emit`, the `why3` PATH, `--no-typecheck`);
this is the fourth, and it was found only because the good news was implausible. When a
metric improves for free, go read the metric's code before you write the improvement down.
