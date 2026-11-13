# Implementation plan: a real model of mixed-type values (wall `dict-value-model-r4`, Gate P)

*Driver run #7, wall cycle steps 5-7 (`config/skills/self-tcb-reduction-driver/SKILL.md` §4, Gates P / S / B / C).
Inputs:
- `getting-better/dict-value-model-r4.md`, the report (rp4, 71c47f152);
- `getting-better/dict-value-model-r4-response.md`, the independent Gate R review (fr4, model fable, 789ac6a0b;
  it cites 9 spike batteries and 8 emission probes, so Gate R's artifact requirement is met);
- the cv13 requirements census (interim 12b5ccb84 on `run7-cv13`; FINAL due 2026-11-14T00:00Z);
- a second independent review of the supervisor's summary plan (findings F1-F11, reserved for this gate by user
  instruction, log 841). Every finding is answered in §1.

User decision of record: log 838 (the boundary is reopened as the main track; a new value type is allowed with
Rocq + Lean certificates; no new axiom; ledger 3; refuse rather than approximate; all L-planes unchanged; watch
the E-matching cost early). Written 2026-11-13 ~16:40Z, about 89 h before the deadline.*

---

## 0. What this plan decides, and how it can be refuted

**Route.** Route (a) of the report, as fr4 shapes it (response §3.1):
- **The value type.** One FROZEN, certified value type replaces the current 5-constructor `hval` in place.
- **What it adds.**
  - faithful reads;
  - narrowing propagated after `isinstance`;
  - structural truthiness;
  - cross-type equality and key canonicalisation;
  - a structural hashability predicate, used as a *derivation*;
  - insertion-ordered dict construction through the certified replace-first/append `pairs_set`;
  - iteration lowered with a hoisted length.
- **Store rule.** The existing fail-closed r2c escape check, unchanged.
- **Rejected.**
  - (c): it reopens the #252 / #325 channels.
  - (b) as a separate model: its one load-bearing idea, a key→type table used as a derivation, is folded into the
    hashability / narrowing derivation.
- **Deferred.**
  - (f), the by-reference heap, goes to a separate census-gated track. fr4's `fr4_alias*.mlw` and its R4 / R7
    numbers are its seed.
  - (d), live refactors, is opportunistic only.
  - (e2), constructor-triggered `pairs_get` equations, is held behind a user decision (§5 Q2).

**The make-or-break spike comes before any `src/` edit (§3, Gate S).** It is numeric, on two real mirror files.

**Refutation exit.**
- If the spike REFUTES, `hval` is not widened. The track records a CERTIFIED-BOUNDARY for "in-place widening at
  this proof cost". It then re-plans the residual: a gated second theory, used only by opting-in functions, which
  does not move the 21 hval mirror files. That variant is measured by the same spike before it is built.
- If the residual also refutes, the track stops. Its deliverables are the certificates (if landed) and the
  measured numbers.

**Expected yield.** This counts whole-chain closures only (F1):
- **2-4 conversions**, `\trusted` 389 → 385-387 from this track;
- the measured closer is s362 `_record_key`; the others are cv13 FINAL's small-home leaves.

The window buys the certified foundation. Every later batch, including (f), needs it.

---

## 1. The reserved findings F1-F11: adopted / rejected

