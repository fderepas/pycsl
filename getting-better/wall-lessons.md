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
