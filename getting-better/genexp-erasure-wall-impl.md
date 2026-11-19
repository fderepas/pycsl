# genexp-erasure-wall-impl.md — R2 implementation plan (spike-first; refutation exit)

Synthesized from `genexp-erasure-wall.md` (CORRECTED) + `genexp-erasure-wall-response.md`
(Gate R **CONFIRM-WITH-CARVE-OUT**, 10 mandatory conditions). Route **R2**: build a faithful,
bounded `any`/`all` lowering. R3 (the `hval` carrier swap) is explicitly OUT of scope and gated
behind response-condition 7.

**Status of condition 1 (probe wired into the battery, ledger of 12, exits 1 on a NEW erasure):
DONE — commit `50247ac3`, landed before this plan, as the review required.**

## What is being built
`any(pred(x) for x in seq)` / `all(...)` currently lower — in EVERY context, program and spec — to
```
val any_1 (a: array int) : bool          (* unconstrained *)
… (if (any_1 (Array.make 1 0)) then 1 else 0)
```
`seq` is dropped and the predicate is erased. There is exactly ONE handler:
`src/pycsl/module6_whyml/expressions.py:5392`, `if func_name in ("any","all")`.

Target shape (the reviewer's `anyfold.mlw`, proven Valid on z3 AND Alt-Ergo, axiom-free):
```whyml
let function any_p (a: array int) : bool
  ensures { result <-> exists k. 0 <= k < a.length /\ <pred>(a[k]) }   (* IFF, condition 3 *)
= let r = ref false in
  for i = 0 to Array.length a - 1 do
    invariant { !r <-> exists k. 0 <= k < i /\ <pred>(a[k]) }
    if <pred>(a[i]) then r := true
  done; !r
```

## Gate S — the make-or-break SPIKE, FIRST, before any emitter edit
The reviewer already proved the SHAPE (`anyfold.mlw`). What is NOT proven, and what can still sink
R2, is that **PyCSL's emitter can generate it with the predicate inlined at the bound variable**.
That is this plan's falsifier, and it is a different question from the oracle's.

1. Re-run the reviewer's `anyfold.mlw` under `why3 prove -P z3` and `-P alt-ergo` → reproduce all
   five goals Valid + `grep -c '^ *axiom'` == 0. (Cheap; confirms the target is still valid.)
2. **THE FALSIFIER — emit ONE hand-written fixture through PyCSL, unmodified emitter, and read the
   `.mlw`:** does the emitter have ANY route from a genexp AST node to a body-carrying construct?
   Specifically, take `any(x > 10 for x in xs)` and determine whether the genexp's element
   expression (`x > 10`) and its bound variable (`x`) survive into Module 5's IR at all, or whether
   the IR has already discarded them by the time `expressions.py:5392` sees the call. Inspect the
   IR (`--dump-ir` or equivalent) — do NOT infer it from the emitted WhyML.
   - **PASS** (the predicate + bound var are present in the IR) → build.
   - **REFUTE** (Module 5 discards the genexp body before Module 6 — i.e. the erasure happens at
     IR construction, not at lowering) → the fix is a Module-5 feature, NOT a Module-6 one, and the
     costed scope in this plan is WRONG. **Record CERTIFIED-BOUNDARY-AT-M5, re-plan, do NOT grind.**
3. Second falsifier, only if (2) passes — **the predicate is an arbitrary expression over the bound
   variable, and the emitter must inline it under a binder.** Spike the HARDEST real shape in the
   mirror, not the easy one: `any(self._pattern_has_constructor(a) for a in pat.get("alternatives",
   []))` — a genexp whose predicate is a RECURSIVE SELF-CALL. If a recursive call cannot appear
   inside the generated fold (termination/variant, or the self-receiver), the IRScanner family is
   not reachable by R2 even though trivial predicates are. Record which sub-class R2 actually
   clears; do not claim the family.

## Build (only if Gate S passes)
(a) `expressions.py:5392` — replace the `any_1`/`all_1` abstract-op emission with a generated
    bounded fold, gated so it fires only for the genexp/comprehension argument form; a bare
    `any(arr)` (no genexp) keeps its current path unless the same fold applies.
(b) Emit the fold as a pure **`let function`** (condition 4) so the result is usable in `assert` /
    `ensures`; local `ref`s keep the interface effect-free (`purity1.mlw` Valid).
(c) The postcondition MUST be an **iff** (condition 3), never a one-directional `->`.
(d) **Contract grammar (condition 5):** a genexp inside `#@ assert` currently does not PARSE
    (`expected ')' (got NAME 'for')`). Both planes must be fixed in one change. If the grammar work
    turns out to be its own subsystem, SPLIT the increment and say so — do not silently ship the
    program plane only and claim the wall.
(e) Reference fixtures, `git add -f`, per the campaign convention: a program-position
    `any(genexp)` AND a `#@ assert all(genexp)`, each with a POSITIVE driver and an EVIL TWIN that
    reads the opposite answer (condition 6). Non-vacuity is the evil twin, NOT a mutation test —
    lesson (l) is precisely that a mutation test cannot see this family.

## Gate battery (driver-verified FRESH, per increment)
Fidelity (`self-annotate-mirror-check.sh` 52/52; `check-self-annotate-sync.sh` drift MUST NOT rise
above its current 5) ∧ whole-file Why3 proof of every touched mirror file ∧ **mirror-wide L3-tc
sweep, all 52** (run #4 lesson (a) — a past run shipped two type-broken mirror files because every
other gate passed) ∧ corpus byte-diff 0 **with the emitted population asserted at 782** (lesson (k)
— a zero diff over a zero population is a false green; the reviewer hit a 543-file short sweep) ∧
ledger == 3 (`Print Assumptions` / `#print axioms`) ∧ count MUST NOT RISE from 981 ∧
`bin/check-emitted-vacuity.py` exit 0, with any cleared IRScanner entry REMOVED from
`KNOWN_ERASURES` in the same commit ∧ **z3-inclusive proving** (condition 9: Alt-Ergo alone cannot
prove `"Number" <> "String"`).

## Honest costed scope
R2 removes an unconstrained oracle from at least 11 verified functions and repairs `#@ assert
all(...)`. It does **NOT** by itself de-vacuify the 8 fully-erased IRScanner predicates — their
`obj: Any` is independently int-erased, and that is R3. **Do not report R2 as "the 9 fixed".** The
honest success criterion for R2 is: the `any_1`/`all_1` oracle no longer appears in any emitted
mirror `.mlw`, the two fixtures prove with their evil twins, and the vacuity ledger shrinks by
whatever it actually shrinks by — possibly zero, if `obj` erasure keeps the IRScanner bodies
input-blind.

## Refutation exit
Gate S step 2 REFUTE (erasure happens in Module 5) → CERTIFIED-BOUNDARY-AT-M5 + re-plan.
Gate S step 3 REFUTE (no recursive predicate under the binder) → build R2 for the non-recursive
sub-class only, and record explicitly that the IRScanner family stays vacuous and gated.
Either way: record, commit the finding, do NOT grind.

---

## §GATE-S — SPIKE OUTCOME: **REFUTE of this plan's scope (re-plan, cheap), not of R2 itself**

Count unchanged (981), ledger 3, no emitter edit made.

**Step 2 (the falsifier) REFUTES the Module-6-only scope, and the emitter says so in its own
comment.** `src/pycsl/module6_whyml/expressions.py:5392` reads:

> *"Unsupported iterable shapes (generator expressions etc.) get **dropped to `0` at the IR
> level**; coerce that to an array placeholder so the abstract val type-checks."*

Confirmed structurally: `grep -c GeneratorExp src/pycsl/frontend/Module5_IREmitter.py` → **0**.
`ast.GeneratorExp` is absent from `_PY_EXPR_HANDLERS`, so `_py_expr_to_ir` returns the fallback
`{"type": "UnknownPyExpr"}` and `_array_coerce_arg` renders it `Array.make 1 0`. **The erasure
happens at IR CONSTRUCTION (Module 5), before Module 6 ever sees a predicate.** Editing the
Module-6 handler alone could not have worked, and the plan's costed scope was wrong.

**The re-plan is CHEAP, not session-scale** — which is why this is REFUTE-and-re-plan rather than
CERTIFIED-BOUNDARY. `ast.ListComp`/`SetComp`/`DictComp` ARE handled (`Module5_IREmitter.py:1052-4`,
`_py_expr_listcomp` at 1210) and preserve `elt` + `generators`. A `GeneratorExp` is structurally
identical to a `ListComp`, so Module 5 needs one dispatch entry plus a handler modelled on the
existing one.

**Step 2 also found a SECOND erasure layer the report and the review both missed.** The bracketed
form `any([x > 10 for x in xs])` DOES reach Module 6 carrying a real `ListComp` IR — and is erased
there anyway, by a different oracle:

```
let function g_form (xs: array int) : int = (if (any_1 (Array.make 1 0)) then 1 else 0)   (* genexp   *)
let function l_form (xs: array int) : int = (if (any_1 (list_comp 0))    then 1 else 0)   (* listcomp *)
  val list_comp (x: int) : int      (* unconstrained, argument int-erased to 0 *)
```

So R2 must clear TWO layers: `UnknownPyExpr` in M5 **and** `list_comp` in M6.

**Step 2 also REFUTES the plan's byte-inertness claim in part.** The review verified 0 corpus sites
for `any_1`/`all_1`, and that stands. But `list_comp` appears in **1 corpus file (`0042.mlw`)**, and
14 corpus programs contain a list comprehension. So:
- gating the fold to the `any`/`all` argument position ONLY → still byte-inert (0 corpus sites);
- touching the GENERAL `ListComp` lowering → **NOT byte-inert**, and needs an M1 sanctioned reset
  with `0042` re-proving. Do not conflate these two; the second is a separate authorization.

### Re-planned increments (each separately spike-gated)
- **R2a** — Module 5 `ast.GeneratorExp` handler mirroring `_py_expr_listcomp` (dispatch entry +
  handler). Makes the predicate and bound variable reach Module 6. Byte-inert (no corpus genexp
  reaches an emitted site today). Small.
- **R2b** — Module 6: generate the bounded iff-specified fold for `any`/`all` **when the argument
  IR is a comprehension**, replacing `any_1`/`all_1` at that position only. Byte-inert by the gate
  above. Must be a pure `let function` (condition 4) with an iff postcondition (condition 3).
- **R2c** — contract-grammar genexp support so `#@ assert all(x >= 0 for x in a)` parses
  (condition 5). Currently `expected ')' (got NAME 'for')`. Independent of R2a/R2b; if it proves
  to be its own subsystem, ship R2a+R2b and say the spec plane is unfixed — do NOT claim the wall.
- **Step 3 (recursive-predicate falsifier) NOT YET RUN.** It only becomes answerable once R2a
  lands and a genexp body actually reaches Module 6. Until then, whether the IRScanner family is
  reachable at all is OPEN, and R2 must not be described as fixing it.

---

## §R2b OUTCOME — **BUILT for the simple-predicate sub-class; Gate S step 3 ANSWERED (IRScanner is out of reach)**

Commit `82e02ad4`. Count 981 -> 981, ledger 3, corpus diff = exactly the 2 new fixtures.

**What works.** `any(P(x) for x in it)` / `all(...)` now emit the reviewer's bounded fold with a
full **iff** postcondition (response condition 3), as a pure `let function` (condition 4), the
predicate lowered through the emitter's existing `subst` binder channel. Fixtures 0936 (positive,
PROVES a real statement about the input) and 0937 (evil twin, MUST NOT prove — and does not).
Both the genexp and the bracketed list-comp form share one spec-hashed definition.

