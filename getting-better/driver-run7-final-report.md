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
| `\trusted` (canonical grep) | 389 | **367 after L13** (374 after L12) |
| Proof-axiom ledger (Rocq / Lean, `proof_axiom_allowlist.py`) | 3 | 3 |
| WhyML assumed-fact families | — | +1: CERTIFIED-DEFINITIONAL (see below) |
| Landings | — | L9, L10, L11, L12, L13 |

- **Goal and stretch.** The goal (< 389) is met. The stretch goal (≤ 375) is met: 374 at L11, 367 at L13 (22 conversions).
- **The one sanctioned assumption.** The new assumed-fact family holds the two route-(e2) `pairs_get` equations. They are realised by the Rocq and Lean lemmas `pairs_get_nil` / `pairs_get_cons`, and recorded in `bin/check-assumed-facts.py`. This is the single exception to "no new axioms", granted by user decision (d), log 848. It is not a proof-assistant axiom, so the ledger stays at 3.

## 2. Landings

| landing | merge | contents | gates |
|---|---|---|---|
| L9 | 1e2d69f05 | lvQ open-world external-effect model; lvR increment 1; wh4 W-hash | v57 85/85; 5 mirror movers proved |
| L10 | 06fac6d26 | Dict value model r4 (lv4) + Rocq/Lean certificates (ce4); u43 emit_ir projector repair; lvR increment 2; lvS; u44 #599 #601 #602; u45 #603-#607 | step M: 23 mirror movers proved whole-file; M1 154 moved corpus files re-proved; v58 85/85 |
| L11 | 010d7aced | lvT generator-as-seq + re lastgroup | Module2 + sertop proved; v59 85/85 |
| L12 | c37d50422 | u46 #608 #609 | v60 85/85; mirror-inert |
| L13 | ad6323517 | lvU (batch F: 4 conversions) + lvV (batch G: sha-256 trio) + u47 #610 (the rt61 repair) | 6 mirror movers proved whole-file at an emission byte-identical to the tip; v62 85/85; full corpus 0/0/0 vs L12 |

## 3. Conversions (22 landed through L13)

- **L9:**
  - `_cache_root`, `_cache_store`, `_parse_args` (lvQ, external model);
  - `calcsize`, `_mutex_inv_application`, `parse_rocq_assumptions_block` (lvR, behaviour-identical respellings).
- **L10:**
  - `_parse_goal_blocks`, `_Harvester._normalize_leading`, `_synthesize_legacy_text` (lvR, typed-local lowering T2b-T6);
  - `_record_key` (lv4, dict model);
  - `_function_body_eqs`, `_residual_selectors_from_records`, `_json_goal_records` (lvS).
- **L11:** `_sexp_tokens`, `_lex_contract` (lvT).
- **L13:**
  - `_build_witness_str`, `parse_sexp`, `_find_coqc`, `_parse_mixin_sig` (lvU: `x or {}` on an `Optional[Dict] = None` parameter, `list(<generator-as-seq>)`, law-free `os.access` / `shutil.which` world queries, behaviour-identical respellings fuzzed on 200,010 inputs);
  - `_sha256_file`, `_cache_key`, `stable_hash` (lvV: law-free SHA-256 digest model; deterministic in the bytes, no injectivity, no length law).

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
| rt61 | lvU + lvV (report-only wrap-up round) | 7 false proofs, one family #610 (module-name shadowing): 6 INTRODUCED by lvU / lvV, 1 from lvQ's L9 model | Under plan line 92 (an introduced breach must be repaired before the batch is done): repaired by u47 (refusal-only) and landed together with lvU / lvV in L13 |

- **Routes repaired this run:** #586, #587, #588, #594, #596 (u43); #599, #601, #602 (u44); #603-#607 (u45); #608, #609 (u46); #610 (u47).
- **Routes still open:** the residuals of #597 (raises in dependency modules) and #598 (kwargs via `super().__init__`); route #583's F3; the documented residuals of #599, #603, #608.
- **Backlog notes from L13 (pre-existing, not introduced):**
  - a `str` subscript carries no IndexError / in-bounds VC outside `no_exception` (the obvious mutants of `_parse_mixin_sig` and `_find_coqc` prove; other mutants were used);
  - `audit_proof` imports `_sha256_file` / `_cache_key` as `val`s without `raises`, as at base (fixing it moves a non-home mirror file);
  - in a file that uses both sha shapes, the outer calls carry no `ext` rows, so handler-dependent claims around them are refused (fail-closed).

## 6. Decisions

**User decisions (relayed by the supervisor):**
- log 838: the dict-model boundary is reopened as the main track;
- log 841: dict-plan-review F1-F11 are reserved for Gate P (never shown to rp4 or the Gate R reviewer);
- log 848: decisions (a)-(e);
- log 907: #599 lands with or before int61;
- 05:11Z on the 16th: a WIP checkpoint from lvU, the second slot for the sha-256 trio, the last landing's proofs closed by 03:00Z;
- 09:15Z on the 16th: plan line 92 stands in wrap-up; an INTRODUCED red-team finding is repaired or the capability is withheld.

