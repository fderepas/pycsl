# int-erasure-seam-r3-impl.md — implementation plan for route R5-str (spike-gated)

*Driver run #3, wall cycle step 5 (impl planner), executor ies1. Synthesized from
`int-erasure-seam-r3.md` (the report) and `int-erasure-seam-r3-response.md` (Gate R: oracle-run,
recommends **R5-str**). Base `a6ea830ed`. Hard time box 2026-10-26T20:00Z.*

## 0. What is being built, and what is not

Route **R5-str** (response §4.1) widens the existing, monomorphic, receiver-passing `str`-method
models so that a `str`/`List[str]` value no longer falls off the faithful model into the opaque
`int` placeholder. Four edits:

| step | edit | WhyML produced (all shapes already exist) |
|---|---|---|
| a | `module6_whyml/expressions.py` whole-list `.split(sep)` (the CF5 branch near `:10027`): gate on `_is_string_expr(receiver)` instead of `_current_self_type in _mutable_state_classes`. Outside `@mutable_state` the result is the plain `array string` (the `seq` `snapshot` is a `@mutable_state` list model). | `(str_split_op recv sep) : array string` |
| b | add `.splitlines()` on the same pattern (`.join` already has `str_join_arr`/`str_join_seq`; it is in scope only where its argument is a string-element array the classifier already knows) | `val str_splitlines_op (s: string) : array string  ensures { Array.length result >= 0 }` |
| c | `_is_string_expr` Subscript arm: an element read `xs[i]` of a Var whose **symbol-table type** is `List[str]` (an annotated local or a param) is string-typed; same for a `for` target iterating such a Var (consumer typing) | `str_strip_op xs[i]`, `str_eq_op … qn` instead of `strip_1 (subscript_get …)` / `x_strip_0 ()` |
| d | mirror only (fidelity plane allows annotations): annotate producer-bound locals (`lines: List[str] = stdout.splitlines()`) | `let lines = ref (str_splitlines_op stdout)` |