| # | finding | decision | where |
|---|---|---|---|
| F1 | yield is a ceiling (48 = first blocker; 16 end on the dict read itself; the dict capability alone completes 0) — count whole-chain closures | **ADOPTED.** Yield = whole-chain closures only; expected 2-4 (fr4 §3.6 agrees: s362 measured; cv13 interim 1 of 43 closes). cv13 FINAL must output, per op set, the rows whose whole chain closes with {model + landed capabilities}; the per-tier table §4 uses only those. | §0, §4 |
| F2 | freeze the constructor set and certify Rocq + Lean ONCE before building the two abilities | **ADOPTED.** Constructor set frozen here (§2.1); certificates (§3 step C) land before any emitter template depends on the new constructors; `Tuple[PyVal, ...]` codomain and the hval-polymorphic `tuple` are built on the final type only. One widening, one certificate round, one 21-file re-proof. | §2.1, §3 |
| F3 | fix `spike/run.sh` for all five rows at HEAD; stronger bar | **ADOPTED.** The reopening test is re-implemented on a fresh HEAD scratch tree with edit specs for all five rows (398 `_record_key`, 400, 034, 001 `_build_callee_no_exception_summary`, 250 — names and cv12 ids resolved by the executor). Bar per row: (a) honest TC-OK (input-reading, no facade, leaf-reachable); (b) `--fun` 0 non-Valid under the pipeline's provers (Alt-Ergo and Z3, best-of-N; each goal's prover recorded); (c) `check-emitted-vacuity.py` clean; (d) every new value-polymorphic builtin documents its wrong-tag arm in `test-suite/annotations.md`, and that arm is a refusal under a `no_exception` context or an uninterpreted value, never a concrete one; (e) a mutant witness per converted leaf. Pass = >= 2 of 5. | §3 step V |
| F4 | store rule: writes only into a fresh, unaliased root; else refuse; alias-mutation witness | **ADOPTED** (= fr4 §3.3.6: the r2c R1-R4 escape check unchanged; parameter / field roots refused; family M stays trusted). fr4's three alias probes P1a/b/c become corpus FAIL witnesses (refused), plus one alias program with a false `ensures` that must not prove on the candidate. | §2.4 |
| F5 | equality laws absent / None / bool (`True == 1`) | **ADOPTED** (= fr4 §3.3.3): `hval_eq` structural with the numeric tower (`HBool b ≡ HInt (0/1)`, `HInt i == HFloat f` iff `from_int i = f`), `HNone` only equals `HNone`, `(1,) != [1]`; `hval_canon` at every key position; `eq_canon_coherent` certified. Each law gets a witness pair (PROVED-at-base where it applies / REFUSED-or-unprovable on the candidate for the false claim). Absent ≠ stored None stays carried by the outer `option` (no `HAbsent`). | §2.2 |
| F6 | claim-gated KeyError / TypeError rule | **ADOPTED** (= fr4 §3.3.2). (i) Un-claimed code: total with an *uninterpreted* result (`any hval`), never a concrete junk value. The `(HInt 0)` junk continuation of `d[k]` is replaced. (ii) Under a claim covering KeyError: an `assert` that the key is present. This exists for the top-level map; it is ADDED for nested `pairs_get` reads, a gap fr4 found (P2). (iii) TypeError is not a VC class at HEAD (`KNOWN_EXCEPTIONS`). So every projection / wrong-tag site (`hstr_of`, `len`, `+`, iteration) is registered with the §7.131 static pass: it is REFUSED under `\all` and ambient otherwise. This closes the report's open question 4 (the unaudited `hval_opaque_str` sites). | §2.2 |
| F7 | cert / emitter `pairs_set` drift; extend coupling to operations; decide iteration order | **ADOPTED.** Every observable operation is either a definitional `let function` with a Rocq + Lean twin lemma, or listed below as an uninterpreted law-free `val`. The observable operations are get, set, literal construction, truthy, eq, canon, hashable, len / nth / tuple, and the projections. The `pairs_set` certificate is replaced by the emitted replace-first/append version, with `read_same_key`, `read_other_key`, `nodup_preserved` and `len_set` (fr4 R7 proves the WhyML twins by induction). Iteration order is DECIDED: insertion order. Literals are built by folding `pairs_set` (no more prepend), and iteration is the list order. | §2.3, §3 step C |
| F8 | #UND hashing is separate | **ADOPTED as a separate work item W-hash** with its own witness pair. It does not count as a side benefit. It is needed by s362 only because the caller hashes the tuple. Its policy (claim-conditional deny for a tagged value, ambient outside claims) needs a user ruling (§5 Q1). Until then s362 waits on it, and W-hash is built behind a flag that is off. | §2.5, §5 |
| F9 | numeric spike: `types.py` whole-file HEAD vs hand-patched theory, <= +25 %, no new Timeout | **ADOPTED and merged with fr4's §3.5 spike.** The spike runs on TWO files: `module6_whyml/types.py` (F9) and `module6_whyml/functions.py` (fr4: home of 6 BOUND stubs, ~1.6 h). Each runs pristine vs the frozen theory hand-patched with the hoisted-length template, per prover, in the pipeline's own call. PASS needs all of: (1) union Valid = 100 % of the pristine union; (2) no goal Valid on pristine becomes unproved by both provers (F9's "no new Timeout" read at the pipeline level: a Z3 timeout on a goal Alt-Ergo proves costs nothing in the best-of-N pipeline); (3) the pipeline wall (Alt-Ergo first, Z3 on its failures; sum of per-goal walls) <= +25 % (F9's bar, which is stricter than fr4's 1.5×); (4) new Z3 timeouts on goals Alt-Ergo does not prove <= 10. REFUTE otherwise. | §3 step S |
| F10 | numeric tiers; hot-home rows deferred by name | **ADOPTED.** Tiers in §4. Deferred to run #8 by name: every BOUND row whose home is `expressions.py`, `statements.py`, `stmt_control_flow.py` or `functions.py` (except as a re-proved mover), or `preamble.py` / `Module5_IREmitter.py` when that home's batch would hold only one stub (cv13 FINAL's list, recorded in the final report with its remaining chain). | §4 |
| F11 | smaller corrections | **ADOPTED.** (a) The mirror's `errors.py` has `PyVal = Any`. `_record_answer` / `_record_is_valid` are already `Dict[str, PyVal]`, and `_merge_records_best_of_n` is s362's consumer: the pilot converts the pair in order. (b) cv13 is cited by commit. (c) "No new axiom" also covers WhyML: a new operation is a definitional `let function`, and a `val ... ensures` is allowed only when it is realisable and cert-covered (as `hpairs_key_eq` is today). (d) Line citations are re-measured at HEAD by each executor. | §2.3 |

The supervisor-plan review's recommended route ((a)+(d): outer Why3 maps, a frozen nested hval sum, immutable
trees, narrowing; TypedDict refactor for run #8+) agrees with fr4's on every point but one.

- **The disagreement.** It lists `HAbsent` in the set. fr4 rejects it on evidence (R2: it buys nothing; absence is
  carried by the outer `option`).
- **Decision.** fr4's set (§2.1). The outer top-level dict stays a Why3 `map string (option hval)`, as it is today,
  which is the review's stratification.
- **TypedDict refactor.** Recorded as the run #8+ direction.

---

## 2. The design (frozen at this gate)

### 2.1 Constructor set (F2, fr4 §3.3.1)

```
type hval = HNone | HBool bool | HInt int | HFloat real | HStr string
          | HTuple hval_list | HArr hval_list | HMap hpairs | HNode hval
with hval_list = HNil | HCons hval hval_list
with hpairs    = PNil | PCons string hval hpairs
```

**Excluded.**
- `HAbsent`: absence is the outer `option`.
- `HSet`: no faithful order, and set equality is extensional. It concerns 2 stubs (s001, s279), which are refused.
- `HBytes` and class instances: refused.

**Revisit trigger.** If cv13 FINAL ranks sets among the top 3 needs of closing chains, the freeze is revisited
BEFORE step C, never after it.

**Floats.** NaN is a refusal site at comparisons. `HFloat real` carries no NaN.

### 2.2 Operations, exception and equality laws (F5, F6; fr4 §3.3.2-3.3.3)

**Reads, iteration and equality: fr4's table (response §3.3.2), verbatim, with these precisions.**
- `d[k]` in un-claimed code continues with `any hval`. Under a KeyError claim it gets a presence `assert`, for top
  and nested reads alike.
- `d.get(k)` yields `HNone` on absence.
- `isinstance` narrowing substitutes the projection in the guarded region.
- Truthiness is `hval_truthy` over all 9 arms.
- `==` is `hval_eq`.
- `len`, `tuple` / `join` / `sorted` / `for` are polymorphic over `HArr` / `HTuple` / `HStr` / `HMap` keys, with a
  hoisted length in every `variant` / `invariant` / loop condition. fr4's R6 / R8 found that 7 of 20 Alt-Ergo goals
  are lost without the hoist.
- Wrong-tag and non-iterable arms are TypeError sites (static pass).

**Stores.** The r2c functional write-back under R1-R4 only; everything else is refused.

### 2.3 Certificates and the operation coupling (F7, F11c; fr4 §3.4)

**Scope.** Rocq (a `Phase2f_PyVal.v` successor) and Lean (a `PyVal.lean` successor) cover fr4's §3.4 table:
- the 9-constructor mutual inductive, with `size` and `size_pos`;
- injectivity and the 36 pairwise disequalities;
- `pairs_get`;
- `pairs_set` replace-first/append, with read-back, `nodup` and `len`;
- the literal fold;
- `hval_truthy`, against the Python truthiness table;
- `hval_eq` / `hval_canon` / `hval_hashable`, with the cross-type table, `eq_refl` on non-float, `eq_sym` and
  `eq_canon_coherent`;
- the list `len` / `nth` / `tuple` lemmas;
- the projections, with `proj_on_tag`.

**Uninterpreted, law-free and listed** (not certified): `hval_opaque_str`, `hval_values_get/len`, `hval_keys_get`,
`hval_as_map`, `pycsl_none_map`.

**Axiom audits.** `Print Assumptions` / `#print axioms` stay within `proof_axiom_allowlist.py`. The ledger stays 3.

### 2.4 Mutation and aliasing (F4)

- **Rule.** Value semantics behind the fail-closed escape check, unchanged. A store is lowered only when its root
  is a non-parameter, non-field local built from literals, never bound to another name, passed or iterated. Every
  relaxation is route (f)'s, and refused until then.
- **Witnesses.** P1a/b/c (refused), plus a false-`ensures` alias program that must not prove.

### 2.5 W-hash: hashability by derivation (F8; fr4 §3.3.4)

- **Predicate.** `hval_hashable` holds structurally for scalars and tuples of hashables. The #349 pass admits a
  PyVal-typed hashed value when either holds:
  - a dominating `isinstance` narrows it to a hashable tag;
  - the mirror's TypedDict schema types the slot as a scalar.

  This is a derivation: a wrong schema sends the value to a refusal, never to a proof.
- **Otherwise.** Refused under `\all`. Outside a claim it is admitted as ambient (USER RULING NEEDED, §5 Q1).
- **Witnesses.** A pair: an unhashable `HArr` key under `\all` is REFUSED, and a narrowed scalar key PROVES.

---

## 3. Steps (first executed action = the spike)

| step | what | who | slots | gate |
|---|---|---|---|---|
| **S (make-or-break)** | Hand-patch the frozen theory (§2.1, hoisted-length template, absent defaults → `HNone`, new arms in every emitted `match` over `hval`) into the base emissions of `module6_whyml/types.py` and `module6_whyml/functions.py`; run the pipeline's per-prover call (`why3 prove -a split_vc -P <p> --timelimit 30 --json`, the exact flags pycsl.py uses) for Alt-Ergo and Z3 on pristine and patched; tabulate per goal. Criterion §1 F9. Also re-run fr4's R6 / R8 control on `monomorphize.py` as a replicate. Also emit (QUICK) the F3 reopening rows at HEAD with the stand-in theory to pre-check the five edit specs. | executor **sp4** (HEAVY_PRIO) | 2 PRIO, ~6-8 slot-h | Gate S: PASS → C; REFUTE → exit §0 |
| **C (parallel with S, discarded on REFUTE)** | Rocq + Lean certificates for §2.3 in a worktree; `make` / `lake build` via heavy.sh; `Print Assumptions` / `#print axioms` clean; ledger 3. Lands on main only after S PASSES. | executor **ce4** | coqc / lake (small) | certificates build, axiom audit clean |
| **T** | emitter: preamble theory text (frozen set, certified `pairs_set`, literal fold, `hval_eq` / `canon` / `hashable` / `truthy`, hoisted-length iteration), expressions (wrap, reads, `any hval` continuation, narrowing substitution, `tuple` / `join` / `len` / `in` polymorphism, `==` via `hval_eq`), statements (nested KeyError assert), functions (`Tuple[PyVal, ...]` codomain = `HTuple`), Module5 slot tags, the §7.131 TypeError-site registration; docs (the 5 surfaces, `bin/doc-coherency.py --check`); corpus witnesses for every law (§2.2, §2.4) and controls. L3 byte-diff must be INERT on the corpus except the declared PyVal-using files (every mover listed and re-proved, M1). | executor **lv4** | QUICK + NORMAL | fidelity, byte-diff (M1), fast planes, ledger 3 |
| **W** | W-hash (§2.5) behind a flag, ON only after the user's ruling | lv4 | — | witness pair |
| **V** | Reopening test re-implemented at HEAD + candidate (F3 bar), all five rows | lv4 / driver | QUICK + `--fun` | >= 2 / 5 |
| **M** | Mirror emission sweep; re-prove EVERY moved mirror file whole-file (expected: the 21 hval files + the homes), PRIO, never `expressions` and `statements` together, PYTHON_CPU_COUNT=6; batched WITH u43's owed hot-file movers so each file is proved once for both. A regression is fixed in the template, never re-trusted. | driver | 2 PRIO, ~35-40 slot-h | 0 non-Valid per file |
| **P** | Pilot conversion s362 `_record_key` (+ its consumer `_merge_records_best_of_n` if its chain closes) in `pycsl.py`, then cv13 FINAL's small-home leaves | lv4 | NORMAL + home proofs | per-conversion gates (base loop), leaf-reachability, mutation |
| **L** | Integration tree + battery (A-F, --slow) + land | driver | — | as in `driver-run5-plan.md` |

---

## 4. Tiers (F10, numbers)

| tier | content | when | conversions |
|---|---|---|---|
| Minimum | report + review + this plan committed (done); spike S measured with a verdict; certificates C built (landed if S PASSES) | by 2026-11-14 ~06:00Z | 0 |
| Target | S PASS; C + T landed; M (all moved mirror files re-proved 0 non-Valid); reopening test >= 2 / 5 under the F3 bar; s362 converted and landed | by 2026-11-16 ~12:00Z | 1-2 |
| Stretch | <= 5 conversions, all in homes <= 1 h proof; `\trusted` 389 → >= 384 from this track | by the hour-90 close (2026-11-17 03:20Z) | 3-5 |

**Deferred to run #8 by name:** the hot-home BOUND rows (cv13 FINAL list), family M (parameter mutation, 17 stubs,
route (f)), family I / C (erased iterables, closures), and the (e2) encoding unless Q2 is answered yes.

