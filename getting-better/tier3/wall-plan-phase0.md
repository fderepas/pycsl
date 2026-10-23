# wall-plan Phase 0 — benchmark freeze + fmap / WL-05 / census spikes + negative controls

**Executes Phase 0 of `generic-dict-str-and-plan.md` §6.** A MEASUREMENT/DECISION
phase: go/no-go verdicts with reproducible evidence, NO permanent `src/pycsl` or
mirror edits. Branch `ghost-assign-bc6`, baseline HEAD `a657569c`, `\trusted`
count **1240** (asserted unchanged below). Provers: system **Alt-Ergo 2.6.2** +
**Z3 4.13.3** under **Why3 1.8.2**, 10 s timelimit. Pipeline runs under project
`.venv` (libcst present — asserted the LIVE emitter body replaced the stub in every
benchmark probe, not a libcst-absent artifact).

## OVERALL PHASE-0 VERDICT — **HALT Track M; proceed Track-R-only.**

| gate | result | consequence |
|---|---|---|
| **Spike (a) fmap** — make-or-break for Track M | **NO-GO** (3 independent grounds) | **Track M halts**; the report's stop verdict re-applies to the V1 `Dict[str,Any]` cluster |
| **Spike (b) WL-05 `ref`+`writes`** | **GO** (4/4 VCs Valid both provers) | M2's target is a real WhyML capability; the WL-05 rejection is an emitter gap, convertible **independently** of Track M's value model |
| **Spike (c) census′** — incidental fraction | **0.90** (18/20) ≥ threshold | Track R yield is large; Track-R-only is the supported path |

Threshold logic (plan §6): Track M **GO requires GO(a) ∧ GO(b) ∧ census ≥ threshold.**
GO(a) **fails decisively**, so Track M halts regardless of the other two. Track R
is gated only on the census′ incidental fraction being *not* "≪ expected"; expected
was "a large fraction," measured **0.90 → Track R ROI holds.** GO(b) is moot for
Track M (halted) but is a positive spin-off: the by-ref-mutation boundary (WL-05,
the 2 `essential` walkers) can be addressed by the `ref`+`writes` emitter routing
rule alone, without the `pyval` value model.

**The single most important finding:** fmap does **not** clear the SMT pathologies.
It is worse — see Spike (a). The plan's premise ("Why3's finite-map theory maps to
solver-native array/UF reasoning") is **empirically false in this Why3/prover
stack**, and the literal design object ("re-back `PDict` with `fmap`") does not even
type-check.

Ledger assertions (verified below §6): `\trusted` = **1240** unchanged; `src/pycsl`
+ mirror **byte-identical to HEAD**; `proof_axiom_allowlist.py` (both copies)
unchanged; the two committed spike fixtures contain **no `axiom` declaration**
(prose mentions only); no `.mlw` pipeline axiom added.

---

## 1. Frozen benchmark — the 4 F-B1 artifacts (reproduced verbatim)

Method (F-B1 §S1b): `git checkout` clean mirror → blank the ONE `#@ \trusted` line
of the target (plain comment, line-count preserved) →
`python3 bin/sync-mirror-bodies.py module6_whyml/<file>.py` (ports LIVE
params+body+returns; asserted the LIVE signature replaced the stub) →
`PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py <mirror> --import-path src/pycsl --fun
<qual>` → `git checkout` revert. All four reverted; count 1240.