**Gate S step 3 — the recursive-predicate falsifier — is now ANSWERED, and it REFUTES the
IRScanner half of R2.** Instrumenting every bail path and running it over the whole mirror
accounts for all 21 remaining `any_1 (Array.make 1 0)` sites:

| sites | reason | reachable? |
|---|---|---|
| **18** (all of IRScanner) | `predicate-needed-op: iRScanner_uses_string_1` — the predicate is a **recursive self-call** | **NO** — needs `let rec function … with …` mutual recursion + a termination variant; the fold is a standalone `let function` in the abstract-ops block and cannot reference the function being defined |
| 1 (`_handle_fieldassign_stmt`) | `stripped.startswith(p)` over a list of **strings** | plausibly — needs a parameterized element type (the fold hardcodes `a: array int`) |
| 1 (Module5_IREmitter) | `predicate-lost-binder: elt_type=BinOp` | unknown — the binder does not survive lowering |

So **R2 does not de-vacuify the 8 fully-erased IRScanner predicates**, exactly as this plan's
"honest costed scope" warned it might not. Their `obj: Any` int-erasure (R3) was never the only
blocker — the recursion is a second, independent one. The vacuity ledger stays at **12**.

### Remaining, in dependency order (each still spike-gated)
- **R2d — mutual-recursion folds.** The only route to the IRScanner 18. Emit the fold INSIDE the
  recursive group (`let rec function f … with _any_fold_f …`) with a shared `variant`. This is a
  materially larger emitter change than R2a/R2b and must be spiked before it is authorized.