---

## 5. Open user decisions (asked through the supervisor; the build does not wait for them except where stated)

- **Q1 (W-hash policy).** May the #349 pass make its deny claim-conditional for a TAGGED value? That means refused
  under `\all`, and admitted outside a claim as an ambient TypeError, the same P1 argument as the accepted `#UND`
  R-gate (§7.131). It stays unconditional for a value statically known to be a list / dict / set.
  - **If no:** W-hash admits only derivation-proved hashable values. s362's caller is then refused, and s362 stays
    trusted.
  - **Default until answered:** OFF.
- **Q2 ((e2) encoding).** May the assumed-facts plane admit the two constructor-triggered WhyML equations for
  `pairs_get`? They are realised by the certified `pairs_get` (proved as Rocq / Lean lemmas). Without them, Z3
  cannot prove multi-key value facts and Alt-Ergo cannot separate string literals (fr4 R5b / R9). Every value-level
  witness with >= 2 literal keys would then be unprovable.
  - **Default until answered:** NO. The rule "no new axioms" stands, and witnesses are designed with a single
    literal key or with symbolic keys.
- **Decided by the driver here, within the user's decision:**
  - the constructor set (§2.1);
  - in-place widening, which accepts the 21-file re-proof and is batched with u43's movers;
  - TypeError stays static-refusal-only in this window.

---

## 6. Gate battery (unchanged, per increment, driver-verified FRESH)

Every increment must pass all of the following:
- fidelity (`check-self-annotate-sync`, `self-annotate-mirror-check`, `doc-coherency --check`);
- whole-file Why3 0 non-Valid for every moved mirror file;
- corpus byte-diff root + pyref (0 MOVED, or only declared movers, each re-proved to its expected verdict);
- the fast planes, plus individually `check-vacuous-drivers`, `check-assigns-writes-survival`,
  `check-trusted-frame-honesty`, `check-getattr-erasure`, `check-mirror-coverage` and `check-emitted-vacuity`;
- ledger == 3;
- `\trusted` strictly down for conversion increments;
- no new axiom (Why3 or proof-assistant), no gate loosening, no new `\trusted`.

Then the integration tree + battery A-F (--slow) before landing.
