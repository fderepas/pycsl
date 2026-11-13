# Independent review of `dict-value-model-r4.md` (Gate R) — and a recommendation for a real model of mixed-type values in PyCSL

*Reviewer fr4, 2026-11-13, tree `/home/fabrice/git/pycsl-rp4` (branch `run7-rp4`, report commit `71c47f152`,
`src/` at `198946a61`). Evidence base: the report, the repository (read-only), and my own oracle runs under
`scratchpad/fr4/` (spikes `spk/`, probes `probes/`, outputs `out/`). I did not read the driver's run logs,
plans, executor briefs or other worktrees; cv13's census is cited only as the report cites it. Every number
in §2 was measured by me today on this host (Why3 1.8.2, Alt-Ergo 2.6.3, Z3 4.13.3), each run going
through `heavy.sh`; the report's numbers are quoted as "report".*

---

## 0. Verdict in one paragraph

The report's diagnosis is **sound and, where I could test it, confirmed**: the `rk` chain proves under
Alt-Ergo in 0.23 s and Z3 loops on the two value-fact sub-goals (H5, re-measured); `HAbsent` changes
nothing for Alt-Ergo and is erratic for Z3 (re-measured); the absent key is `HInt pycsl_none` / `HInt 0`
and `None`/`bool` are folded into `HInt` (code read + emission probe); the `pairs_set` certificate gap is
real (Rocq `Phase2f_PyVal.v:220` and Lean `PyVal.lean:165` prepend, the emitter `preamble.py:8281-8287`
replaces-first / appends); the #349 deny-list is unconditional for an `Any`-classed value
(`pycsl.py:10021-10030`); and the existing nested write-back is fail-closed against aliasing (three alias
probes refused). Two findings of mine sharpen the picture: **(i)** the Z3 loop is cured completely by the
"unfold on constructors only" encoding of `pairs_get` (route (e2)): the same witness that Z3 cannot prove in
120 s proves in 0.02 s under both provers, split or not — but that encoding is two WhyML `axiom`s (or an
equivalent certified definitional spec) and so needs a ledger-plane decision before it can be a product;
**(ii)** the functional write-back is unsound without the escape check — a false postcondition about an
aliased nested dict proves in 0.01 s under Z3 — so the store rule of any route is the escape check, not the
`pairs_set` function; **(iii)** Alt-Ergo, the prover that carries the hval goals today, **cannot prove
`"x" <> "y"`** (no string theory in its Why3 driver), so every dict fact that depends on two literal keys
being different is Z3-only — and Z3 is the prover that loops on symbolic association lists; the provers'
weaknesses are complementary, which makes the encoding choice for `pairs_get` a correctness-of-coverage
question, not a speed question; **(iv)** widening `hval` to 9 constructors is not free for Alt-Ergo on the
one proved hval loop function: it loses 7 of 20 "loop variant decrease" goals it proved in ≤ 0.11 s before
(Z3 still proves all 20 in 0.24 s); the cause is the 9-way `match` inside the loop `variant` term, not the
float type or the real theory, and hoisting the iteration length into a `let` before the loop restores
20 / 20 in 0.71 s — a one-line emitter fix that must be part of the widening. I also found that `TypeError` is **not** a VC-able exception at HEAD
(`KNOWN_EXCEPTIONS` = IndexError, KeyError, StopIteration, ValueError, ZeroDivisionError; a
`no_exception TypeError` is rejected by Module 4), which decides how a value model can be "TypeError-faithful":
by static refusal under `\all`, not by an obligation.

**Recommendation (§3):** build **one frozen, certified value type** (route (a)'s constructor set, no
`HAbsent`, no `HSet`) **in place of `hval`**, with faithful reads, narrowing propagation, truthiness,
cross-type equality / key canonicalisation, a structural hashability predicate used as a *derivation* by the
#349 pass, insertion-ordered dict construction unified with the (then certified) replace-first/append
`pairs_set`, and **the existing fail-closed value-semantics store rule unchanged**; keep the recursive
`pairs_get` as the solver-facing definition (Alt-Ergo carries it; the pipeline is best-of-N) and hold route
(e2) in reserve with its measured numbers; run the make-or-break spike on `functions.py` **before** touching
the 21-file mover set. Reject (c); defer (f) to a separate, census-gated project (my heap probe is its seed);
use (d) opportunistically. Expected yield in ~85 h with 2 slots: **2-4 whole-chain conversions**, 389 →
385-387 — the window buys the certified foundation, not a count. If a count is what the user wants from this
window, this track should not be run.

---

## 1. The report's claims, one by one