- **R2e — parameterized element type** (`array string`, `array <record>`): unlocks the
  `startswith` site and is a prerequisite for any string-predicate fold.
- **R2c — contract-grammar genexp** (response condition 5): `#@ assert all(x >= 0 for x in a)`
  still does not PARSE. Untouched by R2a/R2b; the spec plane remains unrepaired.
- **R3** — unchanged and still gated behind response condition 7 (assoc-list `hval` proving its
  evil twin with the map arm present).

## §R2e SPIKE OUTCOME — REFUTE-as-bounded: R2e is SESSION-SCALE, needs authorization (like R2d/R3)

Gate-S spike (`scratchpad/anyspike/r2e.py`, no emitter edit). The 2 non-recursive string-predicate
sites (`_handle_fieldassign_stmt`, `_union_arm_tag`) need FOUR coordinated capabilities, not the
"parameterized element type" this plan scoped:
1. **Element-type parameterization.** The fold hardcodes `a: array int`; `any(x == "" for x in xs)`
   over a `List[str]` emits `_any_fold (a: array int)` applied to `array string` → L3-tc TYPE ERROR.
2. **Faithful string-predicate lowering INSIDE the fold.** Even typed, `x == ""` lowers to
   `a[_fk] = 313406155` (the int-hash of `""`) — a vacuous comparison; it must be `str_eq_op a[_fk] ""`.