**Driver decisions:**
- log 936: #606 is a declared assumption (FLOAT-FINITE) with a strict-mode refusal;
- log 968: 3600 is a declared over-refusal;
- log 993: lvU and lvV land only together with the #610 repair (L13 as one battery; int64 alone was never landed);
- log 1002: u47's over-refusal check is targeted to the reachable files, with the full sweep done in v62 (0/0/0).

**Standing decisions respected:** the 31 external-world stubs were not reclassified; the #566/#567 mirror exemption was not used; nothing blocked on #497, the PyCSLError `line >= 0` precondition, `#@ \diverges`, #429, #414 or #461/#488 was converted.

## 7. Proof budget

- heavy.sh stayed at 2 proof slots throughout (v3slot never installed); every proof went through it; the guard hook was never bypassed.
- **oom_kill: 0 for the whole run** (pycsl-heavy.slice `memory.events`).
- The expressions.py and statements.py whole-file proofs never ran at the same time.
- The longest single proofs were the whole-file `functions.py` (1364 goals, ~68 min) and `pycsl.py` (812 goals, ~45 min). The longest gate is the --slow planes step of a battery (~4 h).
- Queue starvation was the main cost. It was handled with one-off PRIO grants for driver jobs, a one-slot rule for repair executors, and pausing secondary streams. The proof map let whole-file proofs start early on a snapshot and carry over to the final tip when the mirror emission was byte-identical (L10 step M; L13).

## 8. Incidents and lessons

- **Unquoted heredocs** ran backticks and damaged a brief and log 850. Lesson: quoted heredocs only (log.sh).
- **A worktree was removed while it still held an executor's uncommitted files** (pycsl-rp4; sp4 regenerated them). Lesson: check `git status` and archive untracked evidence before removing a worktree.
- **A brief was never written** because a `cherry-pick -q` failure broke an `&&` chain (u46). Lesson: verify the brief file exists before launching.
- **The driver killed its own shell** with `pgrep -f` (log 911), and **an executor killed another's planes** (log 860). Lesson: rule 25, kill only PIDs whose parent chain was verified.
- **full.sh ignored `# pycsl-flags:`**, which produced false "unexpected" verdicts. Fixed; the files were re-run with their flags.
- **An executor committed `progress.txt`**, which blocked the merge into the main tree (the user's untracked file). It was untracked in the integration branch before landing.
- **lvU went silent for ~8.5 h.** The driver salvaged its tree as WIP commits and gated it independently. Lesson: require a WIP checkpoint every 2 h (added to every later brief).
- **The cwd changes import resolution in sweeps** (a `json/` directory at the repo root). Lesson: sweeps that are compared must use the same cwd; the canonical one is the repo root.
- **The red team found that new external-effect models trusted the callee string** "<mod>.<f>" without checking that `<mod>` is the import, in the function scope (#610). Lesson: a new world model is not done until a red-team round targeting it has returned; schedule that round before the batch, not after.

## 9. End state

- **Branch `ghost-assign-bc6`:**
  - `\trusted` **367** (389 at the start);
  - proof-axiom ledger **3**;
  - one CERTIFIED-DEFINITIONAL WhyML family;
  - last landing L13 (`ad6323517`);
  - nothing pushed.
- **oom_kill:** 0 for the whole run.
- **Post-L13 non-landing work** (supervisor 16:20Z on the 16th). It is committed on run7-* branches only, each ending in a written result for run #8:
  - `run7-sp5` (6b0d5ecae), `getting-better/run8-spike-typed-tuple-return.md`. The typed tuple-return spike is a GO: corpus 0 / 0 / 0, 3 mirror movers, and `_why3_typecheck` proves.
  - `run7-u48` (e4e1bea94), `getting-better/run8-refusal-residuals.md`. Four refusal rules: R1 / R2 / R4 have 0 / 0 / 0 diff; R3 refuses 2 corpus and 3 mirror files (model it instead).
  - `run7-cv15` (3f00cac03), `getting-better/run8-census-seed.md`. The census seed at 367: `_sha256_file` in pycsl.py is one link away; ~212 receiver-dropping fallback sites.
  - `getting-better/driver-run8-plan-draft.md` on the main branch: the draft run #8 plan with these numbers.
- **Kept branches** (commit-only, never rewritten; 28): run7-ce4, run7-cv12 … run7-cv15, run7-int60 … run7-int65, run7-lv4, run7-lvQ … run7-lvV, run7-rp4, run7-sp4, run7-sp5, run7-u43 … run7-u48, run7-wh4.
- **END_CLEANUP**

## 10. Carried forward

- The backlog notes of §5 and the open routes.
- cv14 §3: `_why3_typecheck` (a typed tuple-return exception in the verified return handlers: statements / stmt_control_flow re-proofs plus a corpus-wide emission change), and the two precision gaps: a negative literal slice bound (`str_sub_op` with a negative length) and the receiver-dropping `str.rfind`. Both should be modelled or refused. They were not started after L13 because their re-proofs could not close by the 03:00Z cut-off (log 1018).
- The dict model r4: further yield needs the reopening-test rows (only 398 closes today).
