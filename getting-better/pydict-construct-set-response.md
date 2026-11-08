# Response: pydict copy-and-set-field / dict-comp CONSTRUCTION (independent review)

**Reviewer:** independent (report + repo + oracles only; no sub-loop rationale seen).
**Date:** 2026-08-15. **Baseline:** HEAD `5fd6567b`, trusted count **721** (verified before and after;
all probe edits reverted byte-identical — md5 `342b8ee7…` Module6_WhyMLTranspiler.py mirror,
`8c657252…` Module3_Weaver.py mirror; no stray why3/pycsl processes left).

## Verdict up front

**GATE-C REJECT as escalated — 0 sole-blocked consumers found (my count), the ~10-15 estimate is
OPTIMISTIC, and HALF the requested primitive already exists in the emitter.** The correct move is a
REFRAME, not a build: pivot to wall #1 (Term recognizer-grammar arms) and treat the filtered
dict-comp fold as a *follow-on residual* of wall #1 (see §5).

---

## 1. The report's premise is half-wrong: copy-and-set ALREADY EXISTS

The report claims (§1) the emitter "has NO faithful model for CONSTRUCTING a new/updated map" and
that `d[k] = v` "lowers today to an opaque facade or type-fail". **REFUTED for the set/copy-and-set
half, by reading the live emitter and by an emit oracle:**

- `src/pycsl/module6_whyml/statements.py:1217-1288` — body `d[k] = v` on a **local** dict and on a
  **self-field** dict lowers to `map_update_some` (`val map_update_some (m: map 'k (option 'v)) (k:'k)
  (v:'v) : map 'k (option 'v) ensures { result = Map.set m k (Some v) }`) — exactly the report's
  primitive #1, polymorphic, already landed.
- `statements.py:103-149` (`_build_dict_literal_map`) — variable-valued dict **literals** fold
  `map_update_some` over the pairs (the R3 soundness fix). `del d[k]` → `map_update_none`
  (`Map.set m k None`, statements.py:1350-1357). A pinned `__setdefault` building
  `map string (option int)` also exists recognizer-scoped (preamble.py:2650-2656,
  `_extract_array_lengths`).
- **Emit oracle (ran):** scratchpad `param_dict_mut_probe.py` — a module-level
  `def strip_key(d: Dict[str, str])` doing `d["happy"] = ""` with `#@ assigns d`:

  ```
  PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py <scratchpad>/param_dict_mut_probe.py --no-proof --keep-mlw
  → [level] L1 ✓ L2 ✓ L3-tc ✓
  emitted:  let strip_key (d: ref (map string (option string))) : array string
              writes { d }
            = … d := map_update_some !d "happy" ""; …
  ```

  So even the *caller-visible param* set is faithful (by-ref + `writes {d}`) for FREE FUNCTIONS.
  Only METHOD dict-params are rejected (`_reject_param_collection_mutation`, statements.py:1201-1204,
  the documented WL-05 boundary) — and fixing THAT is an aliasing/frame capability, not `Map.set`.

**What is genuinely missing** (confirmed by reading `expressions.py:11914-11922`): a general
dict-comprehension lowers to the opaque facade `val dict_comp (x: int) : int` applied to `0` unless
the narrow `_dict_content_comp` (identity-key + pure-int value over `array int`) fires. `dict(d,**u)`
/ `.copy()` / `.update()` on dicts are likewise unmodeled. So the wall, correctly stated, is ONLY the
**filtered dict-comp / copy-update fold** — a strictly smaller capability than escalated.

## 2. Primitive faithfulness — CONFIRMED (the report is right here)

Hand `.mlw` authored and proved (scratchpad `pydict_construct_probe.mlw`), using the emitter's own
program-level devices (`map_update_some`, `str_eq_op`):

- `dict_set`: `ensures { Map.get result k = Some v }` + frame `forall j. j <> k -> Map.get result j
  = Map.get d j`.
- `dict_comp_filtered`: bounded loop over a key-seq with guard `k <> excl /\ Map.get src k <> None`,
  variant `Seq.length keys - !i`, postcondition = exact filtered-comp semantics (guarded keys copied,
  everything else `None` off the empty base).
- `non_vacuity_witness`: derives concrete facts (`Map.get d3 "a" = Some "x"`, `Map.get d3 "b" = None`)
  at a call site.

```
why3 prove -P alt-ergo pydict_construct_probe.mlw
  dict_set'vc            Valid (0.04s, 19 steps)
  dict_comp_filtered'vc  Valid (0.12s, 601 steps)
  non_vacuity_witness'vc Timeout (5s)          # string DISEQUALITY — known Alt-Ergo gap
why3 prove -P z3 pydict_construct_probe.mlw
  all three              Valid (≤0.03s)
```

No axiom, no facade. "Trivially faithful" **CONFIRMED** (with the banked wall-lessons (g) caveat:
goals needing string disequality require Z3 in the best-of-N).

## 3. CONSUMER EXISTENCE — the load-bearing artifact: **0 sole-blocked**

### 3a. Census (ran; script + JSON in scratchpad `census_dict_construct.py` / `dict_construct_census.json`)

