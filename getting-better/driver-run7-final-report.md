# Driver run #7: final report (self-tcb-reduction-driver, AUTONOMOUS, 96 h)

- **Window:** 2026-11-13T09:22Z to 2026-11-17T09:21:52Z (`getting-better/.driver-deadline` = 1794907312).
- **Branch:** `ghost-assign-bc6`. COMMIT-ONLY: nothing was pushed.
- **Run log:** entries 828 onward in `getting-better/driver-run-log.md`.
- **Plan of record:** `getting-better/driver-run5-plan.md`, with run #6's lessons:
  - 2 proof slots, which the user decided;
  - PRIO for driver proofs;
  - `PYTHON_CPU_COUNT` ≤ 6;
  - the proof map;
  - leaf-reachability;
  - executors that never end their turn.
- **Main track:** from run hour ~5, the dict value model, by user decision (log 838).

## 1. Results

| | start | end |
|---|---|---|
| `\trusted` (canonical grep) | 389 | **374 after L12**; L13 (lvU) see §2 |
| Proof-axiom ledger (Rocq / Lean, `proof_axiom_allowlist.py`) | 3 | 3 |
| WhyML assumed-fact families | — | +1: CERTIFIED-DEFINITIONAL (see below) |
| Landings | — | L9, L10, L11, L12 (+ L13 if gated) |

- **Goal and stretch.** The goal (< 389) is met. The stretch goal (≤ 375) is met: 374 at L11.
- **The one sanctioned assumption.** The new assumed-fact family holds the two route-(e2) `pairs_get` equations. They are realised by the Rocq and Lean lemmas `pairs_get_nil` / `pairs_get_cons`, and recorded in `bin/check-assumed-facts.py`. This is the single exception to "no new axioms", granted by user decision (d), log 848. It is not a proof-assistant axiom, so the ledger stays at 3.

## 2. Landings

| landing | merge | contents | gates |
|---|---|---|---|
| L9 | 1e2d69f05 | lvQ open-world external-effect model; lvR increment 1; wh4 W-hash | v57 85/85; 5 mirror movers proved |
| L10 | 06fac6d26 | Dict value model r4 (lv4) + Rocq/Lean certificates (ce4); u43 emit_ir projector repair; lvR increment 2; lvS; u44 #599 #601 #602; u45 #603-#607 | step M: 23 mirror movers proved whole-file; M1 154 moved corpus files re-proved; v58 85/85 |
| L11 | 010d7aced | lvT generator-as-seq + re lastgroup | Module2 + sertop proved; v59 85/85 |
| L12 | c37d50422 | u46 #608 #609 | v60 85/85; mirror-inert |
| L13 | pending | lvU (batch F) | — |

## 3. Conversions (15 landed through L12)

- **L9:**
  - `_cache_root`, `_cache_store`, `_parse_args` (lvQ, external model);
  - `calcsize`, `_mutex_inv_application`, `parse_rocq_assumptions_block` (lvR, behaviour-identical respellings).
- **L10:**
  - `_parse_goal_blocks`, `_Harvester._normalize_leading`, `_synthesize_legacy_text` (lvR, typed-local lowering T2b-T6);
  - `_record_key` (lv4, dict model);
  - `_function_body_eqs`, `_residual_selectors_from_records`, `_json_goal_records` (lvS).
- **L11:** `_sexp_tokens`, `_lex_contract` (lvT).

Every conversion has:
- a verbatim live body, or a documented behaviour-identical live respelling (fuzzed where the body was rewritten);
- `--fun` with 0 non-Valid;
- a whole-file proof of its home mirror file at the landing tip;
- a mutation test;
- a leaf-reachability check;
- fidelity;
- a corpus byte-diff;
- the planes.

## 4. The dict value model (main track; user decision log 838)

**Wall cycle.**

| step | artefact | author | verdict |
|---|---|---|---|
| Report | `getting-better/dict-value-model-r4.md` | rp4 | Reopening test 0/5 at HEAD; Z3 `pairs_get` matching loop measured |
| Gate R | `dict-value-model-r4-response.md` | fr4 (fable) | 9 spike batteries + 8 probes |
| Gate P | `dict-value-model-r4-impl.md` | driver | Adopted every finding F1-F11 of the reserved supervisor-plan review |
| Gate S | `dict-value-model-r4-spike.md` | sp4; re-checked by the driver | PASS on types.py (+3.8 %) and functions.py (+0.6 / +1.8 %) |

**User decisions (a)-(e) (log 848).**
- (a) A frozen 9-constructor `hval`: HNone, HBool, HInt, HFloat, HStr, HTuple, HArr, HMap, HNode. There is no HAbsent and no HSet.
- (b) `hval` is widened in place; the 21-file re-proof was accepted.
- (c) A claim-conditional #349 hashing derivation.
- (d) The (e2) equation pair.
- (e) TypeError stays static-refusal-only.

**Certificates.** Rocq `Phase2m_PyValR4.v` and Lean `PyCSL/PyValR4.lean`, plus the WhyML companion `getting-better/dict-r4-theory.mlw`.
- Rocq: 177/177 Closed.
- Lean: axioms within {propext, Quot.sound, Classical.choice}.
- The companion: 184 subgoals, 100 % proved by the union of the two provers.
- The driver re-checked all three (log 877).

**Yield.** One conversion through the model itself (`_record_key`), plus `_residual_selectors_from_records` and `_json_goal_records` through lvS's hval extensions. That is within fr4's 2-4 estimate. The reopening test (r3 rows) scored 1/5: only 398 closes.

**Soundness work on the model.**
- **rt59:** 33 false proofs in 5 families. 5 were introduced by the model and 28 were pre-existing in the old hval model. u45 repaired them before L10 (#603-#607).
- **rt60:** 7 pre-existing residuals. u46 repaired them in L12 (#608 #609).
- **Declared-assumption decision (#606):** NaN on PyVal floats proves in the default mode under the declared FLOAT-FINITE assumption, as for plain floats. It is now surfaced by `--soundness-report` and refused under `--strict-float-finite`.

## 5. Red team and routes

| round | scope | result | handling |
|---|---|---|---|
| rt58 | L9 | 8 false proofs in 3 families: #599 (introduced by lvQ: handler covered by one op, reached by another); #601 and #602 (pre-existing) | Repaired by u44 (L10; #599 was required to land with int61) |
| rt59 | int61 | 33 false proofs in families #603-#607 | Repaired by u45 (L10) |
| rt60 | lvT + u45 / u44 residuals | 7 pre-existing: #608 #609 | Repaired by u46 (L12). Nothing found in lvT |

- **Routes repaired this run:** #586, #587, #588, #594, #596 (u43); #599, #601, #602 (u44); #603-#607 (u45); #608, #609 (u46).
- **Routes still open:** the residuals of #597 (raises in dependency modules) and #598 (kwargs via `super().__init__`); route #583's F3; the documented residuals of #599, #603, #608.

(Sections 6-10, covering decisions, proof hours, incidents and lessons, and the end state, are completed at the end of the run.)