| # | claim (report §) | verdict | evidence |
|---|---|---|---|
| H1 | 389 `\trusted` markers | **confirmed** | `grep -rhF '#@ \trusted' src/self-annotate/src --include=*.py \| wc -l` → 389 |
| H5 | `rk_hval_chain.mlw`: Alt-Ergo all Valid, witness 0.13 s; Z3 witness Timeout 20 s unsplit, both read sub-goals Timeout 30 s split | **confirmed** | §2 run R1: AE witness Valid 0.23 s (2068 steps); Z3 unsplit Timeout (20 s, 25.5 M steps); split: `gn1`, `gn2` Timeout 30 s (48.0 M / 33.6 M steps), `k1 <> k2` and post Valid |
| H5' | `HAbsent` variant: AE unchanged; Z3 Valid unsplit (0.10 s) but Timeout split | **confirmed** | R2: AE 0.25 s; Z3 unsplit Valid 0.21 s (327 k steps); split: two Timeouts (26.1 M / 25.7 M) |
| H6 | `monomorphize.py` emitted: 237 goals, AE 235 / Z3 231 Valid, union 237/237; whole-file L2 SUCCESS 632 s | **confirmed from the report's own outputs; the AE/Z3 per-prover runs re-measured (R6, control)** | `python3 union.py out/mono.ae.out out/mono.z3.out` → `goals=237 valid-by-any=237 none=0`; `grep -c Valid` → 235 / 231; `wholefile.out`: "Verification SUCCESS!"; R6 control: see §2 |
| H7 | no absent marker; `.get` absent → `HInt pycsl_none`; `d[k]` absent → `HInt 0`; `None`/`bool` → `HInt`; `v is None` on an hval read is a Why3 type error; `isinstance(v, int)` → `(any bool)` | **confirmed** | `expressions.py:1384-1390` (`_dv_missing_default` → `"(HInt 0)"` for `hval`), `:1526` (`_pyval_wrap` falls to `HInt (coerce_to_int ..)`); probe P3 `narrow_str`: `HInt _ -> (any bool)` arm and a `not (_r521_v = pycsl_none)` assert with `_r521_v : hval` → L3-tc failure "has type hval, but is expected to have type string" (`p3_eq_truth.mlw:91`) |
| §1.4 | `pairs_set` cert gap: certificates prepend, emitter replaces-first / appends | **confirmed, and sharper** | Rocq `Phase2f_PyVal.v:220` `Definition pairs_set ... := PCons k v p`, comment at `:208-211` says it models `_build_dict_literal_map`'s *construction*; Lean `PyVal.lean:165` `pairsSet ... := .PCons k v p`; emitted `preamble.py:8281-8287` replace-first / append, "proven ... in `r2c_writeback.mlw`" (a spike, not a certificate). The Lean names are `pairsGet` / `pairsSet` (the report writes `pairs_get` / `pairs_set` for both; cosmetic) |
| §1.4 | both certificates `Admitted` / `sorry`-free | **confirmed** | `grep -c 'Admitted\|sorry'`: Rocq 1 hit, a comment ("Nothing here is Admitted", `:51`); Lean 0 |
| §2.1 row 9 | `PyVal` is not a tuple slot type; `bool` slot → `int` | **confirmed** | `Module5_IREmitter.py:3830` `_M5_TUPLE_SLOT_TAGS = {"int": "int", "bool": "int", "str": "str", "float": "real"}` |
| §2.4 / H4 | #349 deny-list unconditional for a value of unknown class ("may be a list / dict / set"), refusal under a TypeError claim only for `#UND` | **confirmed** | `pycsl.py:10021-10030` (`#UNK` → `_u349` deny-list unless class known hashable); claim test `:9988-9993` (`no_exception_all` or `TypeError`/`Exception`/`BaseException` named); `annotations.md` §7.131 |
| §2.3 row 250 | an hval read used as an IfExp test lowers as a *string* truth test | **context-specific, not general** | probe P3 `truth_ifexp` (`1 if v else 0`, `v = d.get("k")`): lowers to `(if (hval_truthy v) then 1 else 0)` — correct. The report's row-250 clash (`str_eq_op <hval> ""`) comes from a context where the operand was inferred as `str` (`expr.get("args")` in `_handle_sum_call`); the general IfExp path is right |
| §3.2 | 0 / 5 TC-OK; refusals #487 / #325 / #349 | **unverified** (`summary.txt` read, probes not re-run; the refusal texts match the routes' messages) | `scratchpad/rp4/reopen/summary.txt` |
| §3.3 | cv13 interim numbers (1 of 43 closes; O11+O12 largest) | **unverified** (cited only) | — |
| §7 | 21 of 53 mirror emissions carry the hval theory | **consistent, not re-measured** | 7 mirror files use `PyVal` (`errors`, `Module5_IREmitter`, `monomorphize`, `expressions`, `functions`, `stmt_control_flow`, `pycsl`), 14 import from `errors` (my grep); the sweep itself lives under a path I did not open |
| §7 (a) | "an `HAbsent` constructor would model something Python does not have" | **agree** | `.get` returns `None`; the carrier-level `option` already distinguishes absent from a stored `None` (`Map.get = None` vs `Some HNone`) |
| §7 (f) | by-reference dicts make aliasing free | **confirmed on the probe, with a cost** | R4: heap store, frame goal Valid 0.00-0.03 s under both provers; the *true* read-back needs an induction lemma for the replace-first `pairs_set` (R4: Timeout without it; R7 with `let rec lemma`: see §2) |
| §8 Q4 | `hstr_of`'s opaque arm under a claim is unaudited | **and `TypeError` is not a VC class at HEAD** | `exception_model.py:122` lists TypeError only in the class table; `KNOWN_EXCEPTIONS` = {IndexError, KeyError, StopIteration, ValueError, ZeroDivisionError} (probe P4/P5: "no_exception names unknown exception 'TypeError'") |

The report's §8.6 process deviation (three extra tiny why3 jobs for a window) is disclosed; the replicate
outputs agree with the battery. My own runs stayed at ≤ 2 heavy jobs (type-only checks are QUICK and
seconds-long).

---

## 2. Oracle runs (all mine, today)

Commands are in `scratchpad/fr4/spk/battery{,2,3,4}.sh` and `scratchpad/fr4/probes/emit.sh`; raw outputs
under `scratchpad/fr4/out/` (`*.out`, `battery*.log` with wall time and `oom_kill` = 0 at every step) and
`scratchpad/fr4/probes/*.emit.out` / `*.mlw`. Spike files are generated from r3's `rk_hval_chain.mlw` by
`spk/gen.py` so that the **same witness** (`key_reads_goal_name`: eight `pairs_get` reads of a record whose
`hpairs` has a symbolic tail `p`, then `gn_i = HStr g_i`, `k1 <> k2`) is measured under each encoding.