AST census over all 721 `\trusted` markers (696 mapped to a live twin): **99** live bodies construct
a map at all; **74** use a genuinely-missing shape (dict-comp / `dict(...)` / `.update` / `.copy` /
`.setdefault` — the rest use only the already-supported `d[k]=v` local/self-field store). Every one
of the 74 was co-blocker-tagged from its live body; the ≤2-co-blocker head of the list was then read
function-by-function. Result:

| candidate | construction | sole-blocked? |
|---|---|---|
| `_sha256_file` ×2 (audit_proof_reverify, pycsl.py) | `.update` | FALSE POSITIVE — hashlib `.update`, not a dict |
| `Module6_WhyMLTranspiler.__init__` | dictcomp | BANNED-VACUOUS (`__init__` absorbs into the record decl — run-#5 lesson; a count cut would be fake) |
| `_render_callee_condition` (M6) | dictcomp `{p: a for p,a in zip(…)}`, faithful `map string (option string)` | **NO — probed, see 3b: 3 further blockers** |
| `_parse_extracted_contracts` (Weaver) | `.setdefault().extend()` + `d[k]=v` | NO — `Dict[int, List[CSLNode]]`: values are CSLNode lists (no CSLNode ADT exists — wall-lessons §roots #4), reads `extraction` records, cross-object `self.parser_module.parse_node_contracts` |
| `_emit_subtyping_goals` (functions.py) | dictcomp `{f['name']: f}` | NO — values are whole `Dict[str,Any]` func records = the report's OWN §4 out-of-scope (heterogeneous pyval root) |
| `apply_inline_globals` (ir_inline) | dictcomp `{g['name']: g['class']}` | NO — source is `List[Dict[str,Any]]` (heterogeneous reads), plus `f.pop('pure', None)` mutation of `ir_data` elements |
| `_record_classification` (monomorphize) | `.setdefault` 2-level | NO — nested `ir_data.setdefault(...)['uninstantiated'] = List[Dict[str,Any]]` heterogeneous literal + `Set[Tuple[str,str]]` |
| `_index_proofs_dir_by_file` (audit_proof) | `.setdefault` | NO — `Path.iterdir`/filesystem + try/except (os-boundary class G) |
| `_subst_var` (Weaver) | dictcomp over dataclass fields | NO — `_dc_fields`/`_dc_replace`/`getattr` = the CSL-dataclass Weaver boundary + self-recursion |
| `sort_functions_by_scc`, `run_ir_semantic_checks`, `_desugar_acts`, … | dictcomp | NO — heterogeneous IR-dict values/sources |

Everything below this head carries ≥4 tagged co-blockers (raise-model, ast.walk, nested-def,
reflection, giants self-calls). **Count of stubs whose SOLE blocker is dict-construction: 0.**

### 3b. Non-destructive `--fun` probe of the BEST census candidate (ran)

`_render_callee_condition` is the one candidate whose dict-comp is exactly the report's primitive
(faithful `map string (option string)` from two `List[str]` params). Its mirror stub carries the
verbatim live body, so the probe was minimal: removed the single `#@ \trusted` marker line, ran

```
PYTHONHASHSEED=0 timeout 300 python3 src/pycsl/pycsl.py src/self-annotate/src/Module6_WhyMLTranspiler.py \
    --import-path src/pycsl --fun module6_whymltranspiler___render_callee_condition [--keep-mlw --no-proof]
→ [level] L1 ✓ L2 ✓ L3-tc ✗
→ File "….mlw", line 583: unbound function or predicate symbol '_in_spec'
```

and the emitted target body (captured from the kept `.mlw`) is:

```
let module6_whymltranspiler___render_callee_condition (self: …) (cond_ir: int)
    (param_names: array string) (args: array string) : _union__render_callee_condition_3
= … let subst = ref 0 in
    … subst := (dict_comp 0);                                   (* blocker 1: the facade — the wall, real *)
    try raise (Return_… (Arm_3_0 (self__expr_to_whyml_4 self cond_ir (const (None: option int)) 0 0)))
    with Exception -> raise (Return_… Arm_3_None) end …
```

Residual blockers ON TOP of dict-construction, read off the artifact:
1. `cond_ir: int` — the `Any` param is int-erased, but the callee val is typed `(x0: emit_ir)` →
   ill-typed even if `subst` were faithful (the emit_ir/pyval value-model wall);
2. bare `with Exception ->` — the try/except-Exception raise-model wall;
3. whole-file L3-tc failure independent of the target: abstract sibling vals emit
   `writes { self._in_spec }` against a record whose fields are prefix-qualified
   (`module6_whymltranspiler__in_spec`) — an unbound-field emitter bug of the
   trusted-val-frame family that gates ANY conversion in this file.

Reverted (marker line restored via Edit); md5 back to baseline `342b8ee7…`; the gitignored generated
`Module6_WhyMLTranspiler.mlw` was regenerated from the reverted source (`L3-tc ✓`, target back to a
trusted val).

### 3c. The report's named candidates — all CONFIRMED co-blocked

- **`substitute`** (proof2why3/canonical.py:52): the dict-construction is only the binder-restriction
  `inner_map = {k: v for k, v in mapping.items() if k not in t.binders}` — precisely the filtered
  dict-comp, faithful-scalar (`Dict[str, str]`). But the body is the 8-arm isinstance dispatch over
  `Var/IntLit/BoolLit/Unsupported/App/BinOp/UnaryOp/Forall/Exists` + self-recursion + tuple-generator
  + frozen-dataclass ctors + `raise TypeError` — **wall #1 in its entirety**. The mirror stub already
  int-erases the param (`mapping: int`). Co-blocked, as the report itself suspected. CONFIRMED.
- **`_collect_*`**: census found exactly **two** map-constructing `_collect_*` trusted stubs —
  `_track_collection_metadata` (5 co-blockers incl. isinstance + `_record_ctor_list_elem` self-call)
  and `_collect_class_fields` (ast.walk + 8 helper self-calls). "Several `_collect_*`" as consumers:
  **REFUTED**.
- **`_extract_happy_properties`**: its construction is `contracts_map[line] = kept` on a **method
  (staticmethod) dict param** — the WL-05 method-param rejection boundary (aliasing/frame capability,
  NOT `Map.set`; note §1 shows the free-function analogue already works). Values are `List[CSLNode]`
  (no ADT) and the filter is `isinstance(n, HappyProperty)` over CSLNode. Sole-blocked: **REFUTED**
  (3 independent walls, none of them the escalated primitive).

## 4. Verdict on the estimate

The "~10-15 un-co-blocked consumers" figure is **OPTIMISTIC — my measured count of sole-blocked
consumers is 0** (population: 74 missing-shape constructors out of 99 constructors out of 721).
The dominant reason is exactly the two exclusions the report itself wrote down: (a) most dict-comp
consumers build **heterogeneous** `Dict[str,Any]`-valued maps (the report's own §4 OUT-scope), and
(b) the faithful-scalar ones sit inside Term-walk / raise-model / Any-int-erasure / CSLNode /
whole-file-gate bodies. This is the tuple-unpack/items-binder lesson repeating: a provable primitive
with 0 sole-blocked consumers.

Honesty caveats on my own oracle: the census is AST-heuristic (its `.update` matcher caught two
hashlib false positives — excluded above; its co-blocker tags were spot-verified by reading the
≤2-tag head, not all 74); `--fun` is known to be spuriously INCOMPLETE-prone, but here it was used
only to READ the emitted body and the L3-tc error, both of which are deterministic emission facts.

## 5. Recommendation

**Do NOT build the primitive now (Gate-C reject). Pivot to wall #1 (Term recognizer-grammar arms) —
with one sequencing note the report should keep:**

1. **Correct the wall statement first.** Copy-and-set (`Map.set`-semantics `map_update_some`) is
   ALREADY landed for locals, self-fields, dict literals, `del`, and free-function by-ref params.
   The open capability is only: general dict-comp fold, `dict(d,**u)`/`.copy()`/`.update()`, and the
   METHOD-param mutation frame (a different, aliasing-class capability).
2. **The filtered dict-comp fold is a FOLLOW-ON of wall #1, not a parallel lever.** Its cleanest
   faithful-scalar consumer (`substitute`) needs BOTH; once the Term-ADT walk lands, the inner-map
   comp becomes `substitute`'s residual blocker — build it THEN, demand-driven, with a live consumer
   in hand (and it is small: §2 shows the whole fold + exact postconditions discharge in <1s).
3. **Bank the two incidental findings** from the probe for the emitter-bug queue: (a) abstract
   sibling vals emitting unqualified `writes { self._in_spec }` → unbound field, a whole-file L3-tc
   gate on `Module6_WhyMLTranspiler.py` (masked-whole-file-blocker family — it will also block
   wall-#1-era conversions in that file); (b) `Optional[str]`-guard `v is not None` lowering via
   `str_hash_op !v <> 0` in the §1 probe emission (hash-collision-shaped None test on a string
   option — worth a faithfulness look, separate from this wall).

## Oracle artifacts (all commands as run)

- `why3 prove -P alt-ergo|z3 <scratchpad>/pydict_construct_probe.mlw` — §2 outputs verbatim.
- `python3 <scratchpad>/census_dict_construct.py` → "total trusted-stub markers mapped: 696 /
  map-CONSTRUCTING live twins: 99" (+ JSON), over `grep -rn '#@ \trusted' src/self-annotate/src`
  = 721.
- `PYTHONHASHSEED=0 timeout 300 python3 src/pycsl/pycsl.py src/self-annotate/src/Module6_WhyMLTranspiler.py
  --import-path src/pycsl --fun module6_whymltranspiler___render_callee_condition` (marker-line
  un-trust, then Edit-reverted byte-identical) — §3b outputs verbatim.
- `pycsl <scratchpad>/param_dict_mut_probe.py --no-proof --keep-mlw` — §1 lowering verbatim.
- Post-review state: count 721; `git status` clean of any src/ change; no leftover prover/pycsl
  processes (`ps` checked).
