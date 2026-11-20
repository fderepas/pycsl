# run8-u56 report: route #616, call-site vacuity probes that why3 rejected

Executor u56, driver run #8. Branch `run8-u56`, tree `/home/fabrice/git/pycsl-u56`, base `run8-u54` @ `57d71f9d3`. Base tree for comparisons: `/home/fabrice/git/pycsl-u56-base` (detached @ `57d71f9d3`).

## Root cause (one cause for all 21)

The #267 call-site probe in `src/pycsl/pycsl.py::_run_vacuity_gate._probe_one` finds each call `(f ...)` of a body-less `val` with an `ensures`. It wraps that call as `( check {vacpre}; let __vac_rK = <call> in check {vacpost}; __vac_rK )`. The scanner that finds where the call ends counted every `(`, `)`, `{` and `}` character, **including those inside WhyML string literals**. The mirror emitter is full of strings like `"(Array.make"`, `"("`, `")"` and `"absurd)"`. So:

- a call such as `(str_startswith_op py_val "(Array.make")` was closed one `)` too **late**, which swallowed the rest of an `||`/`&&` chain into the `let`. The result was `syntax error`, or `unbound function or predicate symbol '__and_l'` when the swallowed text crossed a `let __and_l = ... in` binder;
- a call such as `(str_eq_op t ")")` was closed one `)` too **early**, inside the string. The result was `illegal character in string`;
- a string such as `"(sorted_1 "` whose text starts with a `val` name was taken for a call site, so the rewriter inserted code **inside a string literal**;
- an unbalanced `"{"` or `"}"` inside a string corrupted the spec-brace depth counter. Every later site in the body was then silently skipped, or wrongly considered.

why3 then rejected the rewritten file: rc 1, a diagnostic on stderr, no goal records. The gate printed `[!] ... could not be checked (no probe goal surfaced ...)` and moved on, so the probe never ran.

## Fix