3. **Closure-capture threading.** `any(s.startswith(p) for p in prefixes)` captures the FREE var `s`;
   a standalone `let function _any_fold (a: ...)` cannot see it, so it must be threaded as an extra
   fold parameter. Today it fully erases to `any_1 (Array.make 1 0)`.
4. **A faithful `startswith` model.**
This is the same tier as R2d (mutual-recursion) and R3 (hval carrier swap): a multi-capability
emitter build, NOT a bounded increment. **Disposition: CERTIFIED-BOUNDARY-as-bounded; authorize
first.** No silent vacuity exists in the booked corpus from R2b's int-only fold — a string element
TYPE-FAILS at L3-tc (caught), it does not int-hash silently.

**Bounded Phase-2 frontier is now EXHAUSTED** (R2a/R2b landed; self-state vacuity gate landed; R2c
grammar, R2d, R2e, R3 all session-scale / authorize-first). Per driver §A.3 the run stops early.

---

## §R2d OUTCOME — **BUILT via the pyval catamorphism (NOT hval); 6/8 IRScanner de-vacuified, erasures 12->6**

Commits `413ba556` (+4) and `f778ffb8` (+2). Ledger of KNOWN_ERASURES (bin/check-emitted-vacuity.py)
**12 -> 6**. corpus byte-diff 0 @ population 784==784 both increments; ledger 3 (no cert touched).

**Gate S PASSED — the `let rec ... with ... variant` rec-group weaving is achievable, and the KEY
FINDING is it needs NEITHER hval NOR a new certificate.** The r2d-r3-impl framed the target as the R3
assoc-list `hval` carrier + a new mutual-recursion fold. But the IRScanner `uses_X(obj: Any)` family
is the `obj: Any` dict-first `.get("type")` existence fold, which the ALREADY-CERTIFIED pyval/pydict/
list-pyval L1 catamorphism (the same theory `recognize_bool_existence` / `recognize_void_generic_
descend` fold over, `pv_size`/`size_dict`/`size_list`, ledger 3) models directly — `obj.values()` is
the `size_dict` fold over the `DCons _ v rest` assoc list. So the R2d rec-group fold is a new
recognizer/templater (`recognize_type_existence` + `emit_type_existence_group`, generic_fold.py),
scalar-rooted and keyed on the interned `K_type`, emitting the proven `let rec <n> (obj: pyval) ...
with <n>__d ... with <n>__l ...` group. The fold co-lives with the recursive predicate in ONE mutual
group (self-recursion binds, no `unbound symbol`) and terminates on the structural pyval measure.
`ir_scanner.mlw` whole-file proof SUCCESS both increments.