| # | artifact (face) | exact `--fun` command (after drop-`\trusted` + sync) | verbatim failing error |
|---|---|---|---|
| 1 | `IRScanner.find_named_expr_targets` — WL-05 by-ref `Set` mutation (face 3) | `pycsl.py src/self-annotate/src/module6_whyml/ir_scanner.py --import-path src/pycsl --fun irscanner__find_named_expr_targets` | `[module6-whyml]: in-place mutation of dict/set parameter 'targets' (`targets.add(...)`) is out of scope: … a faithful model requires a caller-visible mutation frame (`writes {targets}`) that PyCSL's by-value map parameter does not provide …` — **REJECTED at the emitter, never reaches proof** |
| 2 | `IRScanner.find_return_type` — opaque-dict `array int` vs `int` collapse (face 1) | `pycsl.py …/ir_scanner.py --import-path src/pycsl --fun irscanner__find_return_type` | `File "…mlw", line 112, characters 28-33: This expression has type array.Array.array int @rho, but is expected to have type int` → `[-] Verification FAILED or INCOMPLETE.` |
| 3 | `_emit_metatype_tags` — `(str,int)` heterogeneous-tuple-unpack mistyping (face 1) | `pycsl.py …/expressions.py --import-path src/pycsl --fun expressionemissionmixin___emit_metatype_tags` | `File "…mlw", line 361, characters 17-28: unbound function or predicate symbol 'iter_length'` → `[-] Verification FAILED or INCOMPLETE.` (the `iter_length` symptom of the opaque tuple-literal lowering; the `int_to_string nm` mistype is the root, per emission-defect-spike-findings.md) |
| 4 | `_call_returns_string_collection` — multi-`_` tuple-unpack duplicate WhyML variable | `pycsl.py …/statements.py --import-path src/pycsl --fun statementemissionmixin___call_returns_string_collection` | `File "…mlw", line 316, characters 15-79: duplicate variable _tu_py_underscore` → `[-] Verification FAILED or INCOMPLETE.` |

All four reproduce the F-B1 / emission-defect findings **byte-for-byte on the error
text**. This is the frozen benchmark: later success is measured against these exact
`--fun` commands and errors.

---

## 2. Spike (a) — fmap-backed `PDict` — **NO-GO** (the make-or-break)

Fixture: `test-suite/corpus/conformance/spikes/fb1_fmap_spike.mlw` (committed,
`git add -f`). Three independent grounds, each reproducible.

### Ground 1 — the literal design is TYPE-REJECTED (does not compile)

`type pyval = … | PDict (fmap string pyval)` is rejected by Why3:

> `Constructor PDict contains a non strictly positive occurrence of type pyval`

Reason: `fmap 'k 'v = abstract { contents: 'k -> 'v; domain: … }`, so
`fmap string pyval` places `pyval` in the **codomain of the arrow** `string ->
pyval` — a non-strictly-positive position. The hybrid `PDict (fmap string pyval)
(list (string, pyval))` is rejected for the **same** reason. Spike (a)'s literal
object — "PDict re-backed by fmap instead of `list (string, pyval)`" — is
**impossible to type-check.** (Same class as the nested-list project's
`array (array τ)` rejection.)

### Ground 2 — even non-recursively, fmap does NOT clear pathology (i)

Since recursion through fmap is rejected, we test the **best case fmap can express**
(a flat dict of NON-recursive leaves) — and the string-keyed read/miss STILL does
not discharge on both provers. Command:
`why3 prove -P '<prover>' -t 10 test-suite/corpus/conformance/spikes/fb1_fmap_spike.mlw`

| goal (module `FmapReadPathology`) | Alt-Ergo 2.6.2 | Z3 4.13.3 | note |
|---|---|---|---|
| `r_hit_a_bare`  read-hit, bare | **Timeout** (10.0s) | **Timeout** (10.0s) | assoc-list `g2_read_hit` was *Valid* — fmap is WORSE |
| `r_hit_b_bare`  2nd-key hit, bare | Valid (0.06s) | **Timeout** (10.0s) | |
| `r_miss_z_bare`  **bare miss (pathology (i) witness)** | **Timeout** (10.0s) | **Timeout** (10.0s) | the exact analog of `g2_read_miss_bare` |
| `r_notmem_bare`  bare non-membership | **Timeout** (10.0s) | **Timeout** (10.0s) | |
| `r_hit_a_guard`  hit, disequalities fed | Valid (0.13s) | **Timeout** (10.0s) | |
| `r_miss_z_guard`  miss, disequalities fed | Valid (0.10s) | **Timeout** (10.0s) | even the "distinctness lemma pack" does not save Z3 |
| `r_notmem_guard`  non-membership, guarded | Valid (0.12s) | **Timeout** (10.0s) | |
| `r_false_twin`  poisoned read (must stay UNPROVEN) | Timeout ✓ | Timeout ✓ | correct — model rejects the false read |

**Pathology (i) verdict: NOT cleared.** The bare miss times out on both provers;
even guarded, Z3 times out on every read. fmap does not provide free select/store;
the string-disequality tax is not removed (guarded still required) and Z3 cannot
discharge it at all.

### Ground 2b — the Z3 choke is the abstract `Fmap`/`Fset` theory, NOT strings