The scanner is now lexical. In both the outer site scan and the closing-paren scan, a string literal (including its `\` escapes) and a nested `(* ... *)` comment are each skipped as a single token. A site is still excluded when its own text contains a `{` character. That check is deliberately left character-blind: relaxing it would make an enclosing `pystr_cat "... ensures { ..."` call the outermost site, and the finer probes of the calls nested inside it would be dropped. The edit is inline (rule 9: no helper extracted). `_run_vacuity_gate` / `_probe_one` are `\trusted` in the mirror (`src/self-annotate/src/pycsl.py`, the `#@ \trusted` block at line 1013). The mirror file is untouched, so no section 10.4 re-port is owed.

## Gate change: a why3 rejection is now a FAILURE

Every probe now runs (see the census below), so the brief's condition is met. In the `no probe goal surfaced` branch, a **non-zero** why3 exit with no probe record is a rejection of the rewritten body. It now prints `[-] vacuity call-site probe for 'F' could not be checked: why3 REJECTED the rewritten body (prover P, exit code N): <diagnostic>` and returns `F [could not be checked: why3 rejected the call-site probe body ... route #616]`. The #615 verdict code already turns that into `NON-VACUITY GATE FAILED ... COULD NOT BE CHECKED` and `Verification FAILED (vacuity could not be checked)`, rc 1. A clean why3 run (rc 0/2) that simply surfaced no probe goal keeps the old non-failing `[!]` warning. That case is not a rejection, and I have no measurement of it, so I did not touch it.

## Census (type-only, no proof)

`scratchpad/u56/census.py` builds every call-site probe body with a given tree's rewriter and runs `why3 prove --type-only` on it. It covers the 8 mirror files that have rejections (`scratchpad/u56/emit/*.mlw`, emitted with `--no-proof --no-typecheck --keep-mlw` from the head tree, whose emission is identical to base):

| Rewriter | Functions with sites | Rejected by why3 | Total sites |
|---|---|---|---|
| base `57d71f9d3` | 182 | **21** (exactly the 21 of the landed logs) | 1391 |
| head | 182 | **0** | 1578 |

**All 53 mirror files** (job2, `scratchpad/u56/census/{head,base}-mir.tsv`, built from the base mirror sweep `scratchpad/u56/sw/base/mir`):

| Rewriter | Functions with sites | Rejected | Total sites |
|---|---|---|---|
| base | 383 | **23**: the 21 above, plus `audit_proof._strip_rocq_comments` and `proof2why3/parser.lex`, which no landed whole-file log lists | 2125 |
| head | 383 | **0** | 2315 |

**Corpus** (head rewriter): root has 1013 functions with sites and 17 rejected; pyref has 33 with sites and 1 rejected. All 18 belong to files whose **own** emission is ill-typed: `why3 prove --type-only` on the unmodified `.mlw` reports the same error. Examples are `unbound ... 'iter_length'` (0793, 0794) and `int -> option int` vs `int` (1133-1143). pycsl refuses these files at the typecheck stage, before any proof or vacuity gate runs, so the rejection is not the rewriter's. The base rewriter rejects the same 18 (`census/rejchk.log`, `census/base-rej.tsv`).

No function has fewer sites at head. 21 functions gained sites, the ones whose scan had been corrupted. Every site that differs between base and head is either a base mis-parse or the same site in its corrected form. Logs: `scratchpad/u56/census8c.log`, `census8-{base,head}.tsv`.

## Probe verdicts (each function ALONE)

Driver: `scratchpad/u56/probe_run.py <tree> <mlw> <fn>`. It calls the head tree's real `_run_vacuity_gate` on the whole-file mirror emission, with the function list narrowed to the one function, the default provers (Alt-Ergo 2.6.3 then Z3 4.13.3) and `--vacuity-timelimit 5`. Every why3 call and every probe-goal answer is logged. Runs went through heavy.sh (`scratchpad/u56/job1.sh`, `job1b.sh`), one function at a time, with PYTHON_CPU_COUNT=2. Slice `oom_kill` was **15 -> 15** across every run (`pr/summary.tsv`).

From the 6th function onward I skipped the per-function `ensures false` probe (flag file `scratchpad/u56/SKIP_PERFN`). It already ran in the landed whole-file proofs, and skipping it saves about a third of the time. Those runs' RESULT therefore reflects the **call-site probe only**. For the first 5 (`_match_block_hdr`, both sertop functions, statements `_array_coerce_arg` and `_first_assign_kind`), both probes ran.

Verdict rule (#267): a function is VACUOUS iff some site's `vacpost` goal is proved and its `vacpre` goal is not. "post-valid" below counts sites where some prover proved the post goal on some path. Every such site also had its pre goal proved, so the continuation was already dead before the call (dead by design), not dead because of the callee.

| File | Function | Rejection cause at base | Sites (head) | Post-valid / pre-valid | Verdict |
|---|---|---|---|---|---|
| statements | `_array_coerce_arg` | `)` / `(` inside `"(Array.make"`... strings: `syntax error` | 18 | 0 / 0 | **not vacuous** |
| statements | `_first_assign_kind` | string `"(sorted_1 "` taken as a site, plus an early close: `syntax error` | 25 | 0 / 0 | **not vacuous** |
| statements | `_wrap_body_with_return_catch` | `"option ("` inside a call: `syntax error` | 27 | 0 / 0 | **not vacuous** (Z3 answered "Out of memory", which is why3's memlimit, on some sites; Alt-Ergo answered Timeout on all) |
| stmt_control_flow | `_handle_if_stmt` | `"absurd)"`: `illegal character in string` | 24 | 0 / 0 | **not vacuous** |
| stmt_control_flow | `_handle_return_stmt` | `"("` inside a call: `syntax error` | 80 | 56 / 56 | **not vacuous** (9334 s). The first run is VOID: I killed it myself (SIGTERM) because it would have hit job1's 3600 s per-function timeout. It was re-run whole in job1b. |
| pure_ast | `_parser___looks_like_match` | `")"`: `illegal character in string` | 30 | 0 / 0 | **not vacuous** |
| pure_ast | `_parser___sequence_pattern` | `"("`: `syntax error` | 17 | 0 / 0 | **not vacuous** |
| pure_ast | `_parser___with_parenthesized` | `"("`: `syntax error` | 5 | 0 / 0 | **not vacuous** |
| expressions | `_array_coerce_arg` | as statements: `syntax error` | 18 | 0 / 0 | **not vacuous** |
| expressions | `_coerce_to_int` | `"("`: `syntax error` | 11 | 0 / 0 | **not vacuous** |
| expressions | `_dv_missing_default` | `"(option "` inside a call: `syntax error` | 13 | 0 / 0 | **not vacuous** |
| expressions | `_handle_slice_access_expr` | `"(String.length "`, swallowed across a `let __and_l`: `unbound ... '__and_l'` | 24 | 14 / 14 | **not vacuous** |
| expressions | `_strip_outer_parens` | `"("` / `")"`: `syntax error` | 9 | 0 / 0 | **not vacuous** |
| Module1_Ingestor (extra) | `_match_block_hdr` | string parens: `syntax error` | 8 | 3 / 3 | **not vacuous** |
| sertop (extra) | `_process_sertop_line` | `"(Answer"`: `syntax error` | 1 | 0 / 0 | **not vacuous** |
| sertop (extra) | `_sexp_tokens` | `"("`: `syntax error` | 16 | 0 / 0 | **not vacuous** |

**No probe is VACUOUS.** There is no ESCALATE.

**Still not run alone** (time box): the 5 extra functions outside the brief's 13, which are functions.py `_compute_return_type` (56 sites), `_parse_mixin_sig`, `_refine_tuple_return_type` and types.py `_first_assign_kind`, `_split_tuple_type`, plus audit_proof `_strip_rocq_comments` and proof2why3/parser `lex`. Their probe bodies **type-check** at head (census), so the next whole-file proof of those files runs them. With this change, a rejection there would now be a hard FAIL rather than a silent skip. List: `scratchpad/u56/fnlist-c.txt`.

Logs: `scratchpad/u56/pr/<function>.log` and `pr/summary.tsv`.