**Converted (removed from KNOWN_ERASURES):**
- SINGLE "type"-tag: `uses_string`, `uses_subscript`, `uses_sum`, `uses_set_card`.
- COMPOUND `type=="Call" and <k2> in (tags)` (k2 = interned K_func/K_op): `uses_ord_chr`, `uses_minmax`.
  `uses_minmax`'s extra `len(args)==2` conjunct is DROPPED — a sound over-approximation under the fixed
  `ensures True` (insight C, the doctrine `recognize_bool_existence` uses for its membership conjunct):
  the true-set is a superset, nothing false is derived, and the mutation-sensitive type/func tags (the
  non-facade signal) are preserved verbatim.

**Residual (2, measured, distinct shapes — NOT the same wall):**
- `_check` (behind the `uses_divmod` wrapper) — a NESTED `def` lambda-lifted at EMISSION time, so it
  is NOT in the Module5 `functions` list the recognizer scans (the "nested def dropped" blocker,
  run-#5 blocker A). Converting it needs recognizing the `uses_divmod` wrapper whole (nested-def +
  delegating call, with the call-site `stmts: Any -> pyval` typing) — a distinct recognizer.
- `uses_array_lit` — a DISJUNCTIVE two-tag-arm discriminant whose second arm is `type=="BinOp" and
  op=="*" and obj["left"].get("type")=="ArrayLit"` — a NESTED-FIELD projection (`obj["left"]` -> a
  pyval child -> its type). Capturing only the direct `type=="ArrayLit"` arm would UNDER-approximate
  (miss `[0]*n`) = an unfaithful partial conversion (refused per wall-lesson (j)). Needs a nested
  child-projection discriminant.

## §R2d-followup — the 3 residual/partial IRScanner erasures RE-SPIKED — all 3 BOUNDED, built

Re-measured against the REAL Module5 IR (spike `scratchpad/irx/spike_ir.py`). The R2d-outcome
prose above was WRONG about `_check`'s blocker, and both other residuals turned out bounded.

### (i3) `_check` — DE-VACUIFIED (`irscanner___check` removed from KNOWN_ERASURES)
The "nested def NOT in the Module5 functions list" claim is FALSE. The lambda-lifted `_check` IS a
first-class IR function `irscanner___check` (`formal_params ['obj']`, no annotations, return bool),
and its body is EXACTLY the compound shape the R2d recognizer already handles (`type=="BinOp" and
op in ("div","/","%")`). Recognition failed for ONE reason: `self_base` was derived with
`rsplit("__",1)[-1]`, which on the mangled `irscanner___check` (`irscanner` + `__` + `_check`) EATS
the method's leading underscore -> `"check"`, so the genexp self-call basename `"_check"` no longer
matched and the whole match bailed. Fix = `split("__",1)[-1]` (the class-method boundary is the
FIRST `__`; a class-lowered name never contains `__`, so it is identical to `rsplit` for every
single-`__` name — byte-inert for the 6 already converted). One-line emitter change; `_check` now
emits the real compound pyval/pydict catamorphism over `obj`.
GATES (all fresh): ir_scanner.mlw whole-file proof SUCCESS; vacuity `--emit` exit 0, `irscanner___check`
removed, no NEW erasure, 0 input-blind; corpus byte-diff 0 @ 784==784 (detached-HEAD worktree);
mirror-wide L3-tc 52/52; mirror-check 52/52; sync drift 5 (== HEAD); ledger 3 (no cert touched);
count 943 unchanged.
NOTE (honest): `irscanner___check` is the de-vacuified target (the KNOWN_ERASURES entry). Its wrapper
`uses_divmod` (`return _check(stmts)`, NOT in KNOWN_ERASURES — references `stmts`) still lowers the
`_check(stmts)` call to the abstract `val _check_1` — connecting the wrapper to the real body is a
separate call-site-typing change, not required for this erasure.

