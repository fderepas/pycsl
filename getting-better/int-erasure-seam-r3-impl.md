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

## 5. Spike results (Gate S) — measured 2026-10-26 (scratch trees under the session scratchpad `ies1/`)

**Instrument.** `T_n` = `git archive a6ea830ed` + the census-r3 guard-neutralisation patch (cv2 `h-all`,
10 hunks, re-applied with offsets only); `T_c` = `T_n` + the R5-str edits. Driver `ies1/tc.sh` = the cv2
`hyptc.sh` loop (port → `--no-proof --keep-mlw` → clash slice), restoring the mirror file after each stub.

**S1 — edits a+b+c alone (no annotation edits), all 179 census stubs in `T_c`:**
- TC-OK **0 / 179** (179 L3-TC).
- Clash line changed vs census r3 (cv2 `hyp-tc`) in **4 / 179**; in every one the R5-str value now
  reaches one link further and stops at the next consumer that is still int-modelled:

  | stub | old first clash | new first clash |
  |---|---|---|
  | `proof2why3/extract.py::_split_rocq_check_output` | `(strip_1 (subscript_get !lines !i)) = !qn` | `contains_check (str_hash_op !stripped) qualnames` (`x in <List[str]>`) |
  | `pycsl.py::_parse_goal_blocks` | `join_1 !cur_header` | `iter_length (str_splitlines_op output)` (`for line in output.splitlines()` — iterating the CALL) |
  | `pycsl.py::_function_body_eqs` | `Arm_3_0 (m_group_1 1)` (`re`) | `iter_length (enumerate_1 !lines)` (`enumerate(<array string>)`) |
  | `frontend/ir_resolve.py::_resolve_module_path` | `path_isfile_op !pkg_init` | `os_path_join_3 (str_hash_op !base) !parts …` (`os.path.join(base, *parts)` star-arg) |

  The other 175 never reach a `split`/`splitlines`/element-of-`List[str]` site before their first clash
  (their first link is a comprehension, `re`, `subprocess`, a dict value, a record field, …).
- User-level probes (response `q1a/q1b/q1c/q4a/q4b`) all go from L3-TC (or a `ln_strip_0 ()` facade) to
  TC-OK with the faithful `str_split_op`/`str_splitlines_op`/`str_strip_op`/`str_eq_op` chain — the
  facade is gone (`grep -c '_0 ()'` = 0 on each emitted function).

**S2 — REFINE, one step on the same pattern** (plan §1 allowance): two more receiver-passing
`array string` ops, no new value shape, no axiom:
- e. `x in xs` (string `x`, `xs` an R5 local or a flat `List[str]` formal) →
  `val arr_mem_str (x: string) (a: array string) : bool ensures { result <-> exists i. 0 <= i < length a /\ a[i] = x }`
  (the existing `seq_mem_str` shape over an array);
- f. `xs.index(x)` on the same receivers → `val arr_index_str (a: array string) (x: string) : int
  requires { exists k. 0 <= k < length a /\ a[k] = x } ensures { 0 <= result < length a /\ a[result] = x }`
  — Python raises `ValueError` on absence, so presence is an OBLIGATION at the call (response §4.2 `s3b`);
- d. (mirror annotations only) `_split_rocq_check_output`'s mirror return `-> int` placeholder →
  the live `-> Dict[str, str]`, plus `#@ loop invariant 0 <= i` / `#@ loop variant len(lines) - i` on its
  two `while` loops and `#@ loop invariant 0 <= i` on the `for` (the live loops carry no variant).

Result on stub 3 in `T_c`: **TC-OK**, emitted function contains **0** `_0 ()` facades and reads
`stdout` (`str_splitlines_op stdout`), every `lines[i]`, and `qualnames` (`arr_mem_str`, `arr_index_str`,
element reads); `why3 prove -a split_vc -P alt-ergo -t 10` on the emitted file: **66 Valid, 0 non-Valid**
(before the loop annotations: 8 non-Valid = 3 loop terminations + 5 `lines[!i]` bounds, all fixed by the
`0 <= i` invariants/variants — none by the model).

**Gate S verdict: PASS (narrow) — 1 stub of 179 reaches non-vacuous TC-OK and proves; the capability
moves the chain of 4.** Corpus/mirror cost: measured in the build battery (§6).

## 6. Build B1 — the emitter change (Module 6), battery

Landed in `src/pycsl/module6_whyml/` (all touched methods are `\trusted` in the mirror —
`_handle_call_expr`, `_handle_len_call`, `_emit_membership`, `_is_string_expr` (unchanged here),
`_typed_local_vars`, `_classify_iterable`, `_handle_for_stmt` — so no verified twin is edited, §10.4
not triggered). **No new `self` field**: the R5 local set is merged into the existing
`_array_elem_types` map as `string` (that map is empty outside `@mutable_state`, so outside it a
`string` entry is exactly an R5 local), which keeps every declared `#@ assigns` frame honest.
Edits, all gated OFF inside `@mutable_state` (whose CF5 `seq string` model is untouched):
- a/b `_handle_call_expr`: `<str>.split(sep)` (1 positional arg, no keywords) → `str_split_op`;
  `<str>.splitlines()` → `str_splitlines_op` (plain `val`, `ensures { Array.length result >= 0 }`);
- c `_typed_local_vars`: a local EVERY assignment of which is such a call (and bound no other way,
  not a formal) is let-bound `array string` (`_array_elem_types[x] = "string"`), so `x[i]` is a
  string (existing classifier arm), `if x:`/`for t in x` use the array paths;