| run | file | what | Alt-Ergo | Z3 | reading |
|---|---|---|---|---|---|
| R1 | `rp4/rk/rk_hval_chain.mlw` (verbatim) | r3 chain | 20 s unsplit: all Valid, witness **0.23 s**; split 30 s: all Valid | unsplit **Timeout 20 s** (25.5 M steps); split: `gn1`, `gn2` **Timeout 30 s**, `k1<>k2` 0.01 s, post Valid | H5 confirmed |
| R2 | `rp4/rk/rk_habsent.mlw` | + `HAbsent` | witness Valid 0.25 s | unsplit **Valid 0.21 s**; split: `gn1`, `gn2` **Timeout** | H5' confirmed: erratic |
| R3a | `fr4/spk/fr4_rich.mlw` | `hval` + `HNone \| HBool bool \| HFloat real \| HTuple hval_list`, absent default `HNone`, arms added to `hval_truthy`, `hval_tuple` and every `or`-default match | witness **Valid 0.25 s** (2159 steps), split 1.3 s total | unsplit Timeout 20 s (19.6 M); split: `gn1`, `gn2` Timeout, rest Valid | a 9-constructor set costs Alt-Ergo nothing on this witness; Z3's behaviour is unchanged (the loop is the symbolic tail, not the width) |
| R3b | `fr4/spk/fr4_unfold.mlw` | route (e2): `pairs_get` as an uninterpreted `function` with the two defining equations as **constructor-triggered axioms** (`[pairs_get (PCons k' v t) k]`), programs ghost | all Valid, witness 0.27 s | **all Valid: witness 0.02 s (46 k steps) unsplit; split `gn1`, `gn2` 0.02 s each** | **the Z3 loop disappears entirely**: a symbolic `pairs_get p k` can fire no equation. Caveat: two `axiom` declarations — see §3.4 |
| R3c | `fr4/spk/fr4_mapcar.mlw` | nested dict carrier = `map string (option hval)` (Why3 1.8.2 **accepts** the recursive occurrence through `map`, and through `string -> option hval`: `fr4_arrow.mlw` type-checks) | witness **Timeout** (both modes) | witness **Timeout** | **unprovable by construction**, not an E-matching datum: a Why3 map has no structure, so the `or`-default's truthiness test is an uninterpreted `hmap_nonempty` and the record may be "empty". R5 re-runs it with a specified truthiness |
| R4 | `fr4/spk/fr4_alias.mlw` | aliasing probe (§3.3): Python `a = d["x"]; d["y"] = a; a["k"] = 1` | §1 value-semantics false post: **Timeout**; §2 heap true post: Timeout; heap false post: Timeout (good); §3 heap frame: **Valid 0.03 s** | §1 value-semantics **FALSE postcondition `d["y"]` has no `"k"`: Valid 0.01 s (11 k steps)**; heap true post: Timeout; heap false: Timeout (good); frame **Valid** | the functional write-back **proves a false fact** about an aliased nested dict; the by-reference store does not, and its frame is free. Alt-Ergo's §1 timeout is a prover difference (see R5b), not soundness |
| R5a | `fr4/spk/fr4_mapcar2.mlw` | R3c with `hmap_nonempty` specified (`result <-> exists k. m k <> None`, a task hypothesis like `hpairs_key_eq`'s) | **all Valid**: witness 0.57 s unsplit (8492 steps), 0.21 s per read sub-goal split | **all Valid**: witness 0.03 s unsplit (55 k steps), ≤ 0.02 s per sub-goal split | a Why3-`map` carrier for nested dicts has **no Z3 loop** (array theory, no recursion) — but it needs a *specified* `val` for truthiness and has no structural `len` / iteration order (the reason R3 chose the assoc list); it is the second cure for Z3 after (e2), with the same ledger question |
| R5b | `fr4/spk/fr4_strlit.mlw` | `"x" <> "y"`; `Map.get (Map.set d "x" v) "y" = Map.get d "y"`; `Map.get (Map.set d "x" v) "x" = v` | `lit_distinct` **Timeout 20 s**; `rw_other` **Timeout**; `rw_same` Valid 0.03 s | all three **Valid ≤ 0.01 s** | **Alt-Ergo cannot separate two string literals** (its Why3 driver has no string theory; the literals are abstract constants). Every dict fact that needs "this key is not that key" is **Z3-only** at HEAD; this is why R4 §1 timed out under Alt-Ergo. Z3 is the prover that loops on symbolic association lists (R1): the two provers' weaknesses are complementary, not redundant |
| R6 | `fr4/spk/mono_rich.mlw` vs `rp4/em/mono.mlw` (control, same host, same hour) | the emitted 973-line `monomorphize.py` file with the **9-constructor set in place of `hval`** (9 absent defaults → `HNone`, 4 arms in `hval_truthy`), pipeline call `-a split_vc`, 30 s, per prover | control: 235 / 237 Valid, Valid-sum 19.5 s, `_collect_generic_decls` 20 / 20 in 1.32 s (max 0.11 s). **Rich: 228 / 237, Valid-sum 25.9 s; `_collect_generic_decls` 13 / 20 — 7 "loop variant decrease" sub-goals Timeout 30 s**, the 13 Valid ones 7.15 s (×5) | control: 231 / 237 (6 Timeouts, all `pyval`/`wf_ir`), Valid-sum 2.0 s (report) ; rich: **235 / 237**, `_collect_generic_decls` 20 / 20 in 0.24 s | union still 237 / 237, but **width is not free for Alt-Ergo**: on the one hval loop function it loses 7 goals it proved in ≤ 0.11 s. The lost goals are the variant terms `(match hv with HArr l -> hval_list_len l \| _ -> hval_iter_len_other hv end) - !i`: a 9-way case split per unfolding. R8 isolates the cause (reals? width? the inline match?) |
| R8 | `fr4/spk/mono_rich_nofloat.mlw`, `mono_rich_absfloat.mlw`, `mono_rich_hoist.mlw` | R6's file with (a) no `HFloat` (8 constructors, no real theory), (b) `HFloat pyfloat` over an abstract type, (c) the 9 constructors but the loop's iteration length **hoisted** into a `let` before the loop so the variant is `len - !i` | (a) **228 / 237, the same 7 loop-variant Timeouts**, `_collect_generic_decls` 13 / 20 (6.2 s) — so it is **not the real theory**; (b) 228 / 237, the same 7 Timeouts, 13 / 20 (6.45 s) — not the float type either; (c) **235 / 237 (= control), `_collect_generic_decls` 20 / 20 in 0.71 s (max 0.06 s), Valid-sum 17.6 s (< control's 19.5 s), wall 78 s vs 300 s** | (a) 231 / 237 (same 6 `pyval` Timeouts as control), `_collect_generic_decls` 20 / 20, Valid-sum 2.5 s | **the cost is the 9-way inline `match` inside the loop's `variant` term (re-split at every unfolding), and hoisting the iteration length into a `let` before the loop removes it entirely.** A one-line emitter change (`stmt_control_flow.py`'s hval `for` template) makes the widening free on this file for Alt-Ergo |
| R7 | `fr4/spk/fr4_alias2.mlw` | R4 + `let rec lemma pairs_set_read_same / read_other` (induction, no axiom) for the emitted replace-first `pairs_set` | both lemmas **Valid** (0.17 s / 0.27 s, by structural induction); heap true post **Valid 0.03 s**; heap false post Timeout (correct); value-semantics false post Timeout (the R5b literal issue) | lemmas Valid ≤ 0.01 s; value-semantics **false post Valid 0.01 s** (again); heap true post **Valid 0.01 s**; heap false post **Timeout** (correct); frame Valid | the emitted `pairs_set` needs its read-back lemmas *in the theory* (as `let rec lemma`, proved, not assumed) for any store fact to be provable; with them the by-reference store proves the true fact, refuses the false one, and frames for free |
| R9 | `fr4/spk/fr4_twokey.mlw` | the **emitted** hval theory, verbatim: `pairs_get (PCons "x" 1 (PCons "y" 2 PNil)) "y" = Some 2`, `... "x" = Some 1`, `pairs_get (PCons "x" 1 PNil) "z" = None` | first key Valid 0.03 s; **second key Timeout 20 s; absent key Timeout 20 s** | all Valid (0.98 s / 0.09 s / 0.71 s) | with today's theory Alt-Ergo can only read the *first* binding of a literal dict; every read that must skip a key, and every absent-key fact, is Z3-only (R5b's consequence inside the actual carrier) |
| P1a/b/c | `probes/p1_alias_nested.py`, `p1b_alias_top.py`, `p1c_alias_param.py` | emission (`--no-proof --keep-mlw`) of three alias programs with a FALSE `ensures \result == 0` | — | — | **all three REFUSED before emission**: nested local tree with a non-literal container on the path (r2c R3); `b = a` on a mutated top-level dict (route #59, "lowers to a COPY"); a nested store through a **parameter** (r2c R1, "needs the call-site kill rule"). The store rule is fail-closed today |
| P2 | `probes/p2_keyerror.py` | `d["k"]` on `Dict[str, PyVal]`, with and without `no_exception KeyError` | — | — | claimed: `assert { Map.get d "k" <> None }` then the read (`p2_keyerror.mlw:77`); unclaimed: `None -> (HInt 0)` junk continuation (`:84`) |
| P3 | `probes/p3_eq_truth.py` | `v == 1`, `1 if v else 0`, `isinstance(v, str)` then `return v` | — | — | `==` → `match v with HInt i -> i = 1 \| _ -> false` (right only because `bool` is folded into `HInt`; no float); IfExp → `hval_truthy v` (right); narrowing not propagated → L3-tc failure (H7) |
| P4/P5 | `probes/p4_hash.py`, `p5_typeerror.py` | hashing a PyVal read / `v + "x"` under `no_exception TypeError` and `\all` | — | — | `no_exception TypeError` **rejected by Module 4** ("names unknown exception 'TypeError'"). Under `\all`: `s.add(v)` **REFUSED** by the R-gate ("`v` is HASHED ... its class cannot be derived ... claims `no_exception` covering TypeError", `p4_hash.emit.out`); the un-claimed twin (`p4b_hash_unclaimed.py`): **admitted** by the ir-semantic passes (the ambient rule), then **fails L3 type-check** — `map_update_some !s v 0` puts an `hval` into a `map int` set (`p4b_hash_unclaimed.mlw:82`): there is no hval-keyed collection today, so hashing a tagged value is fail-closed by typing, not modelled. `v + "x"` under `\all` and un-claimed: **no route fires** — the emission is `str_concat v <hash>` with `v : hval` and fails L3 type-check (`p5_typeerror.mlw:82`): fail-closed by a type accident, not by a rule (report Q4 confirmed: the projection sites are unregistered) |

---

## 3. Recommendation

### 3.1 The route: a frozen certified value type, reads + laws + derivations, the existing store rule — in place of `hval`

Build route **(a)** with these amendments, as **one** change to the shared theory:

1. **Freeze the constructor set first** (§3.3.1) and certify it (Rocq + Lean) **before** any emitter
   template or stub is touched. Reason: the theory text is shared by 21 mirror emissions (report §7, my
   count is consistent); every constructor added later re-pays the ~35-40 h re-proof. One widening, once.
2. **In place of `hval`, not a second gated theory.** The report's Q7: a gated second theory keeps the 21
   files byte-identical *today*, but every BOUND stub's home is one of the big hval files anyway (`functions`
   6, `expressions` 5, `Module5` 4, `preamble` 4, `Module6_WhyMLTranspiler` 4), so their re-proof comes with
   the first conversion batch regardless; and two coexisting mixed-value theories add a bridge family (cv13's
   O16 already lists 5 stubs blocked on hval↔pyval / hval↔emit_ir bridges) that the certificate must then
   also cover. The in-place widening is measured cheap (R3a, R6) and is paid once.
3. **Reads faithful, narrowing propagated, truthiness and `or`-defaults structural, `tuple` / `join` / `len`
   / `in` / iteration over the value** — the report's list, which my probes confirm is where the chains stop
   (P3 `narrow_str`). **Iteration lowers with a hoisted length** (`let n = hval_iter_len hv in while !i < n
   ... variant { n - !i }`): R8 shows this is what keeps the widened type free for Alt-Ergo.
4. **Equality and keys by law** (§3.3.3): `hval_eq` with Python's cross-type numeric equality, `hval_canon`
   at every key position; **hashability by derivation** (§3.3.4): a structural `hval_hashable` that the #349
   pass may use, and the deny-list made claim-conditional for a *tagged* value (it stays unconditional for a
   value statically known to be a list / dict / set).
5. **Dict construction in insertion order through the certified `pairs_set`** (§3.3.5): closes the
   §1.4 gap and gives iteration an order.
6. **Store rule unchanged** (§3.3.6): value semantics behind the fail-closed r2c escape check (R1-R4 in
   `statements.py:3716-3745`). Parameter mutation (family M, 17 stubs) **stays trusted in this window**.
7. **Solver-facing `pairs_get`: the recursive definition for the mirror's type-safety goals now, and the
   constructor-triggered equations (route (e2)) adopted as soon as the ledger-plane decision allows.** The
   reasoning changed during this review: the mirror's `ensures True` shape is served by Alt-Ergo with the
   recursive definition (R1-R3a, report §5), but Alt-Ergo cannot separate string literals (R5b), so every
   *value* fact about a dict with two or more literal keys — the non-vacuity witnesses this track must
   produce, and any future value-faithful contract — is Z3-only, and Z3 loops on the recursive definition
   (R1) and does not on (e2) (R3b: 0.02 s) or on a map carrier (R5a: 0.03 s). (e2) is therefore the
   precondition for Z3 to be the value-fact prover, not a speed option. Its product form is two WhyML
   `axiom`s (Why3 forbids a `val function` whose `ensures` mentions itself) realised by the certified
   `pairs_get`; whether the assumed-facts plane may admit a *certified definitional* axiom pair is user
   decision 2(d) (§3.7). Until then: recursive definition, best-of-N, and the §3.5 cap on Z3 timeouts.
8. **Make-or-break spike on `functions.py` before step 1 lands in `src/`** (§3.5).

**Rejected / deferred:**
- **(c) int-erasure + typed views: reject**, as the report does. Routes #252 / #325 exist because this was a
  false-proof channel; an opaque conversion of an opaque int is an approximation of a value (rule 1), and on
  carrier 2 (`f_get_1 <hash>`) it is input-blind.
- **(f) by-reference heap: defer to its own census-gated project.** My probe (R4/R7) shows the model works
  as expected (false fact unprovable, frame free, true fact provable with an induction lemma), and the census
  says mutation is where the population is — but (f) changes the WhyML type of every dict-typed parameter,
  field and local in adopting files, moves every tight `assigns` frame onto heap regions, and asks
  `check-trusted-frame-honesty` / `check-assigns-writes-survival` to understand regions. It cannot be
  certified, built and planed in 85 h alongside the value type, and building the value type first is a
  prerequisite for it anyway (the heap's object type is the frozen value type). Note also that Why3's own
  `ref` discipline already assumes two dict *parameters* are distinct objects (route #316's fence exists for
  the related writes question); (f) is where that assumption would be discharged honestly.
- **(d) live refactors: opportunistic only** (s003 / s006 flags class), never as the model.
- **(b) schema-keyed views: not as a separate route** — fold its one load-bearing idea (a statically chosen
  projection whose *justification* is a key→type table from the mirror's TypedDict annotations) into the
  hashability / narrowing derivation of 4; a *modelled cast* to a TypedDict record is a new value shape with
  its own certificate and is out of this window.
- **(e1) constant-folding literal `pairs_get`**: an optimisation with no soundness content; do it only if the
  spike shows literal-key chains dominating.
- **(a) with `HAbsent`**: reject the constructor (Python has no such value; the carrier's `option` already
  distinguishes absent from stored `None`; R2 shows it buys nothing).

### 3.2 Why not "value model is enough" and why not "mutation now"

cv13's interim claim that mutation and aliasing are the largest group is consistent with everything I
measured: P1c shows the one store rule PyCSL has refuses a parameter root by design, and R4 shows *why*: the
functional write-back proves a false fact the moment two names share an object. Under the fixed contract
shape (`requires True`, rule 5) a non-aliasing precondition is not available, so parameter mutation is
honest only under (f). Hence the honest boundary for this window is **"reads, laws and derivations
convert; mutation of a parameter stays trusted"**, said up front rather than discovered at hour 60.

### 3.3 Design decisions

#### 3.3.1 Constructor set (frozen, certified first)

```
type hval = HNone | HBool bool | HInt int | HFloat real | HStr string
          | HTuple hval_list | HArr hval_list | HMap hpairs | HNode hval
with hval_list = HNil | HCons hval hval_list
with hpairs    = PNil | PCons string hval hpairs
```
- `HNone`: the faithful value of a one-argument `.get` on an absent key and of a stored `None`; `v is None`
  becomes `match v with HNone -> true | _ -> false` (today a type error, H7).
- `HBool`: separate from `HInt` so `isinstance(v, bool)` / `isinstance(v, int)` are decidable (today
  `(any bool)`), with the numeric laws of §3.3.3 restoring `True == 1`.
- `HFloat real`: the IR / JSON payloads carry floats (cv13 O9, s027, s329); no NaN in Why3 reals — a NaN
  reaching a comparison is a refusal site, not a model.
- `HTuple`: distinct from `HArr` because hashability and `==` differ (`(1,) != [1]`; a tuple of hashables is
  hashable, a list never is) — H4's codomain needs exactly this tag.
- **Not included:** `HAbsent` (above); `HSet` (unordered: iteration has no faithful order and set equality is
  extensional — model later or refuse; 2 stubs: s001, s279); `HBytes`, `HDate`, class instances (refuse).
- **Frozen** means: the Rocq and Lean inductives, `size`/`size_pos`, injectivity / disequality for every pair,
  and the laws of §3.3.3-3.3.5 land in one commit with the emitted theory text; adding a constructor later is
  a new wall cycle with the 21-file re-proof as its cost.

#### 3.3.2 Operations and exception behaviour

| Python | lowering | KeyError / TypeError |
|---|---|---|
| `d.get(k)` | top-level `match Map.get d k with Some v -> v \| None -> HNone`; nested `match pairs_get p k with Some v -> v \| None -> HNone` | none (faithful) |
| `d.get(k, x)` | same with `x` wrapped | none |
| `d[k]` | under a claim covering KeyError: `assert { ... <> None }` before the read (exists today for the top-level map, P2; **must be added for nested `pairs_get` reads**, which today take the `(HInt 0)` default silently under a claim — a gap to close); outside a claim: the continuation is dead in Python — use `any hval` rather than the specific junk `(HInt 0)` (both are sound over-approximations; `any` has no accidental value) | KeyError: obligation under a claim, ambient otherwise |
| `k in d` | top-level `Map.get d k <> None`; nested `pairs_get p k <> None` | TypeError on an unhashable `k`: §3.3.4 |
| `isinstance(v, T)` | a tag `match`, **and the narrowed projection is substituted in the guarded region** (`hstr_of v`, `hint_of v`, `match v with HMap p -> ...`) — the missing link in P3 `narrow_str`, 034a, 250a | none |
| `if v` / `v or x` / IfExp test | `hval_truthy` (structural, all 9 tags) | none |
| `v == w`, `v != w` | `hval_eq` (§3.3.3) | none (builtin `__eq__` does not raise) |
| `len(v)` | `match v with HStr s -> String.length s \| HArr l \| HTuple l -> hval_list_len l \| HMap p -> hpairs_len p \| _ -> <TypeError site>` | TypeError site |
| `v + "x"`, `v.split()`, `str` slots, f-strings | `hstr_of v` **only where narrowing established `HStr`**; otherwise a TypeError site | TypeError site |
| `tuple(v)`, `", ".join(v)`, `sorted(v)`, `for x in v` | hval-polymorphic over `HArr` / `HTuple` / `HStr` / `HMap` keys; a non-iterable tag is a TypeError site; loop variant `hval_list_len l - i` | TypeError site |
| `d[k] = v`, `d.setdefault`, `.pop`, `.update`, nested `.append` | r2c functional write-back under R1-R4 **only**; everything else refused (P1a/b/c) | KeyError for `.pop` under a claim |

**TypeError sites.** At HEAD TypeError is not in `KNOWN_EXCEPTIONS`, so it cannot be a VC: a site is
either *statically refused* when the function claims `\all` (the §7.131 mechanism) or *ambient* (sound by
the P1 argument: an un-claimed function's `ensures` is only about normal returns). The decision for this
window: **register every projection site above with the §7.131 pass** (so `\all` functions with an
un-narrowed `hstr_of` are refused rather than proved on the opaque string — the report's Q4, which I
confirm is unaudited today: `hval_opaque_str` has 4 emitter sites in `expressions.py` and no R349-style
registration), and leave the ambient rule for the mirror's unclaimed contract shape. Promoting TypeError to
a VC class (trigger `is_HStr v` etc.) is the right long-term move but is an exception-model change with its
own corpus impact; not in this window.

#### 3.3.3 Equality laws (incl. Python cross-type equality)

`hval_eq : hval -> hval -> bool`, structural, total, **certified** against the table:
- numeric tower: `HBool b` ≡ `HInt (if b then 1 else 0)`; `HInt i == HFloat f` iff `from_int i = f`;
  `HBool`/`HInt`/`HFloat` never equal `HStr`/`HNone`/containers (`True == 1`, `1 == 1.0`, `"1" != 1`,
  `None != 0`, `None != False`);
- `HNone == HNone` only; `HStr` by string equality; `HArr`/`HTuple` elementwise **within** the same tag
  (`(1,) != [1]`); `HMap p == HMap q` iff same key set and `hval_eq` on each value (order-independent) — a
  quantified definition; emit it as a `let rec` over `p` with a `pairs_get` on `q` and accept the E-matching
  cost only where `==` between dicts occurs (rare in the emitter; a `val` opaque fallback is sound);
- `HNode` / `HNode`: structural over `emit_ir`'s own equality.
Today's `v == 1` → `match v with HInt i -> i = 1 | _ -> false` (P3) is right only because `bool` is folded
into `HInt`; with `HBool` it must become `hval_eq v (HInt 1)`.

**Key canonicalisation.** Python merges `d[1]`, `d[True]`, `d[1.0]`. A `map hval _` keyed on raw tags would
count them as three keys — a false `len`. Every key position takes `hval_canon k` (`HBool b -> HInt ..`,
integral `HFloat` → `HInt`), and the certificate proves `eq_canon_coherent : hashable a -> hashable b ->
(hval_eq a b <-> hval_canon a = hval_canon b)`.

#### 3.3.4 Hashing / hashability (the #349 finding)

`hval_hashable : hval -> bool` = `HNone | HBool | HInt | HFloat | HStr -> true | HTuple l -> all hashable l
| HArr | HMap | HNode -> false`. The #349 pass treats a `PyVal`-typed hashed value as **derivable-hashable**
when (i) a dominating `isinstance` narrows it to a scalar tag or a tuple of scalars, or (ii) its key→type
schema (the mirror's TypedDict annotation for that record kind; `ir_schema.py` for IR nodes) types the slot
as a scalar — a derivation, never an assumption: a wrong schema sends the value to a refusal, not to a proof.
Otherwise: **under `\all` refused** (as `#UND` is), **outside a claim admitted** (ambient TypeError). That
is a policy change from today's unconditional deny for `#UNK` values and it is the only thing that lets H4's
`best[key]` in `_merge_records_best_of_n` (unclaimed, `pycsl.py:788-792`) admit a `Tuple[PyVal, ...]`
codomain. The WhyML map is keyed on `hval_canon k`.

#### 3.3.5 Iteration order and dict construction

Python dicts iterate in insertion order. Today a dict literal is built by **prepending** (`_pyval_wrap`,
`expressions.py:1511-1515`, "prepend order is observationally irrelevant") while the write-back `pairs_set`
**appends** new keys: two orders in one carrier, and the certificate proves read-back for the prepend only.
Decision: build literals as `pairs_set (... (pairs_set PNil k1 v1) ...) kn vn` with the emitted
replace-first/append `pairs_set`; iteration = list order = insertion order with last-wins duplicates
removed; certify **that** `pairs_set` (`read_same_key`, `read_other_key` by induction — R7 is the WhyML
version — plus `nodup` preservation and `keys_in_order`). A symbolic parameter `hpairs` under
`requires True` may carry duplicates no Python dict has; reads take the first (consistent), iteration visits
junk: a harmless over-approximation of the input space. Dict length is `hpairs_len` on a `nodup` list.

#### 3.3.6 Mutation / aliasing rule

**Value semantics behind the fail-closed escape check, unchanged, plus the KeyError obligation for nested
subscripts.** Evidence: R4 §1 (a false fact proves in 0.01 s without the check) and P1a/b/c (the check
refuses the three alias shapes). The rule's contract: a store is lowered only when the written tree is a
non-parameter local built from literals, never bound to another name, passed or iterated, with literal keys
below the first and only literal-produced containers on the path (R1-R4). Any relaxation (a parameter root,
a stored non-literal container) is route (f)'s problem and is refused until (f) exists.

### 3.4 Coupling to certificates (Rocq + Lean), per type and per operation

| item | Rocq (`Phase2f_PyVal.v` successor, or a `Phase2g` side-car) | Lean (`PyVal.lean` successor) | status |
|---|---|---|---|
| the 9-constructor mutual inductive | definition; `size`, `size_pos`; injectivity and pairwise disequality (36 pairs) | same (`#print axioms` ⊆ allowlist) | new; mechanical |
| `pairs_get` | as today (`string_dec`) | `pairsGet` | exists |
| `pairs_set` replace-first/append | **replace the prepend**; `read_same_key`, `read_other_key`, `nodup_preserved`, `len_set` | same | closes the §1.4 gap |
| literal construction = fold of `pairs_set` | `build_fold_read_back` (last-wins), `build_nodup` | same | new |
| `hval_truthy` | the 9-arm table vs Python truthiness (`None`, `False`, `0`, `0.0`, `""`, `()`, `[]`, `{}` falsy) | same | new |
| `hval_eq`, `hval_canon`, `hval_hashable` | the cross-type table (`True == 1`, `1 == 1.0`, `"1" != 1`, `None != 0`, `(1,) != [1]`); `eq_refl` on non-float, `eq_sym`; `eq_canon_coherent` | same | new; the one with real content |
| `hval_list_len`, `hval_list_nth`, `hval_tuple`, `hval_len` | `nth_in_range`, `len_nonneg`, `tuple_preserves_elems` | same | new; small |
| `hstr_of`, `hint_of` projections | `proj_on_tag` (`hstr_of (HStr s) = s`), totality | same | new; trivial |
| `hval_opaque_str`, `hval_values_get/len`, `hval_keys_get`, `hval_as_map`, `pycsl_none_map` | uninterpreted `val`s: **not** required by the rule; list them in the ledger note as law-free | — | unchanged |
| route (e2) equations, if ever adopted | `pairs_get_nil`, `pairs_get_cons` proved of the certified `pairs_get` (so the WhyML `axiom` pair is a *realised* definitional spec) | same | only with the ledger-plane decision |

Every lemma above is first-order structural; I estimate 1.5-2.5 days for both assistants, and the
`Print Assumptions` / `#print axioms` check must stay within `proof_axiom_allowlist.py` (3-axiom ledger
untouched).

### 3.5 E-matching / proof-cost risk and the make-or-break spike

**What is measured.** Width of the constructor set: nothing on the witness (R3a: AE 0.25 s vs 0.23 s);
on the 237-goal `monomorphize.py` file (R6) Alt-Ergo **loses 7 of the 20 hval-loop goals** (all "loop
variant decrease", 30 s each) and spends ×5 on the rest, Z3 is unaffected (20 / 20, 0.24 s), union stays
237 / 237; R8 shows the cause is the 9-way `match` in the `variant` term, not reals, and that hoisting the
loop length (`let n = <len of the iterable> in ... variant { n - !i }`) restores the control numbers
exactly (20 / 20, 0.71 s, Valid-sum 17.6 s vs 19.5 s control). Depth / symbolic tails: Z3 loops on value
facts over a symbolic `hpairs` (R1, R2, R3a; 20-120 s), Alt-Ergo never did (≤ 0.27 s); the loop is gone
under the constructor-triggered encoding (R3b: 0.02 s) and under a map carrier (R5a: 0.03 s). Literal
keys: Alt-Ergo cannot separate two string literals (R5b), so multi-key value facts are Z3-only. The mirror's
type-safety goals do not ask for value facts (report §5: hval function 0.19 s on Z3). Big dispatch-heavy
files are **unmeasured** (report §8.1; the r3 history of `stmt_control_flow.py` ~2400 s after one hval
field is the only datum). Lesson of R6/R8 for the emitter: **every `match` over the widened type that sits
inside a `variant`, an `invariant` or a loop condition must be hoisted to a `let`-bound constant**; the
widening is otherwise paid at every unfolding.

**Make-or-break spike (before any `src/` edit).** Take the base emission of
`src/self-annotate/src/module6_whyml/functions.py` (home of 6 BOUND stubs, last whole-file ~1.6 h, carries
the hval theory), substitute the frozen theory text by the `mono_rich.mlw` recipe (type decl, `hval_truthy`
arms, absent defaults → `HNone`, new arms in every emitted `match` over `hval`), and run the pipeline's own
per-prover call (`why3 prove -a split_vc -P <p> --timelimit 30 --json`) for Alt-Ergo and Z3 on both the
pristine and the substituted file (4 runs, ≤ 2 at a time, ~2 × 1.6 h of slot time).
- **PASS**: union Valid = 100 % of goals on the substituted file; Alt-Ergo sum-of-Valid ≤ 1.5 × pristine;
  new Z3 timeouts ≤ 10 (= ≤ 5 min of wall); no goal that was Valid under both provers becomes Valid under
  neither.
- **REFUTE** (exit): any previously-Valid goal lost for both provers, or Alt-Ergo sum > 2 ×, or the file's
  estimated whole-file time (sum of per-goal walls) > 2 × 1.6 h. On refutation: do not widen `hval`; fall back
  to (e2) for `pairs_get` only after the ledger-plane decision, or stop the track.
- The cheaper gate already ran: R6/R8 on `monomorphize.py` — without the hoist the widening would have
  **refuted** on the Alt-Ergo criterion (7 lost goals, Valid-sum ×1.3 plus 210 s of timeouts); with the
  hoist it **passes** (235 / 237 = control, Valid-sum 0.9 × control). The `functions.py` spike must be run
  with the hoisted template, and the criterion applies per prover: Alt-Ergo must not lose a goal it proved
  on the pristine file *unless Z3 proves it in ≤ 1 s*.

### 3.6 Realistic yield, ~85 h wall, 2 proof slots

Count = stubs whose **whole chain** closes (L1 + L2 whole-file + L3 inert), not links moved.

| tier | work | hours (build / proof) | conversions |
|---|---|---|---|
| T0 spike | §3.5 on `functions.py` + `monomorphize.py` | 2 / 4 (slot) | 0 |
| T1 foundation | frozen theory + certificates (Rocq + Lean) + emitted text + consumer templates (truthiness, `or`-default, isinstance arms, narrowing substitution, `tuple`/`join`/`len`/`in`, KeyError on nested subscript, `hval_eq`/`hval_canon`, #349 derivation, insertion-order literals) + doc coherency (5 surfaces) + L3 byte-diff (must be inert: everything gated on `PyVal`) | 28-36 / — | 0 |
| T2 mover re-proof | the 21 hval mirror files re-proved (report: ~35-40 h of proof); on 2 shared slots realistically 24-30 h wall, overlapping T1's tail | — / 24-30 | 0 (the ledger does not move, nothing is lost) |
| T3 leaves | s362 `_record_key` (home `pycsl.py` ~0.5 h; needs `Tuple[PyVal, ...]` codomain = `HTuple`, hval `tuple()`, `HNone`, and the #349 derivation at its caller) — the only measured closer; then the small-home leaves of cv13's final list (candidates: s270 `_mixin_dep_pseudo_functions` if its trusted callee can be typed, s258 `_match_pattern_cond`, s249 `_handle_join_call`), each owing its home's whole-file proof (`expressions.py` ~11 h is the trap: at most one batch of it) | 8-12 / 12-20 | **2-4** |
| T4 family M / I / C | mutation of parameters, iteration over erased iterables, closures | — | 0 in this window (route (f), closure-lift are separate tracks) |

**Expected: 389 → 385-387.** The report's 1-5 and cv13's 1-of-43 are consistent with this; I see no
evidence for more. The deliverable of this window is the certified foundation (which every later batch,
including (f), needs) plus the make-or-break numbers; if the user's success criterion is a conversion count,
this is the wrong track to spend 85 h on.

### 3.7 Steps, with the refutation exit first

1. **Spike (T0, hours 0-6):** R6/R8 are done (pass with the hoisted loop length, refute without); run
   §3.5 on `functions.py` with the hoisted template. REFUTE → stop or
   switch to (e2) pending the ledger-plane decision; PASS → 2.
2. **User decisions needed before T1** (each a one-line answer): (a) the frozen constructor set of §3.3.1;
   (b) in-place widening of `hval` (21-file re-proof accepted) vs a gated second theory; (c) the #349 policy
   for tagged values (claim-conditional deny, ambient outside claims); (d) whether a WhyML `axiom` pair that
   is *realised* by the certified `pairs_get` may be admitted by the assumed-facts plane (needed only for
   (e2)); (e) `TypeError` stays static-refusal-only in this window.
3. **Certificates first (T1a):** Rocq + Lean for §3.4; `Print Assumptions` / `#print axioms` clean; commit.
4. **Emitted theory + consumers (T1b):** `preamble.py` theory text; `expressions.py` wrap / reads /
   `or`-default / isinstance arms / narrowing substitution / `hval_eq` / `tuple`-`join`-`len`-`in`;
   `statements.py` nested KeyError assert; `functions.py` `Tuple[PyVal, ...]` codomain; `Module5` slot tags;
   `pycsl.py` #349 derivation; the 5 doc surfaces (`bin/doc-coherency.py --check`). L3 byte-diff must be
   **inert** (everything gated on `PyVal` / `hval` selection); any corpus movement is a bug, not an M1 case.
5. **Mirror emission sweep + the 21 re-proofs (T2):** `bin/mirror-emit-sweep.sh`; queue the big files on
   the two slots (never `expressions.py` and `statements.py` together); any regression → fix the template,
   never re-trust.
6. **Pilot conversion s362 (T3):** port, L1, `--fun`, whole-file `pycsl.py`, vacuity probe; then the next
   leaves in small homes; stop when the home is a ~10 h file and the batch holds only one stub.
7. **Record** the (f) design spike (`fr4_alias*.mlw` + R4/R7 numbers) as the opening evidence of a separate
   by-reference track, census-gated on cv13 FINAL.

### 3.8 Open risks

- **Big-file E-matching is unmeasured** until step 1 runs; the one historical datum (2400 s) is from a single
  field retype on `stmt_control_flow.py`. The spike exists to turn this into a number.
- **Z3 under best-of-N**: every Z3 loop on an hval value goal costs 30 s of wall; the per-file budget in
  §3.5 caps it at 10 new timeouts. If the big files show hundreds, (e2) becomes mandatory and needs decision
  2(d).
- **Alt-Ergo cannot separate string literals (R5b, confirmed)**: `"x" <> "y"` times out; so does
  read-over-write across two literal keys. Every faithful multi-key dict *value* fact is Z3-only, and Z3 is
  the prover that loops on symbolic association lists (R1). Consequences: (a) the mirror's type-safety
  goals are unaffected (both arms of an undecided key comparison type-check), which is why the hval files
  prove today; (b) any value-level `ensures` over a dict with ≥ 2 literal keys — the non-vacuity witnesses
  of this track, a future value-faithful contract — needs Z3 **and** a loop-free encoding: (e2) (R3b) or the
  map carrier (R5a). So (e2) is not an optimisation to hold in reserve for speed; it is the precondition for
  Z3 to serve as the value-fact prover. The ledger-plane decision 2(d) should therefore be taken *now*, not
  on refutation. (c) It also means the current `hpairs_key_eq` spec gives Alt-Ergo nothing on literal keys:
  a two-key literal read under Alt-Ergo is undetermined (R9: the second key and the absent key time out,
  the first key proves; Z3 proves all three in ≤ 1 s).
- **The #349 policy change** (claim-conditional deny for tagged values) is a soundness-adjacent decision;
  the argument is the P1 argument already accepted for `#UND` (§7.131), but it widens what un-claimed
  functions may do. The user should rule explicitly.
- **TypeError stays static**: a `\all` function with an un-narrowed projection is refused, not proved; the
  mirror's shape is unclaimed so this does not bite the count, but it caps the model's faithfulness story.
- **Frozen-set regret**: `HSet` (2 stubs) and class instances are refused; if cv13 FINAL shows sets high in
  the ranking, the freeze is wrong and should be revisited *before* T1, not after.
- **Shared slots**: T2's 24-30 h wall assumes the two proof slots are mostly this track's; today both were
  held by other tracks for most of my session.

---

## 4. Answers to the report's open questions (§8)

1. *Value or state model?* Value model now, state model (f) as a separate project; "pure reads and laws
   convert; parameter mutation stays trusted" is the honest boundary of this window (§3.2).
2. *Absent vs None.* A real `HNone`; no `HAbsent`. Absence is already distinguished at the carrier level
   (`Map.get = None` vs `Some HNone`; `pairs_get = None` vs `Some HNone`), so `k in d` after `d[k] = None` is
   faithful without a new constructor.
3. *Hashing a typed mixed value.* A derivation when narrowing or schema makes the tag static; otherwise the
   `#UND` treatment (refused under `\all`, ambient outside) — there is no TypeError VC to attach an obligation
   to at HEAD (§3.3.2).
4. *`hstr_of`'s opaque arm.* Not audited today (confirmed: 4 emitter sites, no §7.131 registration); make
   every un-narrowed projection a §7.131 site.
5. *Is the `pairs_set` gap a coupling-rule violation?* Literally no (the rule speaks of value *shapes*), in
   spirit yes: the certified `pairs_set` is the literal constructor, not the write-back. §3.3.5 unifies them
   and certifies the emitted one.
6. *Z3 brittleness.* Acceptable under best-of-N for this window (Alt-Ergo ≤ 0.27 s everywhere measured), with
   the §3.5 cap; (e2) is measured to cure it (R3b) and is the fallback, gated on decision 2(d).
7. *Gate or extend?* Extend `hval` in place, once, with a frozen set (§3.1 item 2).

---

## 5. Files

- This response: `getting-better/dict-value-model-r4-response.md`.
- Spikes: `scratchpad/fr4/spk/gen.py` (generator), `fr4_rich.mlw`, `fr4_unfold.mlw`, `fr4_mapcar.mlw`,
  `fr4_mapcar2.mlw`, `fr4_arrow.mlw`, `fr4_alias.mlw`, `fr4_alias2.mlw`, `fr4_strlit.mlw`, `mono_rich.mlw`
  (derived from `scratchpad/rp4/em/mono.mlw`), `battery{,2,3,4}.sh`.
- Probes: `scratchpad/fr4/probes/p1_alias_nested.py`, `p1b_alias_top.py`, `p1c_alias_param.py`,
  `p2_keyerror.py`, `p3_eq_truth.py`, `p4_hash.py`, `p5_typeerror.py`, `emit.sh`, `*.emit.out`, `*.mlw`.
- Outputs: `scratchpad/fr4/out/*.out`, `battery*.log` (wall, rc, `oom_kill`), `progress.txt`.