Module `FmapIntKeyControl` — the same reads with **int keys** (zero string theory):

| goal | Alt-Ergo | Z3 |
|---|---|---|
| `i_hit_1` int-keyed hit | Valid (0.07s) | **Timeout** (10.0s) |
| `i_miss_9` int-keyed miss | Valid (0.04s) | **Timeout** (10.0s) |
| `i_notmem` int-keyed non-membership | Valid (0.06s) | **Timeout** (10.0s) |

Z3 times out on the trivial int-keyed two-element dict. So the killer is
`fmap.Fmap` itself — an **abstract type axiomatized over `map.Map` + `set.Fset`** —
whose domain reasoning (`add_domain` / `mem` / `S.add`) Z3 handles poorly regardless
of key type. "fmap = solver-native select/store" is **false in this stack.**

### Ground 3 — pathology (ii) pair-nested termination: fmap cannot express it

fmap is abstract: **no induction principle, no structural fold.** A `size : pyval ->
int` recursing into a dict's values cannot be defined over an fmap without adding
axioms; `Fmap.size` gives only the domain **cardinality** (key count), useless as a
depth measure. And the fmap-backed value type is rejected anyway (Ground 1). On the
**only** walkable faithful form (the list backing), module `PairNestedTermination`
tests the plan's own size-measure variant (§3.5):

| goal (program-form walk, `variant { size … }`) | Alt-Ergo | Z3 |
|---|---|---|
| `walk'vc` | **Timeout** (10.0s) | **Timeout** (10.0s) |
| `walk_list'vc` | **Timeout** (10.0s) | **Timeout** (10.0s) |
| `walk_pairs'vc` | **Timeout** (10.0s) | **Timeout** (10.0s) |

**Pathology (ii) verdict: NOT discharged.** The doubly-nested `Cons (_, v) t`
decrease VC times out on both provers even with the size-measure variant.
Termination is sound **only** via Why3's syntactic structural checker (pure logic
`function`, no VC) — which the emitter's real program-form walk cannot use. fmap is
irrelevant here (type-rejected).

### Spike (a) overall — **NO-GO**

Both required pathologies **fail** on both provers, and the literal design does not
type-check. `GO(a)` required both to discharge on both provers with no axiom; none
do. **Track M halts.** Per the plan, this "would indicate research-grade, and the
report's stop verdict re-applies" — it does. The F-B1 NO-GO is re-confirmed, and
the specific "finite-map backing" rescue hypothesis is **refuted with measurement.**

**Honesty note on "no new axiom":** the committed fixture contains no `axiom`
*declaration*. But `fmap.Fmap` is itself an abstract, axiomatized stdlib theory
(extensionality, `add_contents_*`, `add_domain`, `find_def`, …) layered on
`set.Fset` — a **larger trusted base** than the pure-inductive `list` foundation of
F-B1's `fb1_pyval_spike.mlw`, which needs no theory axioms at all. So fmap-backing
would *also* have widened the trusted base even if it had worked. It did not.

---

## 3. Spike (b) — WL-05 `ref`+`writes` minimal example — **GO**

Fixture: `test-suite/corpus/conformance/spikes/fb1_wl05_spike.mlw` (committed).
A `ref` set-like parameter, mutated in place (`add`), with `writes {p}` + the FIXED
self-annotation contract shape `requires True / ensures True / writes {p}`
(type-safety + frame only). Command:
`why3 prove -P '<prover>' -t 10 test-suite/corpus/conformance/spikes/fb1_wl05_spike.mlw`

| goal | Alt-Ergo 2.6.2 | Z3 4.13.3 |
|---|---|---|
| `targets_add'vc` (set param, `writes {p}`) | Valid (0.03s) | Valid (0.00s, 6 steps) |
| `dict_targets_add'vc` (dict param, `writes {d}`) | Valid (0.02s) | Valid (0.01s, 6 steps) |
| `two_frames'vc` (non-aliasing: `!q = old !q` after mutating `p`) | Valid (0.03s) | Valid (0.00s, 6 steps) |
| `caller'vc` (mutation escapes to caller) | Valid (0.03s) | Valid (0.00s, 90 steps) |