- c `_handle_for_stmt`: `for t in <R5 local | flat List[str] formal>` types `t` as a string local;
  `_classify_iterable`: `for t in <str>.splitlines()` materialised once like the `.split` arm;
- `_handle_len_call`: `len(<R5 split/splitlines call>)` → `Array.length`;
- e `_emit_membership`: `x in <R5 local | flat List[str] formal>` → `arr_mem_str`;
- f `_handle_call_expr`: `<same>.index(x)` → `arr_index_str` (presence REQUIRED).

B1 battery (commit `dbad763e6`, base `a6ea830ed`, base worktree `pycsl-ies1-base`):

| gate | rc | result |
|---|---|---|
| fidelity `check-self-annotate-sync.sh` / `self-annotate-mirror-check.sh` | 0 / 0 | 929 verbatim (incl. the B2 conversion) / 53 mirrors in sync |
| corpus root `byte-diff-compare.py BASE CAND` | 1 (M1) | 2423 / 2428 (+5 ADDED witnesses 5700–5704); **3 MOVED**: `1174_route72_split_valid_separator` (`s_split_1 <h>` → `str_split_op !s " "`), `1552_route160_split_with_a_literal_separator_is_allowed` (`iter_length (s_split_1 <h>)` → `Array.length (str_split_op !s " ")`), `3754_gen37_ch34_module_str_list_shadowed_false` (`!op = <hash>` → `str_eq_op !op "zz"`, the for-target over a `List[str]` formal). Re-proved at base AND candidate: 1174 PASS/PASS, 1552 PASS/PASS, 3754 (expected FAIL) FAIL/FAIL — verdicts kept, and 3754 now fails on the faithful string compare instead of a hash |
| corpus pyref `byte-diff-compare.py BASE/pyref CAND/pyref --min-files 2000` | 0 | 2186 / 2186, 0 MOVED |
| mirror `mirror-emit-sweep.sh` base vs emitter-only | — | 0 of 53 MOVED (emitter-only; with B2 exactly 1 MOVED = `proof2why3/extract`) — no mirror proof owed by B1 |
| witnesses 5700–5704 (candidate / base) | — | 5700 PASS/FAIL(L3), 5701 PASS, 5702 expected-FAIL FAIL (base: PROVED — the opaque `xs_index_1` carried no obligation), 5703 PASS/FAIL, 5704 expected-FAIL FAIL/FAIL |
| `run-soundness-planes.sh` (fast 61) | 1 → 0 | first run: 1 RED `check-claim-vacuity` (my witnesses added `requires True`/`ensures True`; contracts tightened, witnesses re-proved); re-run on committed HEAD `3e88d431a`: **rc 0, all 61 green (fast + conversion tier)** |
| ledger | — | `proof_axiom_allowlist.py` untouched; no `axiom` in any new op (all `val` + `ensures`/`requires`) |

## 7. B2 — conversions

| stub | result |
|---|---|
| `proof2why3/extract.py::_split_rocq_check_output` | **CONVERTED** (`3e88d431a`, 446 → 445). Whole-file proof 66/66 Valid, `Verification SUCCESS` (8m47s incl. queue); `--fun` 66 Valid; emit-diff = the trusted `val` becomes its `let` body, nothing else in the file moves; 0 `_0 ()` facades; planes conversion tier green; `check-trusted-reasons` 417↔417. Not on DO-NOT-CONVERT (pure parser, no subprocess). |

## 8. Final reach measurement and verdict

Re-run of all 179 census stubs with the FINAL emitter (`ies1/out-c2`, mirror signatures as at base):
0 TC-OK as ported (stub 3 needs its step-d return annotation, then converts — §7); clash line
changed in 3/179 (stub 3 now at its return placeholder; `_resolve_module_path` at
`os.path.join(base, *parts)`; `_function_body_eqs` at `enumerate(<array string>)` with `re` behind it);
`_parse_goal_blocks` is back to its census clash (`"\n".join(<List[str] seq local>)`, then a list of
tuples) after the `splitlines` iteration arm.

**Verdict: BROKEN (narrow).** R5-str is sound, corpus-cheap (3 moved, all re-proved, 0 pyref, 0
mirror) and converts **1** stub; it advances 3 more chains by one link each, and none of those is one
small step from TC-OK. The response's expectation ("single digits; stub 3 certainly") is met at its
low end. Residuals, in reach order:
1. `enumerate(<array string>)` over an R5 local (`_enumerate_seq_recv` already has the flat-formal
   array arm) — then `_function_body_eqs` hits `re` (R5-lib, coupling rule: new `re_match` shape);
2. `"sep".join(<List[str] seq local built by append>)` + `List[Tuple[str,str]]` accumulation
   (`_parse_goal_blocks`);
3. `os.path.join(a, *parts)` star-arg (`_resolve_module_path`);
4. the 175 stubs whose first link is not a `str`-family site (comprehensions, `re`, `subprocess`,
   dict values, record fields) are untouched by R5-str — the seam itself stands (R4 still blocked by
   the input-dispatch wall, per the response).

Soundness notes: `strip`/`lstrip`/`rstrip` share one plain `val str_strip_op` (fresh result per call,
length bound only — no false equalities); `.split`/`.splitlines` on a value `_is_string_expr` calls a
string but which is a `pathlib.Path` would be modelled instead of raising `AttributeError` — the same
pre-existing classifier precision as the `.strip()`/`.lower()` path, not new; `arr_index_str`'s
`requires` refuses the `ValueError` path (conservative: stricter than Python, never weaker).