### (i1) `is_recursive(name, obj)` — FULLY DE-VACUIFIED (`irscanner__is_recursive` removed)
The only PARTIAL IRScanner erasure (kept `name` via `str_hash_op name`, int-erased `obj`). Two
independent deltas vs the 6, both BOUNDED extensions of the recognizer/emitter:
(a) a leading scalar-`str` "carried" param `name` threaded verbatim through the mutually-recursive
    fold group (`is_recursive name obj` / `__d name d` / `__l name xs`); and
(b) a discriminant that compares the interned "func" key against the RUNTIME param, not a literal:
    `type=="Call" and func==name` -> new `_match_key_eq_param` matcher + a `"param"` pred kind
    emitting `{n}__func_is obj name` (reuses the existing `func_is (v) (tag: string)` reader,
    passing `name` where a literal tag would go). The genexp self-call `IRScanner.is_recursive(name, v)`
    now matches via a generalized `_match_any_selfrecurse_genexp` (carried leading args + bound var last).
Emitted body references BOTH `name` and `obj` via a real pyval fold + `pystr_eq`.
GATES (all fresh): ir_scanner.mlw whole-file proof SUCCESS; vacuity `--emit` exit 0, `irscanner__is_recursive`
removed, no NEW erasure, 0 input-blind; corpus byte-diff 0 @ 784==784; L3-tc 52/52; mirror-check 52/52;
sync drift 5 (== HEAD); ledger 3; count 943 unchanged. The `carried=[]` default keeps all 6 + `_check`
byte-identical (verified by the 0 byte-diff and unchanged recognitions).

### (i2) `uses_array_lit(obj)` — DE-VACUIFIED FAITHFULLY, BOTH arms (`irscanner__uses_array_lit` removed)
A DISJUNCTIVE dict-arm: `type=="ArrayLit"` OR (`type=="BinOp" and op=="*" and
obj["left"].get("type")=="ArrayLit"`). Two BOUNDED extensions, all machinery pre-existing:
(a) the dict-arm body may hold N>=1 `if <disc>: return True` tag-guards (was exactly 1) — the
    recognizer collects a `preds` LIST, the emitter ORs the per-arm strings (single-arm output
    stays byte-identical, so the 8 already-converted are unchanged); and
(b) a NESTED child-field projection `_match_nested_type_proj` (`obj["left"].get("type")==tag`,
    lowered by Module5 to a `Call func="get"` with a `receiver=Subscript(obj,"left")`) -> a
    `"nested"` pred kind whose emitter reads the interned `K_left` cell with a direct-match
    `getp_left (d): option pyval` projector (NOT the theory `get`, which mis-resolves unqualified),
    then applies the CHILD's `type_is`. The `isinstance(obj["left"],dict)` guard is dropped as a
    sound over-approx (the pyval `type_is` on a non-PDict child already returns false).
Capturing ONLY the direct `ArrayLit` arm would have UNDER-approximated (missed `[0]*n`) — refused
per lesson (j); both arms are modelled. Emitted body references `obj` through real folds.
GATES (all fresh): ir_scanner.mlw whole-file proof SUCCESS (first attempt type-errored on the theory
`get`; fixed with the `getp_left` projector, re-proved SUCCESS); vacuity `--emit` exit 0,
`irscanner__uses_array_lit` removed, no NEW erasure, 0 input-blind; corpus byte-diff 0 @ 784==784;
L3-tc 52/52; mirror-check 52/52; sync drift 5 (== HEAD); ledger 3; count 943 unchanged.

### VERDICT — all 3 residual/partial IRScanner erasures were BOUNDED and are DE-VACUIFIED
KNOWN_ERASURES lost all 3 IRScanner entries (`irscanner___check`, `irscanner__is_recursive`,
`irscanner__uses_array_lit`); the remaining 3 gated entries are non-IRScanner (`_collect_class_constants`,
`_handle_mktuple_expr`, `_emit_new_ghost_ref`). The IRScanner type-existence family is FULLY honest.
No boundary was recorded — the R2d-outcome prose that predicted 2 residual boundaries was refuted by
re-measuring against the real Module5 IR. No new axiom/cert/theory (ledger 3); count 943 throughout
(de-vacuification makes a fake conversion honest, it does not lower the count).