No new value shape (`string`, `array string` and `str_split_op`/`str_strip_op`/`str_eq_op` are already
emitted and covered), no polymorphism (route #325 untouched: every new op is monomorphic), no axiom
(ledger stays 3), contract shape unchanged.

**Not in scope** (response §4.4, §6.3): comprehensions/genexps (`(any int)`, 172 bodies), `re`,
`subprocess`/`tempfile`/`shutil` (R5-lib: new value shapes, coupling rule), cross-file self-methods,
`Iterator[...]` annotations, `[]`→`Array.make 1024 0`. R5-str moves the `int` boundary outward by one
family; it does not remove the seam.

## 1. FIRST ACTION — the make-or-break falsifier spike (Gate S)

**Name:** `S-R5str-reach` — *does the R5-str emitter change move ANY of the 179 seam stubs to a
non-vacuous TC-OK, at an acceptable corpus/mirror cost?*

The response's `.mlw` spike (`s3b`, Valid) shows the Why3 target is provable for stub 3; per lesson (s)
("a spike proves the target, the emitter gives the distance") the falsifier must be run on the
**emitter**, not on hand-written WhyML.

Procedure (scratch trees only, nothing under `src/` of the worktree is touched):
1. `T_n` = `git archive a6ea830ed` + the census-r3 guard-NEUTRALISATION patch (cv2 `h-all`: the seven
   refusal guards print `HYP-HIT:<code>` and continue) — the exact instrument that defined the 179.
   `T_c` = `T_n` + edits a, b, c (≈15–40 lines in `expressions.py`).
2. Re-measure stub 3 (`proof2why3/extract.py::_split_rocq_check_output`) in `T_n` and `T_c`, with and
   without step-d annotations, and read the emitted function (lesson (s)).
3. Port + `--no-proof --keep-mlw` **all 179** stubs of census r3 (`cv2/list-tc.tsv`) in `T_c`
   (`scratchpad/ies1/tc.sh`); for every stub whose verdict or clash changes, re-run it in `T_n` so the
   move is attributed to the change and not to the `ba41be495 → a6ea830ed` drift.
4. Every candidate TC-OK in `T_c` is screened: no input-blind `*_0 ()` facade / receiver-less op in
   the emitted function, then (if any remain) the four oracles of `bin/screen-conversion-candidate.sh`.
5. Corpus cost: byte-diff (root corpus + pyref) of `T_c`-minus-neutralisation (= the real candidate
   emitter) vs the base worktree; count MOVED files; mirror-emit sweep moved count.

**Verdict rule (fixed before the run):**
- **REFUTES → CERTIFIED-BOUNDARY, stop** if 0 of the 179 reach TC-OK with a non-vacuous emitted body
  in `T_c` (with step d applied where the stub binds a `str`-family producer to a local), **or** if the
  corpus/mirror cost is unacceptable (a moved corpus file that cannot be re-proved to its expected
  verdict, or a moved mirror whose type-check breaks). Then: record the measured chain residuals here,
  commit this doc, do not build.
- **PASSES → build (§2)** if ≥ 1 stub reaches non-vacuous TC-OK **and** passes the four screen
  oracles, with every moved corpus/mirror file re-provable.
- **REFINES → re-plan the residual** if stubs move (clash changes, chain advances) but none reaches a
  non-vacuous TC-OK: record the next-link census (which capability is now first), do not sprawl into it
  within this time box unless it is a ≤ 1-step extension of a–c on the same pattern.

## 2. Build (only after Gate S PASS) — §3 L-plane battery per increment

B1. Port the emitter change to `src/pycsl/module6_whyml/expressions.py` (Module 6). No helper
    extraction in mirrored files; the touched emitter methods' mirror twins: if any already-VERIFIED
    mirror method is edited, its re-port + re-proof co-lands (§10.4) — else the edit stays only in
    `\trusted`-twinned methods (checked with `grep` on the mirror before editing).
B2. Conversions the capability unlocks, **one commit per conversion**, each with the 5-point gate
    (driver-backlog "DO-NOT-CONVERT"): (1) `--fun` 0 non-Valid AND home-file whole-file proof 0
    non-Valid, (2) emit-diff = only assumptions becoming obligations, (3) planes green, (4) `\trusted`
    count down by exactly the markers removed, (5) corpus inert vs the B1 commit. The DO-NOT-CONVERT
    list is honoured (`subprocess`/`os.makedirs`/`Path.mkdir` under `assigns \nothing`, `pycsl.py`
    prover drivers, `proof2why3` extractors, `audit_proof_reverify` probes).

## 3. Gate battery (common brief rule 5; every rc reported, teed in full)

| plane | command | pass |
|---|---|---|
| L1 fidelity | `bash bin/check-self-annotate-sync.sh && bash bin/self-annotate-mirror-check.sh` | rc 0 |
| L2 proof | `--fun <m>` 0 non-Valid + home file whole-file `pycsl.py` 0 non-Valid (HEAVY_LOW=1) | `Verification SUCCESS` |
| L3 corpus | `bin/byte-diff-sweep.sh` base vs candidate, `bin/byte-diff-compare.py` once per tree (root, pyref) | 0 MOVED, or each MOVED = exactly the intended shape (`x_split_1 <h>`/`x_splitlines_0 ()`/`strip_1 (subscript_get …)` → `str_split_op`/`str_splitlines_op`/`str_strip_op …`) AND re-proved at base and candidate to the same expected verdict (M1) |
| mirror | `bin/mirror-emit-sweep.sh` base vs candidate | every MOVED mirror type-checks (`--no-proof`) and is OWED a whole-file proof (listed; short ones proved here) |
| planes | `bin/run-soundness-planes.sh` (fast 61) | green |
| ledger | `src/pycsl/proof_axiom_allowlist.py` untouched; no `axiom` in new ops | 3 |
| count | `grep -rhF '#@ \trusted' src/self-annotate/src --include=*.py \| wc -l` | 446 → 446−k |

## 4. Costed scope (honest)

- Spike: 179 ports × ~3–60 s `--no-proof` (QUICK slot) ≈ 0.5–1.5 h; corpus byte-diff ≈ 2 × 20–40 min.
- Corpus exposure (response row 15): `.split(` 14 + `.splitlines(` 0 root files; step c touches
  programs indexing/iterating `List[str]` then calling a `str` method (≤ 14 per method). Each moved file
  needs a base+candidate re-prove (minutes each).
- Mirror exposure: every mirror file with a `.split(`/`.splitlines()` on a `str` receiver or a
  `List[str]` element `str`-method — likely several of the big files (expressions/statements), whose
  whole-file proofs take 2–3 h each; at most one or two can fit in this time box, so the build is
  only worth starting if the spike's yield justifies it.
- Expected yield (response §6.3): single digits; stub 3 is the full-chain candidate, but its chain
  (read off the baseline emission at `a6ea830ed`) has ≥ 8 links: `splitlines` producer, `lines[i]`
  element typing, `stripped` local typing, `not stripped` string truthiness, `stripped in qualnames`
  membership, `lstrip()[2:]` slice + `startswith`, `" ".join(block).strip()`, `qualnames.index(qn)`
  (unconstrained op → bounds VC, response §4.2), and the mirror's `-> int` return placeholder vs the
  `map string (option string)` result. Also `proof2why3`'s extractors are on the DO-NOT-CONVERT list;
  `_split_rocq_check_output` is a pure parser (no subprocess) and is checked against the list
  before any conversion.

## 5. Spike results (Gate S) — filled in by the run

(pending)