**GO(b).** Why3 natively accepts `ref`+`writes` for the M2 target shape; the frame
VC discharges on both provers, and region typing enforces non-aliasing structurally
(`two_frames` proves `q` untouched by `p`'s frame). The WL-05 rejection (benchmark
#1) is confirmed an **emitter capability gap, not a WhyML semantics wall** — and
addressable independently of Track M.

---

## 4. Spike (c) — R0 census′ — incidental fraction **0.90** (18/20)

Classification of a 20-stub sample of the V1 `Dict[str,Any]` readers + V2
collection-result builders, on the incidental/essential axis (INCIDENTAL = dispatches
on a known `"type"`/`"stmt"`/`op`/`func` tag + reads a fixed named-key set →
rewritable as tag-dispatch/accessor; ESSENTIAL = uniform over unknown shapes / by-ref
param mutation). Each row read from the LIVE body in `src/pycsl/module6_whyml/`.

| file | function | class | justification (actual body behaviour) |
|---|---|---|---|
| ir_scanner | collect_escaping_exceptions | INCIDENTAL | dispatches `stmt.get("stmt")`∈{Raise,Try}; recurses fixed `("body","orelse")` |
| ir_scanner | collect_user_exceptions | INCIDENTAL | same Raise/Try tag-dispatch, named `exc_type`/`handlers`/`body` |
| ir_scanner | collection_binder_kinds | **ESSENTIAL** | after Forall/Exists check, recurses `for v in obj.values()` — whole-tree uniform scan |
| ir_scanner | find_append_targets | INCIDENTAL | `stmt=="Expr"`, `value.type=="Call"`, `func.endswith(".append")`; fixed-key recursion |
| ir_scanner | uses_ghost_type | INCIDENTAL | `stmt=="GhostAssign"`, named `ghost_type`; fixed-key recursion |
| ir_scanner | find_assigned_vars | INCIDENTAL | `stmt` tag-dispatch; mutated set is a LOCAL, not a by-ref param |
| ir_scanner | find_record_vars | INCIDENTAL | `stmt=="Assign"`+`value.type=="Call"`; fixed-key recursion |
| ir_scanner | find_return_type | INCIDENTAL | `stmt=="Return"` then `value.type`∈{Tuple,String}; fixed-key recursion |
| ir_scanner | has_early_return | INCIDENTAL | `stmt` tag-dispatch (If/For/While/Try), named body/orelse/handlers |
| expressions | _handle_attribute_expr | INCIDENTAL | `obj_ir.get("type")`∈{Result,Subscript,Var}; named object/attr |
| expressions | _handle_call_expr | INCIDENTAL | dispatch on `expr["func"]` name; named args (large but pure name-tag) |
| expressions | _handle_binop | INCIDENTAL | `expr["op"]` + `left.get("type")`; named left/right |
| expressions | _tag_of_value | INCIDENTAL | `x_ir.get("type")=="Var"` then named `name` (the `ord` sum hashes the name, not a dict key) |
| expressions | _match_pattern_cond | INCIDENTAL | `pat.get("pattern")` tag-dispatch (Wildcard/Value/Capture/Or) |
| stmt_control_flow | _classify_iterable | INCIDENTAL | `iter_ir.get("type")`∈{Call,Var}+`func=="range"` |
| stmt_control_flow | _infer_return_value_type | INCIDENTAL | `val_ir.get("type")` tag-dispatch |
| stmt_control_flow | _try_local_decl_kind | INCIDENTAL | `val_ir.get("type")`∈{Call,DictLit,SetLit}+`func` |
| types | _first_assign_kind | INCIDENTAL | `val_ir.get("type")` tag/shape dispatch |
| types | _val_is_bool | INCIDENTAL | `val_ir.get("type")`∈{Compare,BoolOp,UnaryOp,BinOp}+`op` |
| functions | _returns_string_seq | **ESSENTIAL** | recurses `for x in node.values()` — uniform over unknown shapes |

**INCIDENTAL = 18, ESSENTIAL = 2 → incidental fraction 0.90.** Only the two full-tree
`for … in obj.values()` scanners are genuine uniform-over-unknown-shape reflection;
every other stub — including the three large `_handle_*` handlers — dispatches on a
known tag and reads fixed named keys. No stub in the sample mutates a caller-owned
by-ref set/dict (the sets they build are locals).

**Two honesty caveats** (so the 0.90 is not over-read):
1. This is a **rewritability** classification, not a proven conversion. "Incidental"
   means *rewritable as tag-dispatch*, addressable by the already-certified IR-node
   ADT — but a rewrite must still land as live-source edits gated by byte-diff 0 +
   the reference oracle.
2. Incidental **recursive** walkers (the many that recurse over `("body","orelse")`
   stmt-lists) still depend on the stmt-node ADT + a termination measure. Spike (a)
   Ground 3 measured the program-form size-measure variant as **timing out**, and the
   whole-body census independently placed ~10 such stubs in "needs-size-measure"
   (termination the sole unproven VC). So Track R's *ready* yield is the
   non-recursive / pure-`bool` subset plus whatever the ADT + syntactic-checker route
   already converts (the census's 11 convertible-NOW); the recursive remainder shares
   pathology (ii)'s open friction. Track R ROI holds (0.90 ≫ threshold) but its yield
   is *staged*, not all-at-once.

---

## 5. Negative controls (plan §6 — a pipeline that never rejects is coherent-and-wrong)

| control | what it poisons | expected | observed | verdict |
|---|---|---|---|---|
| **poisoned walker** (fixture module `PoisonedWalkerControl`) | a real type confusion behind the `pyval` façade: assert an int-only dict yields a `"ghost"` string leaf | MUST stay UNPROVEN | `poison_type_confusion`: Timeout on Alt-Ergo **and** Z3 (unproven) | **PASS** — the sound value model rejects type confusion |
| **poisoned frame** (throwaway, reverted) | a body declaring `writes {p}` that also mutates `q` | MUST be rejected by Why3 | `this expression produces an unlisted write effect` | **PASS** — the WL-05 frame VC bites |
| **poisoned refactor** (Track R oracle; throwaway, reverted) | a behavior-changing emitter edit: `op_translate` mistranslates `+` → `"PLUS_POISON"` | MUST turn the corpus byte-diff red | `diff -rq` fired on **7 of 15** sampled reference files (0001,0004-0007,0009,0014 — those using `+`); reverted clean | **PASS** — the reference corpus is a live behavioral oracle for Track R |

All three controls FAIL the pipeline as required, confirming the conversion/refactor
gates are not coherent-and-wrong. The poisoned walker is retained in the committed
`fb1_fmap_spike.mlw`; the poisoned frame and poisoned refactor were reverted.

---

## 6. Ledger assertions (re-verifiable)

```
$ find src/self-annotate/src -name '*.py' -exec grep -h '\trusted' {} \; | wc -l
1240
$ git status --short src/pycsl/ src/self-annotate/ | grep -v '^??'
(empty — src/pycsl + mirror byte-identical to HEAD)
$ git status --short src/pycsl/proof_axiom_allowlist.py src/self-annotate/src/proof_axiom_allowlist.py
(empty — axiom allow-list untouched)
$ grep -c '^\s*axiom\b' test-suite/corpus/conformance/spikes/fb1_fmap_spike.mlw test-suite/corpus/conformance/spikes/fb1_wl05_spike.mlw
0   (prose mentions of the word "axiom" only; no axiom DECLARATION; no .mlw pipeline axiom added)
```

- `\trusted` = **1240**, unchanged.
- `src/pycsl` + mirror **byte-identical to HEAD** (all benchmark & negative-control
  probes reverted).
- 3-axiom ledger untouched: no `.mlw` `axiom` declaration in either committed spike;
  `proof_axiom_allowlist.py` (both copies) unchanged. (`fb1_fmap_spike.mlw` *uses*
  the axiomatized `fmap.Fmap`/`set.Fset` stdlib theories — flagged in §2 as a
  widened trusted base, but that is a stdlib `use`, not a pipeline-emitted axiom.)

## 7. Pointers
- Benchmarked-against: `getting-better/tier3/fb1-feasibility-spike.md`,
  `…/emission-defect-spike-findings.md`, `…/whole-body-census.md`
- Fixtures (committed, `git add -f`): `test-suite/corpus/conformance/spikes/fb1_fmap_spike.mlw`,
  `…/fb1_wl05_spike.mlw` (baseline: `…/fb1_pyval_spike.mlw`)
- Plan: `generic-dict-str-and-plan.md`; report: `generic-dict-str-and.md`;
  discipline: `config/skills/self-tcb-reduction/SKILL.md` §10–§11