---

## §R2c OUTCOME — **BUILT via the existing certified quantifier; spec plane repaired, count-neutral**

Count unchanged (**942**), ledger 3 (no cert/allowlist/formal-semantics touched), corpus byte-diff = exactly
the 2 new fixtures. This is a SPEC-PLANE INTEGRITY repair — it does NOT lower the `\trusted` count, and
count-neutral is the correct outcome (the reviewer's condition 5).

**NOT its own subsystem (the plan's SPLIT contingency did not fire).** STEP-0 census located the contract
grammar as the hand-written recursive-descent `_ContractParser` (`src/pycsl/frontend/Module2_Parser.py`),
which replaced the former Lark engine. The genexp arg to `all`/`any` in a `#@` clause is a BOUNDED grammar
addition wired straight onto the existing quantifier path — NOT a new subsystem:
- `all(P for x in dom)` desugars to exactly the CSLNode `\forall x in dom; P` builds (`_mk_in`,
  quantification.md P3); `any(P for x in dom)` to `\exists x in dom; P`.
- So the IR, the WhyML lowering, and the 3-axiom certificate are **entirely reused** — zero new value
  model, zero new lowering, zero certificate touch. The emitted `.mlw` is BYTE-IDENTICAL to the
  hand-written quantifier form (verified: `diff` empty).

**The one-branch change** (`_ContractParser._parse_atom_name`): on a call whose callee name is `all`/`any`,
parse the first expr; if a `for` follows, consume `for VAR in DOMAIN`, close `)`, and return
`Forall`/`Exists` via `_mk_in`. A non-genexp `all(arr)`/`any(arr)` (no `for`) keeps the CallExpr path
(byte-inert).

**STEP-1 SPIKE PASSED (make-or-break):**
- (a) PARSES — `#@ assert all(x >= 0 for x in a)` no longer `expected ')' (got NAME 'for')`.
- (b) FAITHFUL — lowers to `forall x. (exists _mem_0. 0<=_mem_0<len(a) /\ a[_mem_0]=x) -> x>=0`; grep 0
  `all_1`/`any_1` oracle in the emitted `.mlw`. The oracle is GONE from spec position.
- (c) NON-VACUOUS — the POSITIVE fixture proves (Valid, both provers via the standard battery) and the
  EVIL TWIN (`all(x>=5 …)` under a precondition giving only `a[i]>=0`) does NOT prove (Unknown). Evil
  twin, not a mutation test (lesson l).

**Fixtures** (git add -f): `0938_spec_genexp_all_any.py` — positive `all` AND `any` genexp asserts, both
PROVE; `0939_spec_genexp_evil_twin.py` — `# pycsl-expected: FAIL`, MUST NOT prove (XFAIL). Also repaired
the PRE-EXISTING red `0937` (R2b's evil twin was missing the `# pycsl-expected: FAIL` marker → the runner
scored it FAIL; the fix is comment-only, 0937 emission byte-identical) — opportunistic gate hardening.

**GATES (all fresh, driver-verified):** corpus byte-diff 0 over the 784 existing files (base 784 / mine 786
= +2 new fixtures; 0 existing files differ; detached-HEAD worktree, `.venv` symlinked, population asserted);
mirror-check 52/52; mirror-wide L3-tc 52/52; **all 52 mirror `.mlw` emission BYTE-IDENTICAL to HEAD** ⇒ the
whole-file self-annotation proof suite is provably unaffected (identical WhyML input ⇒ identical proof
result — the sound fast equivalent, since the edited live `_parse_atom_name` is a `\trusted` stub in the
mirror and no mirror `#@` clause uses genexp); sync drift 5 == HEAD; ledger 3; count 942 unchanged.

**The spec plane of the any/all fold is now repaired.** `#@ assert all(genexp)` / `any(genexp)` is a real,
provable obligation instead of an unconstrained `val`. R2d/R2e/R3 remain as previously scoped.
