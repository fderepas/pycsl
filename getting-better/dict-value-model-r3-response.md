# Independent review of `dict-value-model-r3.md`

*Reviewer run 2026-10-28T02:22Z–T03:00Z on `ghost-assign-bc6` HEAD `08a606ea2` (`src/` byte-identical
to `59985d6e9`, the report's base). `src/` and `bin/` were not touched. Every scratch artefact is under
`scratchpad/wall-dict-review/` (untracked). Every pycsl / why3 job ran through
`scratchpad/heavy/heavy.sh`. Both NORMAL heavy slots were held for the whole window by other
executors' multi-hour proofs (a 16 h `pycsl-u411` mirror proof and a 9 h `wall-dict/drv/get_hash.py`
run, plus a queued NORMAL waiter on `gate.lock`), so this review's oracle is the QUICK class
(`--no-proof --keep-mlw` emission + grep of the real WhyML) plus one hand-written `.mlw` spike,
proved with Alt-Ergo (and cross-checked with Z3) at 03:11Z when slot 1 freed (§1 S1, §5.2). No
whole-file pycsl proof was run.*

---

## 0. Verdict in one paragraph

The report's measurements hold up under re-measurement, and its central numbers (19/370 first-link,
0/4 after one `hval` link, 5/27 mirrors cleared by a perfect dict model) are the right ones for the
**conversion** question: a `Dict[str, Any]` value model is **not worth building** for conversions,
and the report says so correctly. But the report mis-frames the **hashing** question. It prices the
residual as "refuse every underivable hashed value, 27/53 mirrors", and never asks *what claim the
admitted sites falsify*. Measured here: the `#349` refusal and the `#UND` admission are independent of
any `no_exception` claim (q5b), PyCSL's own trigger model injects an exception VC **only** under a
claim (p_idx, p_keyerr) and treats un-claimed callees as **ambient** even from a `no_exception \all`
caller (p_claim_calls_unclaimed, `pycsl-exception-model/SKILL.md:118-132`), and **0 of the 679
flip sites sit in a mirror function that claims `no_exception`** (`q5cost.py`, at both `3b2d2e763`
and HEAD). The only corpus files in the flip scan that carry a claim are two *expected-FAIL* tests.
So the 27-mirror cost is the price of refusing where nothing is claimed. The route I recommend is a
**claim-gated `#UND` refusal** (§5): refuse an underivable hashed value exactly where the function
claims exception-freedom, which is where the red-team false proofs (`pycsl.py:5152-5154`, "PROVED
`no_exception \all`") actually live. It costs 0 mirror sites, changes no WhyML, adds no axiom
(ledger stays 3) and no facade. It does not convert a single stub, and it is honest about that.
Whether it "closes" the residual depends on one question the project must answer, not me: does
LINK-3 claim that the emitter never raises (§5.4)? If yes, only the full flip is honest and the
right move is to certify the 27 mirrors as a boundary; if no, the gated rule closes the family.

---

## 1. Oracle runs (the artefacts this review stands on)

All commands from `/home/fabrice/git/pycsl` with `PATH=$HOME/.opam/framac-coq8/bin:$PATH`;
`H=scratchpad/heavy/heavy.sh`, `R=scratchpad/wall-dict-review`.

| id | command | key output | confirms / refutes |
|---|---|---|---|
| **O1** | `$H python3 src/pycsl/pycsl.py $R/q4_hash_get.py --no-proof --keep-mlw` | rc 0, `L3-tc ✓`; `q4_hash_get.mlw:23` `let s = ref (any int) in`, `:30` `v := (match Map.get m "a" with \| Some v_ -> v_ \| None -> pycsl_none end)` | **confirms** §3.2 q4: `{m.get("a")}` admitted under `no_exception \all`, no hashing obligation emitted |
| **O2** | same on `$R/q5_hash_sub.py` | rc 1, `[ir-semantic]: 'h2' line 7: \`v\` (an instance of ['a list / dict / set']) is HASHED by \`{v}\` … PYCSL-R349-UNHASHABLE-RECORD` | **confirms** q5: `{m["a"]}` refused. Note the message says the subscript value *is* `a list / dict / set` (the `#UNK` reading), not "underivable" |
| **O3** | same on `$R/q6_hash_ir.py` | rc 0; `q6_hash_ir.mlw:16` `val f_get_1 (x0: int) : int`, `:20` `let names (funcs: array int)`, `:30` `seen := map_update_some !seen (f_get_1 1878939832) 0` | **confirms** q6: element erased to `int`, receiver-less `.get` facade |
| **O4** | `$R/q5b_hash_sub_noclaim.py` = q5 **without** the `no_exception` line | rc 1, same `PYCSL-R349-UNHASHABLE-RECORD` | **new fact**: the hashing refusal is **not gated on a `no_exception` claim** |
| **O5** | `$R/p_idx_noclaim.py` (`return xs[5]`, no claim) vs `$R/p_idx_claim.py` (with `no_exception \all`) | no-claim `.mlw`: `xs[5]` bare, no predicate; claim `.mlw:14`: `begin assert { in_bounds ((Array.length xs)) (5) }; xs[5] end` | **new fact**: PyCSL injects the trigger VC only under a claim (Why3's own `Array.([])` precondition still applies to arrays; it does not to maps, see O6) |
| **O6** | `$R/p_keyerr_noclaim.py` (`return d["a"]`, `Dict[str, int]`, no claim) | rc 0; `.mlw:13` `(match Map.get d "a" with \| Some v_ -> v_ \| None -> 0 end)` | **new fact**: an un-claimed KeyError is admitted, no VC, continuation with a sentinel. This is the same model shape as the admitted `#UND` hash site |
| **O7** | `$R/p_claim_calls_unclaimed.py` (`caller` claims `no_exception \all`, calls un-claimed `h` that hashes `m.get("a")`) | rc 0; `.mlw` `let caller (m: …) : int ensures { (result = 1) } = (h m)` with no assert | **new fact**: the inter-procedural default is *ambient* (skill §"Inter-procedural rules", strict flag off). A claim-gated refusal leaks exactly as much as every other implicit exception already does |
| **O8** | `$R/q2_pyval.py` | `.mlw:82-83` `None -> (HInt pycsl_none)`, `HInt _ -> (any bool)` | **confirms** §3.2 q2: absent key is `HInt`, so the `isinstance(_, str)` test has a nondeterministic arm |
| **O9** | `$R/q3b_typeddict.py` | rc 1; `.mlw:14` `(if (node.py_type = 1734671427) then 1 else 0)`; Why3: "has type string, but is expected to have type int" | **confirms** q3b hashed-literal clash on a record field |
| **O10** | `$R/q7_td_boundary.py` | rc 1; "expected to have type PyCSL_Program.varir" at `.mlw:29` | **confirms** q7: no modelled `Dict[str, Any]` → TypedDict cast; fails closed |
| **O11** | `$R/p_pyval_return.py` (`-> Dict[str, PyVal]`, `return node`) | rc 0; `.mlw:69` `let function ident (node: map string (option hval)) : map string (option hval)` | **refutes as stated** §6(a) "selection … not on a return (#69)": a `Dict[str, PyVal]` *return annotation* is selected today |
| **O12** | `$R/p_pyval_bare_return.py` (`-> PyVal` and `-> Tuple[PyVal, PyVal]`) | `let function first … : hval` type-checks; `let function pair … : (int, int)` clashes (`hval` vs `(int, int)`) | **qualifies**: bare `PyVal` returns are selected; `PyVal` inside a `Tuple[...]` return is int-erased. That, not #69, is the return-side gap for stub 398 (`-> "Tuple"`) |
| **O13** | `python3 $R/q5cost.py` (pure Python over `mirflipA.tsv`, the `3b2d2e763` mirror text and HEAD) | `sites 679 distinct functions 202 mirrors 27`; claim-gated: `0 sites in 0 functions, 0 mirrors` at base and at HEAD; Q5 narrow rule (`.get` on a *declared* `Dict[str, Any]`/dict/IR receiver, ≤2 hops): `35 sites, 21 functions, 6 mirrors` (`expressions` 12, `functions` 7, `statements` 7, `types` 6, `stmt_control_flow` 2, `audit_proof` 1) | **new measurement** for §5 and for report Q5 |
| **O14** | `grep -c no_exception` over the 16 files of `e1-r392-395/corpus-flipA-firstscan.tsv` | 14 files: 0; `3341_…` and `5069_…`: 2 each, both `# pycsl-expected: FAIL` | **new measurement**: no claimed PASS file in the flip scan |
| **O15** | greps | `#@ \trusted` 442; `Dict[str, Any]` 277 (mirror) / 1833 (src); `grep -rhc '#@ no_exception' src/self-annotate/src` = 9 lines in 4 files (`exception_model.py`, `frontend/desugar.py`, `module6_whyml/expressions.py`, `module6_whyml/stmt_control_flow.py`) | **confirms** §1 counts; the mirror barely claims `no_exception` |
| **O16** | per-mirror census over `scratchpad/wall-dict/flipclass.tsv` | `mirrors 27 dict-only 5 [audit_proof_reverify, audit_proof, ir_schema, frontend/ir_resolve, module6_whyml/preamble]`; `non-dict sites total 170 in 22` | **confirms** §4.4 "5 / 27 cleared, 170 non-dict sites in 22" |
| **O17** | re-read of the report's four §4.5 spike outputs at the Why3-reported spans (`python3` slice of `spike/398.mlw:1386[893:1297]`, `400.mlw:1364[34:438]`, `282.mlw:2535[61:183]`; `034.out`) | 398: span is the hval argument of `tuple_1`; 400: the hval argument of `join_1`; 282: the hval `dep.get("sig", "")` read passed to `_parse_mixin_sig`; 034: hval at a `map string` key | **confirms** §4.5's four "next links" |
| **O18** | source reads `pycsl.py:6231-6234`, `:8222-8234`, `:7490-7510`, `:8462-8696`; `preamble.py:8087-8124`; `Module5_IREmitter.py:6142-6186`; `expressions.py:1595-1600`, `:3633-3640`, `:11625-11640` | as quoted in §2 | confirms §2.2 and §3.1 citations; **refutes** "`hstr_of` exists only in compare and return positions" (§4.5): it is emitted at a `str`-method *argument* (`:11640`, route #296), a set-membership *key* (`:1600`) and a `.lower()` *receiver* (`:3639`) |
| **S1** | `$H why3 prove -P alt-ergo --timelimit 20 $R/rk_hval_chain.mlw` (slot 1 freed at 03:10Z after three timed-out attempts at 02:31Z, 02:36Z, 02:42Z) | rc 0; `pairs_get'vc` Valid (0.02 s), `hval_truthy'vc` Valid, `record_key'vc` Valid (0.02 s), `occ_get'vc` Valid (0.01 s), **`key_reads_goal_name'vc` Valid (0.12 s, 2068 steps)** — `$R/rk_hval_chain.altergo.out` | the §5.2 leaf spike **passes**: the hand-patched 398 chain type-checks, the hval tuple is accepted as a `map` key, the witness is non-vacuous |
| **S1-z3** | same with `-P z3` | the four function VCs Valid (< 0.01 s); **`key_reads_goal_name'vc` Timeout (20 s, 39,270,123 steps)** — `$R/rk_hval_chain.z3.out` | the §3.3 E-matching cost on `pairs_get` is real and prover-dependent: Alt-Ergo discharges the witness in 0.12 s, Z3 does not in 20 s. The pipeline's primary prover is `Alt-Ergo,2.6.3 -a split_vc` (observed in `ps`), so this is a warning, not a refutation |

---

## 2. Claims: confirmed, refuted, qualified

### 2.1 Confirmed (with my own artefact)

- **§1 counts** 442 / 277 / 1,833 (O15).
- **§2.2 the `#UND` rule.** `pycsl.py:8222-8234` reads exactly as quoted: an `Any`/`object`/TypeVar
  reached through a container is `#UND` when the receiver's known-value table says `?`; `:7503-7508`
  documents that reading `#UND` as `#UNK` "refused 13 of 53 mirrors and 5 PROVED corpus files" at
  the time.
- **§3.2 probes** q2, q3b, q4, q5, q6, q7 (O1-O3, O8-O10). The `.get` / `[k]` asymmetry is real and
  is a *classification* asymmetry: the subscript value is classed `a list / dict / set` (O2's message),
  the `.get` value is `#UND` and adds no class.
- **§4.4** 5 dict-only mirrors, 170 non-dict sites in 22 mirrors (O16).
- **§4.5** the four next links, as the Why3 spans say (O17). The analysis "one link per capability" is
  correct for the first link.

### 2.2 Refuted or materially qualified

1. **"`hstr_of` exists only in compare and return positions" (§4.5, 282 row).** Refuted (O18).
   Route #296 already projects an `hval` at a `str`-method *argument* (`expressions.py:11632-11640`),
   and — this is the part that matters for route (a) — it **withholds the projection under a
   `no_exception` context**: "the raw `hval` fails Why3 type-check: fail-closed, the dropped TypeError
   is never claimed absent". So the "argument-boundary projection" the report lists as missing has a
   precedent *and a soundness discipline*: it is sound under `requires True / ensures True` because a
   wrong tag means Python raised, and the fixed contract shape claims nothing about raising. Route
   (a)'s consumer links are therefore cheaper and better-understood than §6(a) suggests — and still
   worth one stub each (§4 below).
2. **"`Dict[str, PyVal]` is selected on a parameter or local but not on a return: backlog #69"
   (§6(a)).** Stale as stated. `-> Dict[str, PyVal]` and bare `-> PyVal` are selected today (O11,
   O12). #69's actual content (`driver-backlog.md:157-192`) is a *dict literal in return position*.
   The return-side gap that bites the §4.5 leaf 398 is `Tuple[PyVal, …]` → `(int, int)` (O12).
3. **§4.5's "one link" for 398 undercounts the remaining chain.** The first Why3 error is the hval
   argument of `tuple_1`, but the function's declared return is `(int, int, int)`
   (`spike/398.mlw:1380`) while every component the body builds is `hval`. Fixing `tuple` alone
   leaves a `((hval×5), hval, hval)` vs `(int, int, int)` clash. For this 8-line leaf the chain is
   at least {`Tuple[PyVal,…]` return codomain, `tuple(hval)`}: **two emitter capabilities for one
   stub**, consistent with the levers ledger.
4. **The report never states that the hashing refusal is claim-independent.** It is (O4). This is
   not an error in the report, but it is the fact that re-prices the whole §6 hashing column
   (§3, §5 below). The report's own `#349` provenance says the false proofs were proofs of
   `no_exception \all` (`pycsl.py:5152-5154`: "`s = {d}` PROVED `no_exception \all` (e08 …, e09 …;
   CPython TypeError)").
5. **"The last open family of false proofs" (§0).** Qualified. A proof is false only relative to a
   claim. For a mirror function with the fixed shape and no `no_exception`, the model's continuation
   past a would-be `TypeError` is the same shape as its continuation past a would-be `KeyError`
   (O6: `None -> 0`, no VC) or an un-claimed callee's exception (O7). PyCSL's exception model calls
   that *ambient* by design (`pycsl-exception-model/SKILL.md:118-132`). So the 679 un-claimed mirror
   sites are not false proofs of anything the mirror claims; the false-proof family is the set of
   `#UND` hashes **inside a claimed function**, and that set is empty in the mirror (O13) and
   consists of two expected-FAIL tests in the flip corpus scan (O14).
6. **Minor.** `preamble.py:8012-8013` (quoted in §3.1 as the `hval` definition) says
   `HMap (map string (option hval))`; it is a docstring. The emitted type is `HMap hpairs`
   (`:8087-8088`, and `spike/398.mlw:1073-1075`). The report's table is right; the line citation is
   to the stale comment.

---

## 3. What the report over-scopes and under-scopes

**Over-scoped**

- *The hashing cost.* "27 / 53 mirrors at 679 sites" is the cost of refusing `#UND` **everywhere**.
  The cost of refusing it **where a claim is made** is 0 mirror sites (O13). The report prices only
  the first and then correctly concludes a dict model cannot pay it; it never prices the second.
- *The dict model as "the wall".* The report's own numbers say the dict read is first-link for
  19/370 and that behind it sit hval consumers (§4.5) and 336 non-dict first blockers. Calling the
  object under review "the untyped `Dict[str, Any]` value model" overstates its leverage; §6's
  "What the measurements say" already retreats to "positive derivation for every value source".
- *Route (c).* Pricing a schema-keyed view at all. Its soundness cost (an unproved typing assumption
  on the input) is disqualifying under rule 1, and its yield is 1 mirror. Correctly rejected, but it
  did not need a row.

**Under-scoped**

- *The claim dimension* (whether the hashing site is inside a `no_exception` function) is absent from
  every table. It is the dimension along which the cost collapses.
- *The inter-procedural default.* Under the ambient default (O7), even the full flip does not make a
  `no_exception \all` mirror function sound against a callee's hash site; the flip's 27-mirror price
  buys intra-procedural refusal only. The report should have said what the flip buys.
- *The absent-key sentinel* (`HInt pycsl_none`, O8) is listed as missing for route (a) but not
  costed. It is the one `hval` change that is a WhyML *type* change (a sixth constructor `HAbsent`)
  and so trips the coupling rule (new Rocq/Lean certificate). That is a real cost the report leaves
  out of §6(a)'s "New certificate? No".
- *The `Tuple[PyVal, …]` return codomain* (O12) is the actual return-side gap for the leaf spikes
  and is not in the report's "what is missing" list.

---

## 4. The conversion question: not worth building a dict value model

I agree with the report's reading of its own numbers, and add two:

- Every §4.5 next link is a *different* emitter capability (`tuple`/`join` over `hval`, `hval` as
  map key, `hval` at a typed argument, `Tuple[PyVal,…]` returns), each lands in a big mirror whose
  whole-file re-proof is 1-3 h, and each is worth one stub. O12 adds the return-codomain link to
  that list. R5-str's "1 stub, 3 chains moved by one link" is the right prior.
- The one chain that *could* be finite is the 8-line leaf 398 `_record_key`. I wrote its complete
  hand-patched WhyML (`$R/rk_hval_chain.mlw`, §5.2) to measure that, and it **proves** (S1: every
  goal Valid under Alt-Ergo, the non-vacuity witness in 0.12 s). So the chain for the best leaf is
  measured, not estimated: exactly two emitter capabilities (`Tuple[PyVal, …]` return codomain and an
  hval-polymorphic `tuple`), and Why3 accepts the hval tuple as a `map` key at the hashing consumer.
  Z3 times out on the witness (S1-z3), which is the §3.3 E-matching cost showing up on a 9-line
  function; in a 2,500-line mirror whole-file proof that cost is the risk, not the type-check.
  This does not change the verdict: two capabilities, one `pycsl.py` mirror re-proof, one stub.

**Recommendation for conversions: certify the `Dict[str, Any]` read chain as a boundary.** Reopening
capability, concretely: the day the emitter gains `Tuple[PyVal, …]` return codomains *and* one
hval-polymorphic builtin for another reason, re-run `scratchpad/wall-dict/spike/run.sh` on rows 398,
400, 034, 001, 250 (the small leaves of §4.3); the reopening test is TC-OK on at least two of the five.

---

## 5. The hashing question: the recommended route and its make-or-break spike

### 5.1 Route R-gate: claim-gated `#UND` refusal

**What.** In the per-function hashing pass of `pycsl.py` (the `#349`-`#383` walk at `:8462-8696`,
where `_hc349` is intersected with the unhashable set `_u365` and the refusal is raised at
`:8678-8696`), add the underivable case as a *second* polarity: when the hashed expression's derived
class set is `#UND` (today: "adds no class", `:6231-6233`; the raise is at `:8677-8696`), refuse — **iff the enclosing function
carries a `no_exception` directive** (any form: `\all` or a list that includes `TypeError`; the
per-function flags already exist for the `no_exception` summary, see `Module6_WhyMLTranspiler.py`
mirror `_build_callee_no_exception_summary`). The positive deny-list (`a list / dict / set`, an
unhashable record) stays unconditional exactly as today.

**Why it is the right object.** The false proofs this family produced were proofs of
`no_exception \all` (`pycsl.py:5152-5154`). The trigger model injects exception VCs only under a claim
(O5) and treats un-claimed code as ambient (O6, O7). A claim-gated `#UND` refusal is the hashing
analogue of that rule: where the function claims it does not raise, an underivable hashed value is a
`TypeError` the proof cannot exclude, so the file is refused; where it claims nothing, the site has
the same status as every un-claimed `d[k]`.

**What it costs, measured.**

- Mirrors: **0 sites, 0 functions, 0 files** (O13), at the flip's measurement base and at HEAD. The
  mirror claims `no_exception` on 9 lines in 4 files (O15), none of them containing a flip site.
- Corpus / `pycsl_lib`: of the 16 files in `corpus-flipA-firstscan.tsv`, 14 carry no claim and the
  two that do (`3341`, `5069`) are `# pycsl-expected: FAIL` (O14). The report's "7 root/pyref PASS
  files" are therefore expected to be untouched; the e1 log-mode re-run (§5.2) is the gate.
- Conversion census side effect: the 10 `route#349` first blockers of §2.2 are in un-claimed mirror
  functions, so they move to their next blocker. No conversion is unlocked; the report's "19/19 live
  in flip-refused mirrors" catch (§6(d)) disappears, because no mirror is flip-refused any more.
- WhyML: none. Ledger: 3. Facades: none (nothing is emitted). Corpus byte-diff: a refusal-set change
  only; the `.mlw` of every PASS file is unchanged by construction.

**What it does not do.** It converts nothing. It does not make any hashed value *derivable*. It
re-labels the 679 un-claimed sites from "residual" to "ambient, like every un-claimed implicit
exception", and that re-labelling is only honest if LINK-3's meaning permits it (§5.4).

**Optional second step (report Q5).** Under the gate, closing the `.get` / `[k]` asymmetry costs
nothing in the mirror (both become `#UND`, refused only under a claim). Without the gate, refusing
`.get` on a *declared* `Dict[str, Any]` receiver costs 35 sites in 21 functions of 6 mirrors (O13,
item 2) — so Q5 is affordable only as part of R-gate. Making `[k]` symmetric the other way (treating
the subscript as `#UND` rather than `a list / dict / set`) is a *widening* of admitted programs in
un-claimed functions and needs its own e1 scan; I would not bundle it.

### 5.2 The cheapest MAKE-OR-BREAK spikes

**For R-gate (no emitter edit, no WhyML):**

1. **The e1 log-mode flip, gated.** Re-run the `route394` log-mode patch with the refusal predicate
   `#UND ∧ enclosing function claims no_exception`, over the 53 mirrors, the two corpus trees and
   `pycsl_lib`. Pass: 0 mirror refusals, corpus refusals ⊆ expected-FAIL. **Refuted** if any PASS
   file or `pycsl_lib` module carries a claimed function with a `#UND` hash — then the cost is that
   count, and it is still the true cost of the claimed-but-unproved family. (`q5cost.py` + O14 are
   the static pre-run of this spike and predict pass.)
2. **A red-team probe pair** in the style of e08/e09: `{m.get("a")}` under `no_exception \all`
   (today proves, O1 shows no obligation) must become `PYCSL-R349`-refused; the same body without the
   claim must stay admitted. This is a two-file corpus addition with expectations FAIL / PASS.

**For route (a), should the project still want a leaf (`$R/rk_hval_chain.mlw`, RUN, S1 / S1-z3):**
the verbatim hval theory of `spike/398.mlw:1073-1120`, the verbatim body of `_record_key`
(`spike/398.mlw:1386`) with exactly the two hand-written links — an hval-typed tuple return and
`let function hval_tuple (h: hval) : hval` — plus the real consumer shape of
`_merge_records_best_of_n` (`occ: map ((hval,hval,hval,hval,hval), hval, hval) (option int)`, i.e.
the hval tuple **as a map key**, the hashing position) and a non-vacuity witness
(`key_reads_goal_name`: two records differing only in `goal_name` give different keys, by
`assert`). Result: **pass** under Alt-Ergo (all five goals Valid, witness 0.12 s); under Z3 the four
function VCs are Valid and the witness **times out at 20 s** (39 M steps). Reading: the chain is
finite and two links long for the best leaf, Why3 accepts the hval tuple as a map key, and the
`pairs_get` E-matching cost is real but prover-dependent. If the project ever builds these two
capabilities, the next make-or-break is the `pycsl.py` mirror whole-file proof time with 398
converted, measured against its current time, before the second leaf (400, `join` over hval).

### 5.3 Why not the other routes

- **(a) tagged `hval` for hashing:** the hashing check is a static pre-pass over Python source
  (`pycsl.py:7490-7510`); an `hval` may be `HArr`. The report is right that (a) touches 0 `#UND`
  sites. For conversions, §4.
- **(b) TypedDict views:** no modelled boundary (O10), a union of up to 117 shapes has no Why3
  record, and the closed views over-claim presence (`op` in 5/117 classes). Agreed.
- **(c) schema-keyed view:** an unproved typing assumption on the input; forbidden by rule 1 and
  worth 1 mirror. Agreed.
- **The full `#UND` flip:** honest but 27 mirrors un-proved to refuse 679 sites of which 0 falsify a
  claim. It is the right move only under the strict reading of LINK-3 (§5.4).

### 5.4 The one question that decides between R-gate and "certify as boundary"

R-gate is sound **relative to the trigger model as documented** (claims are per-function; un-claimed
code is ambient). It is *not* enough if the project reads LINK-3 ("the emitter's self-verification")
as "the emitter does not raise on any input" — under that reading every un-claimed `d[k]`, `xs[i]`
and hash in the mirror is already a gap, the fixed contract shape (`requires True / ensures True /
assigns`) does not state it, and the only honest closure is the full flip plus `no_exception` on
every mirror function, which is a different (and far larger) campaign than this wall. The
self-tcb-reduction skill's own words — "type-safety + frame — never value-faithful" — point to the
first reading. The project should write down which it is; this review's recommendation assumes the
first.

---

## 6. Answers to the report's questions (§8)

1. **Is the right object a dict value model?** No. For hashing, the right object is the *claim*: a
   positive derivation for every source (call results through mirror signatures, `ast` attributes,
   dict reads) is the road to lifting refusals in *claimed* code, and there is none in the mirror
   today (O13). For conversions, no single value model is the object; the levers ledger stands.
2. **A sound schema-keyed view without `wf_ir`?** No. Provenance typing ("produced by an IR
   traversal") is a precondition in disguise; a modelled `validate_ir` postcondition can only be
   consumed through a `requires` on every downstream function, which rule 5 forbids. The only
   rule-compatible version is a *refusal-side* use (never admitting more than today), and that yields
   1 mirror (§4.4).
3. **Is a closed set of hval-polymorphic builtins the whole chain?** No, by O12 and O17: behind
   `tuple`/`join`/key/argument sits the `Tuple[PyVal,…]` return codomain, and behind that the
   consumers of the returned tuple (`_merge_records_best_of_n`'s `occ`). The §4.5 pattern predicts
   another layer; `rk_hval_chain.mlw` measures exactly how many for the best leaf.
4. **A principled Why3 typing of `node["k"]` by `node["type"]`?** One record with 114 `option`
   fields is a sound *shape* (no presence over-claim, projections are field reads, no E-matching) but
   it is a TypedDict with every key `NotRequired`: consumers see `option`, so every read needs a
   `match`, and it still needs the boundary cast that O10 shows does not exist. It replaces the
   `pairs_get` cost with an `option` cost at every consumer. Not cheaper.
5. **Close the `.get` / `[k]` asymmetry?** Yes, but only inside R-gate: under a claim both are
   `#UND` and refused; outside a claim both are ambient. Stand-alone, refusing `.get` on declared
   `Dict[str, Any]` costs 35 sites / 6 mirrors (O13) for no claim closed.

---

## 7. Worth building?

- **A `Dict[str, Any]` value model for conversions: no.** Certify as boundary with the reopening
  test of §4. The report's measurements justify this on their own.
- **R-gate for hashing: yes, if LINK-3 is the "type-safety + frame" reading (§5.4).** It is one
  predicate change in `pycsl.py`'s hashing pass, 0 mirror cost, no WhyML, no axiom, no facade, and it
  closes the family the red team actually found. Its gate is the e1 log-mode re-run (§5.2, item 1);
  its evidence is already favourable (O13, O14). If LINK-3 is the stronger reading, do not build
  anything here: certify the 27 mirrors as a hashing boundary with R-gate's census as the reopening
  measure (the day a mirror function gains a `no_exception` claim over a `#UND` site, that site must
  be refused or derived).

---

## 8. Honest limits of this review

- **No full pycsl proof ran.** Both NORMAL heavy slots were held until 03:10Z; the only proof
  observed is the hand-written spike (S1, S1-z3). O1/O3's "admitted" is an emission fact (no
  obligation at the hash site, `any int`); a Why3 run cannot fail a goal that is not there, so the
  conclusion stands, but the q4/q6 proofs themselves were not observed.
- **The spike is a 9-line function in isolation.** It measures the chain length and the type-level
  acceptance, not the whole-file proof cost in `pycsl.py`'s mirror; S1-z3 is the reminder that
  the latter is the open risk.
- **`q5cost.py` is syntactic.** It detects a claim as a `#@ no_exception` line in the `#@` block
  above the `def` or in its first eight body lines, follows `.get` receivers through ≤2 local
  `Assign` hops, and takes the first same-name function at HEAD. A module-level or inherited claim
  form, if PyCSL had one, would be missed; `docs/pycsl-concrete-syntax-reference.md:149-165` lists
  only the per-function forms.
- **O14 is a grep** for the token `no_exception` in whole files, an over-approximation of "the flagged
  function claims"; it reported 0 for 14 of 16 files, so the over-approximation does not matter.
- **R-gate's semantics depend on §5.4**, which I cannot settle from the code; I have said which
  reading I assumed and why.
- Nothing was committed; `src/` and `bin/` were not edited.
