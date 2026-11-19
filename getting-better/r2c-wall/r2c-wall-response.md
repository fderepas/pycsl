# Independent review of `r2c-wall.md` (mutation of the IR tree, R2c-caller)

**Reviewer:** independent (no driver log, no backlog, no other agents' notes were read).
**Tree:** `/home/fabrice/git/pycsl`, branch `ghost-assign-bc6`, HEAD `cdbae732` (the report's HEAD
`348874ab` is an ancestor). `src/`, `bin/`, `test-suite/` untouched. All oracle artifacts are under
`getting-better/r2c-wall/review-spikes/`. Every pycsl/why3 job went through
`scratchpad/heavy/heavy.sh`; why3 = `/home/fabrice/.opam/framac-coq8/bin/why3`, Z3 4.13.3.

**One-line verdict.** The report's physics is right (a value model carries an alias-free
caller-tree store; it cannot carry observed sharing), its reclassification of the 11 markers is
right, and "0 complete chains from any single route" is right. Three things need correcting before
it drives an impl plan: (1) the `_emit_first_assign` precondition it puts in front of routes (a)
and (c) is **already fixed on main** (route #294, commit `294dd20e`, 2026-10-20, an ancestor of the
report's own HEAD) — the ordering question in §6 Q4 is moot; (2) the aliasing obligation
(i)–(iv) is **incomplete**: a caller-side hole (`derived_local_hole`, proved Valid in my spike)
is not covered by any of the four rules and needs a fifth, call-site rule; (3) route (d) is
over-scoped — `_emit_specializations` does not itself write through sharing, so it is *pending*,
not *boundary*. Ranking by blockers removed per unit cost: **(c) > (a) > (d) > (b)**.

---

## 0. Oracle runs

| # | command (all via `heavy.sh`, PATH incl. framac-coq8/bin) | artifact | result |
|---|---|---|---|
| O1 | `why3 prove -P z3 -t 20 -a split_vc spike/r2c_writeback.mlw` (the report's spike, re-run) | `review-spikes/rerun_r2c_writeback.z3.out` | **37 Valid**; `caller_twin` line 106 `Timeout (20.00s)`; `alias_hole` line 119 **Valid (1.37s)**. Report §4.2/§4.3 CONFIRMED verbatim. |
| O2 | `why3 prove -P z3 -t 20 -a split_vc review-spikes/rv_derived_local.mlw` (my spike: same defs + 4 twins) | `review-spikes/rv_derived_local.{mlw,z3.out}` | **38 Valid**. `derived_local_hole` Assertion **Valid (0.02s)** — a FALSE claim under CPython (see §2). `derived_local_ok` Valid; `pairs_set_appends` Valid; `pairs_set_dup` both asserts Valid. |
| O3 | `pycsl.py review-spikes/r294_false_proof_hval_alias.py` (full proof; the ch29 `e: Dict[str,PyVal] = func; return "name" in e` with `ensures \result == False`) | `review-spikes/r294_false_proof_hval_alias.out` | `Prover result is: Timeout (30.00s)` → `[-] Verification FAILED`. The ch29 false proof **no longer proves**. |
| O4 | same, `r294_false_proof_hval_alias_dictcopy.py` (`e = dict(func)`) | `review-spikes/r294_false_proof_hval_alias_dictcopy.out` | L3-tc error `This expression has type string -> option hval, but is expected to have type int` → FAILED (fail-closed refusal, not the empty map). |
| O5 | same, `r294_false_proof_str_alias.py` (`Dict[str,str]`) | `review-spikes/r294_false_proof_str_alias.out` | `Timeout (30.00s)` → FAILED. |
| O6 | `pycsl.py review-spikes/rv_q3.py --no-proof --keep-mlw` and `rv_q6.py` (the report's q3/q6) | `review-spikes/rv_q{3,6}.out` | both `[ir-semantic] … route #289 … Store through the list's own name.` Report §2.3 refusal table CONFIRMED. |
| O7 | `git merge-base --is-ancestor 294dd20e 348874ab` | — | true. `294dd20e repair(#294): dict first-assign keeps a non-empty-construction RHS; str-set assign keeps a non-set() RHS` (2026-10-20). Live code: `src/pycsl/module6_whyml/statements.py:81-96` (dict) and `:1281-1298` (str-set). Corpus witnesses `3430–3436`, `3442`, `3443` exist. |
| O8 | greps | — | `pairs_set|hval_list_set|hval_list_snoc|hmap_set` in `src/pycsl`: 0 hits (confirmed). `#@ \trusted` in mirror: 449 (confirmed). Literal builder PREPENDS: `expressions.py:1336-1341`, `preamble.py:8049` (confirmed). |

A counterexample attempt on `caller_twin` (`-P "Z3 4.13.3 (counterexamples)"`) was refused by the
local why3.conf (`No prover … corresponds to`), so the twin stays "Timeout", as the report says.
Not chased further: it is the report's claim, and a timeout on a false twin is the expected shape.

---

## 1. Factual corrections to the report

1. **`_emit_first_assign` is fixed on main (route #294).** §5(c) "A known false proof is adjacent and
   must be fixed first", §5 comparison table "(c) … `_emit_first_assign` false proof underneath",
   and §6 Q4 are **stale**. O3–O5 show the three ch29 false proofs no longer prove at HEAD; O7 shows
   the fix predates the report's HEAD by two days. The non-literal RHS is now KEPT (`statements.py:
   81-96`: the ν-typed empty base is used only for a `DictLit` or an RHS that already lowered to the
   int-typed everywhere-None map). Consequence: route (c)'s "≈1 h after the first-assign fix" is
   "≈1 h now", and (c) and (a) have **no ordering precondition** left. What #294 does *not* give: a
   lowering for `copy.deepcopy(decl)` / `dict(func)` as an hval — O4 shows `dict(func)` is a
   fail-closed L3-tc error, so sd/sf still need "deepcopy = identity on hval" (report §5c, correct).
2. **File paths.** `ir_inline.py` and `monomorphize.py` live in `src/pycsl/frontend/`, `scc.py` in
   `src/pycsl/module6_whyml/`. The cited line numbers are otherwise exact at HEAD (checked: ir_inline
   505/527/538, monomorphize 138/445/489/503/508-509/530/534/557/569-570/579/672/675, scc 184/192).
3. **sf's "conditional alias" is semantically vacuous.** `contracts = spec.get("contracts") or {}`
   followed by `for clause in (...): if clause in contracts: contracts[clause] = …`
   (`monomorphize.py:569-574`). When `spec["contracts"]` is absent/`None`/`{}`, the fresh `{}` has
   no clause, so **no store happens on either branch**. "Write iff present and truthy" collapses to
   "write iff the clause is present in `spec["contracts"]`". No `or {}` modelling is needed for sf;
   the general `.get(k, [])`-then-`append` hazard remains (it is live in es's local `by_generic`
   only through `setdefault`, which does write back). Over-scoped hazard, not an error.
4. **es's top-level stores need no new machinery.** `ir_data["type_decls"] = new_type_decls`,
   `ir_data["functions"] = new_functions` (508-509) REPLACE whole keys with fresh lists — exactly the
   q1/q8 `map_update_some` shape the report says is already carried (§2.2). es's only path-stores are
   into LOCAL trees (`by_generic.setdefault(..).append`, `spec["name"] = …` on a deepcopy result). So
   es is "C-top (carried) + L", and belongs to route (c)'s scope, not (a)'s.
5. **Insertion order is already inconsistent.** The report correctly makes `pairs_set` append
   (O2 `pairs_set_appends`), but the literal builder PREPENDS (`expressions.py:1336-1341`, "prepend
   order is observationally irrelevant" — true for `pairs_get` only). The moment an `.items()` /
   `.values()` lowering over `hpairs` lands (ra needs one, §3 row 1), literal-built maps iterate in
   REVERSE Python order while stored keys append. Fix the builder to append (or reverse at the end)
   in the same build that adds `pairs_set`. Also O2 `pairs_set_dup`: on a pair list with a duplicate
   key, `pairs_set` replaces the first binding only and the stale one survives — harmless for
   `pairs_get`, wrong for any future `len`/iteration. A Python literal `{"a":1,"a":2}` is the only
   source today; worth an `assert distinct-keys` in the builder rather than a lemma.
6. **§3 recount: CONFIRMED** from the live lines — C = {ra, ic, es-top}, S = {m5-epi, m5-ppc},
   L = {cgd, sd, sf, scc}, X = {ef, pts}. With correction 4, the genuinely "caller path-store" set is
   **ra alone** (store of a FRESH value into a loop element of the parameter's list), plus the S
   pair's appends into a self field. ic is the only body whose *meaning* depends on sharing.
7. "`_Inliner(funcs, ..)` reads callee bodies rewritten through the alias" — CONFIRMED
   (`ir_inline.py:430-436`: the inliner is built over `funcs`, the loop rewrites
   `rewrite_funcs` elements, which are the same dicts).

---

## 2. SOUNDNESS: the obligation (i)–(iv) is incomplete; what must be refused

**The hole.** `review-spikes/rv_derived_local.mlw` `derived_local_hole` (O2, Valid):

```
let funcs = fns !ir in            (* Python: funcs = ir["functions"]  — read BEFORE the call *)
rewrite_all ir v;                 (* a converted callee with `assigns ir` *)
… assert { pairs_get p "symbol_table" = Some st0 }   (* funcs[0]["symbol_table"] is the OLD table *)
```

CPython: `funcs` is the same list object, its element now has `v`. The value model proves the
stale value. This is **not** `alias_hole` (which stores a shared value INTO the root before the
call): here the sharing is created by a plain READ out of the root, and the mutator is a *callee*
whose frame is honest (`assigns ir`). None of the report's rules fires: (i) is about the callee's
parameters, (ii) about reads inside the mutating body, (iii) self fields, (iv) values stored into a
tree. It is live in the mirror in exactly this shape: `apply_inline_globals`
(`ir_inline.py:521,538,542`): `funcs = ir_data.get("functions", [])` … `_inline_calls(funcs, …)` …
`for f in funcs: … f.pop("pure")`.

**Why it matters under `ensures True`.** The report's §4.5 is right that the harm is a frame hole
plus stale no-exception/type-safety VCs. Here the stale snapshot is *in the caller*; the caller is
itself a converted method proving no-exception over the snapshot. E.g. a `KeyError`-freedom VC on
`funcs[0]["body"]` after a callee that `pop`s `"body"`: provable on the snapshot, false in Python.

**Rule (v), call-site kill.** At every call whose contract has `assigns R` where `R` is bound to an
argument `a`, every live local that may share a mutable sub-object with `a` (bound from a subscript
/ `.get` / `.pop` / `.setdefault` / loop target / unpack / comprehension / call result / shallow copy
over `a`, transitively) is **killed**: any later read of it is refused (fail-closed), or the
emitter re-derives it from `R` after the call (sound only for reads that are literally a re-read of
the same path — `funcs = ir_data.get("functions", [])` qualifies; `body_funcs = [f for f in funcs
if …]` does not, because the filter would have to be re-run).

**Is the partner check decidable and complete?**
* *Decidable:* yes. It is a may-alias relation over a FINITE set of names (parameters, locals,
  `self` fields read in the body) computed by a forward, flow-sensitive syntactic walk over the IR
  — the #279/#283/#295 walk is already that. No ownership types are needed as long as the default
  for an unrecognized expression is "may share with every mutable-capable name in scope" (fail
  closed).
* *Complete:* only if the alias-CREATING grammar is closed. The report's (ii) names "the partner
  set of a path prefix" without listing the generators. They must include at least: name binding;
  subscript / `.get` / `.pop` / `.setdefault` / `.items()` / `.values()` results; attribute reads;
  loop targets and tuple unpack; walrus; `or` / if-expression; comprehension elements over a shared
  source (scc's `[func_by_name[n] for n in …]` returns parameter elements in a fresh list);
  shallow copies (`dict(x)`, `list(x)`, `x.copy()`, `x[:]`, `sorted(x)`, `reversed(x)`); default
  arguments; closures capturing a name; a parameter element stored into a self field (escapes to
  every later method — the S pair's `self.program_ir["functions"].append(member_ir)` makes
  `member_ir`'s source a permanent partner of `self.program_ir`); and **every call result of
  mutable-capable type, which must be a may-partner of every mutable-capable argument (and of
  `self` for a method)** because `ensures True` says nothing about freshness. The untracked
  `p002…p010_*_alias.out` probes in the tree suggest this grammar is already being censused at
  the list level; the hval-path rule must inherit all of them.
* *Fresh set (the only things that break sharing):* literals whose elements are immutable or
  themselves fresh; `copy.deepcopy`; a comprehension that builds NEW dicts/lists of immutables.
  NOT fresh: any call result, any shallow copy.

**What exactly must be refused (fail-closed list).**
1. A path store through root `R` in a body where a may-partner of `R` (other than the loop element
   the write-back rebuilds) is read after the store — report (ii), kept.
2. A call with `assigns R` while a may-partner local of the argument is read afterwards — rule (v),
   NEW (O2).
3. A path store whose root is a call result or a shallow copy (#283/#288/#295 shape) — this
   **also refuses the S pair's `member_ir["abstract"] = True`** (`Module5:3167-3171`, `member_ir`
   is `_build_function_ir(...)`'s result) unless a "fresh result" fact exists. The S pair's
   `.append({literal})` forms are fine. Note this in the S-pair chain cost.
4. A store below a parameter element that was stored into a local tree — report (iv), kept (cgd
   stores `func` into `generics`; a later `generics[t]["methods"][j]["k"] = …` would be
   caller-visible).
5. Type-disjointness as the ONLY alias escape for a parameter is valid only when the two carriers
   are Why3-distinct types (a caller that passed one object to both would not type-check). A
   `PyVal`/`Any`-typed parameter is NEVER disjoint. ra's `rename_map: Dict[Tuple[str,str],str]`
   qualifies.
6. On rule (i): "every other same-carrier parameter must be in the frame too" is **trivially
   satisfiable by widening the frame** (`assigns funcs, rewrite_funcs` for ic). Widening is sound
   for the caller (both havoc'd) but does not make ic's BODY sound: the `inliner` object (a call
   result over `funcs`) is read in every later iteration after `f["body"] = body` → refused by
   rule 1/3, not by (i). The report's "ic is refused by (i)" reaches the right answer for the wrong
   reason; say so in the impl plan so nobody "fixes" (i) by widening.

**`alias_hole` and `derived_local_hole` must both be regression witnesses that become emit-time
REFUSALS**, as the report's make-or-break for (a) says. Under the current `--no-proof` discipline
the natural home is `core_ir_semantic` / the #289 arm (`pycsl.py:6391-6416`), not Why3.

---

## 3. Route-by-route

### (a) Path write-back on a `ref` root — AGREE, with carve-outs

* Confirmed: the calling convention exists (q1/q2/q8 as emitted; I did not re-run them — they are
  L3-tc only and the `.out` files are in the tree), the write-back proves (O1 37/37), `assigns
  <root>` + `ensures True` is a sufficient *callee* contract shape (the havoc of `ir` subsumes any
  path frame).
* Carve-out 1: sufficiency stops at the callee. At the call site, rule (v) is mandatory (§2).
  Without it, (a) converts a stale-snapshot false proof into every converted caller of a converted
  mutator.
* Carve-out 2: es is not in (a)'s scope (correction 4); the S pair's `member_ir[...] = …` is
  refused (§2 item 3). (a)'s real consumers are **ra** and the S pair's **appends**.
* Carve-out 3: the ra read seams. "`new_st = {}` → `map string (option string)` cannot be turned
  into an `HMap`" is true but the cheaper route is **sink-driven carrier choice**: a local dict
  whose only escape is a store into an hval tree is built AS an `HMap` from `PNil` with
  `pairs_set` in the first place (prescan on the sink, like `_pyval_locals`). No map→HMap
  conversion is needed. That removes one of ra's four seams for free with (a)'s own ops.
* Cert: 4 structural functions + 3 `let rec lemma`s, ledger stays 3 — agree; O1/O2 prove the
  lemmas without any axiom.

### (b) Heap / regions — REFUTE as a next step

Agree with the report's own cost analysis and add: under `requires True` a heap model cannot even
state the separation ic needs, so (b) buys "faithful ic" only in a contract shape the loop forbids;
and ic's other blockers (`_walk_dicts` generator, the `_Inliner` object, `_cb` set) are each a
build. 0 markers, largest cert delta, two coexisting models. Not before every (a)/(c) consumer is
exhausted.

### (c) R2c-local — AGREE, and it is now the cheapest route (precondition gone)

* With #294 on main, (c) has no ordering precondition. It is the report's own spike minus the `ref`
  parameter, with the obligation reduced to a syntactic fresh-root test (literal / comprehension of
  immutables / `copy.deepcopy`) plus report rule (iv) and §2 item 3.
* Scope confirmed: cgd (138), sd (530-534, loop element of a deepcopy), sf (557, 569-570, 579),
  scc (184), and es's locals (445, 489, 503). That is 4-5 of the 11 markers whose *first or second*
  blocker is this store.
* `copy.deepcopy` = identity on hval: agree it is faithful for a pure ADT (and a `deepcopy` of a
  caller element is the ONE construction that makes a local root alias-free by definition).
* Residual risk: a `#283`-style partner through a comprehension (scc) is still refused unless the
  comprehension lowering knows it builds a fresh list of *strings* (`sorted_names` is
  `List[str]`, immutable elements → fresh). That is a type test, cheap.

### (d) Certified boundary — AGREE for ic only; es is pending, not boundary

* ic: the body's meaning depends on two names for one object (confirmed §1.7). Boundary, with the
  reopening conditions the report gives, and with the R6 frame-honesty audit first (agree).
* es: its body does not write through sharing (correction 4). The `generics` staleness is in
  `monomorphize()` (`monomorphize.py:57,86,93`), which is a *different* stub, and it is exactly
  rule (v) at the `_emit_specializations(ir_data, …)` call site. So es stays pending on value-model
  seams; `monomorphize()` is the one that would be refused by (v) and could be boundary later.
* Make-or-break (frame honesty of the boundary set): agree; it is ≈1 h and should run before any
  ledger entry.

---

## 4. Ranking (expected blockers removed per unit cost; complete chains are 0 everywhere)

| rank | route | consumers whose store-blocker disappears | cost | soundness debt it adds |
|---|---|---|---|---|
| 1 | **(c) R2c-local** | cgd, sd, sf, scc, es-local (4-5 markers) | ≈1 h spike + one emitter build (same 4 ops as (a)), no contract-shape change, no call-site rule | fresh-root test + rule (iv) + "store on call result refused" |
| 2 | **(a) ref-root write-back** | ra, S-pair appends (3 markers) | core done (O1); + partner walk (i)-(v) over hval paths | rule (v) is MANDATORY; `alias_hole` + `derived_local_hole` must refuse at emit |
| 3 | (d) boundary, ic only | 0 (ledger honesty) | ≈1 h frame audit | hides an under-declared trusted frame if the audit is skipped |
| 4 | (b) heap | ic faithfully, 0 complete | days + new cert + 6-file re-proof | frame-plane collapse |

(c) before (a) because (c) needs no call-site rule, its ops ARE (a)'s ops (so (a) inherits the
cert for free), and it touches the larger marker set. (a) second because ra is the only chain that
could complete with ≤2 further builds (store + sink-driven `HMap` local = 1 build; `.items()` over
`hpairs` + `isinstance → match HStr` = 1 build; prescan seeding is a known arm) — §6 Q5's answer is
"ra, plausibly 2 builds after (a) lands, not ≤2 builds total".

---

## 5. Minimal make-or-break spike for the top route (c)

One hand `.py`, through `pycsl --no-proof --keep-mlw` then a Why3 witness, ≤ half a day:

```python
#@ requires True
#@ ensures True
#@ assigns \nothing
def cgd_min(funcs: List[Dict[str, PyVal]]) -> Dict[str, PyVal]:
    generics: Dict[str, PyVal] = {}
    for func in funcs:
        t = func.get("self_type") or ""
        if t == "G":
            if t not in generics:
                generics[t] = {"kind": "class", "methods": []}
            generics[t]["methods"].append(func)        # the R2c-local store (cgd:138)
    return generics
```

Pass criteria (all three, else (c) is "enabler with no consumer" and drops below (a)):
1. L3-tc clean, with the append lowered to a write-back on the LOCAL root
   (`generics := map_update_some !generics t (HMap (pairs_set p "methods" (HArr (hval_list_snoc …))))`),
   and the dict literal `{"kind": .., "methods": []}` lowered to a real `HMap`, not `any_map ()`.
2. Witness: a caller asserts `hval_list_len (methods of generics["G"]) = 1` after one matching
   element → Valid; its twin `= 0` → not Valid.
3. Refusal witness: the same body plus `generics["G"]["methods"][0]["x"] = 1; return funcs[0]` is
   REFUSED at emit (rule (iv): store below a stored parameter element), not proved.

If 1 fails only on the dict-literal → hval seam, that seam is the next blocker and is measured as
such; the store itself is then "about 0 marginal", as the report predicts. If 1 fails on the
loop/prescan seam (`ref 0`), cgd stays ≥2 and R2c-local is an enabler without a consumer.

---

## 6. Gate R answers

1. §3 reclassification: **CONFIRMED**, with es moved from C-path to C-top(carried)+L.
2. §4: **CONFIRMED** (O1) that caller-tree mutation is a modelling choice for alias-free roots and
   fundamental only where code depends on sharing; `assigns <root>` + `ensures True` is sufficient
   for the callee and **insufficient at the call site** without rule (v) (O2).
3. Partner obligation: **decidable fail-closed** with the existing walk extended to hval paths,
   call results as may-partners of their mutable arguments, and the call-site kill — no ownership
   types needed. Complete only with the explicit alias-creating grammar of §2.
4. Ordering: **moot** — #294 is on main (O3–O5, O7). No precondition before (a)/(c).
5. ≤2 builds: none now. ra is the closest after (a): about 2 further builds.
