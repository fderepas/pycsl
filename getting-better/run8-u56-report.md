# run8-u56 report: route #616, call-site vacuity probes that why3 rejected

Executor u56, driver run #8. Branch `run8-u56`, tree `/home/fabrice/git/pycsl-u56`, base `run8-u54` @ `57d71f9d3`. Base tree for comparisons: `/home/fabrice/git/pycsl-u56-base` (detached @ `57d71f9d3`).

(DRAFT: filled in as jobs finish.)

## Root cause (one cause for all 21)

The #267 call-site probe in `src/pycsl/pycsl.py::_run_vacuity_gate._probe_one` finds each call `(f ...)` of a body-less `val` with an `ensures`. It wraps that call as `( check {vacpre}; let __vac_rK = <call> in check {vacpost}; __vac_rK )`. The scanner that finds where the call ends counted every `(`, `)`, `{` and `}` character, **including those inside WhyML string literals**. The mirror emitter is full of strings like `"(Array.make"`, `"("`, `")"` and `"absurd)"`. So:

- a call such as `(str_startswith_op py_val "(Array.make")` was closed one `)` too **late**, which swallowed the rest of an `||`/`&&` chain into the `let`. The result was `syntax error`, or `unbound function or predicate symbol '__and_l'` when the swallowed text crossed a `let __and_l = ... in` binder;
- a call such as `(str_eq_op t ")")` was closed one `)` too **early**, inside the string. The result was `illegal character in string`;
- a string such as `"(sorted_1 "` whose text starts with a `val` name was taken for a call site, so the rewriter inserted code **inside a string literal**;
- an unbalanced `"{"` or `"}"` inside a string corrupted the spec-brace depth counter. Every later site in the body was then silently skipped, or wrongly considered.

why3 then rejected the rewritten file: rc 1, a diagnostic on stderr, no goal records. The gate printed `[!] ... could not be checked (no probe goal surfaced ...)` and moved on, so the probe never ran.

## Fix

The scanner is now lexical. In both the outer site scan and the closing-paren scan, a string literal (including its `\` escapes) and a nested `(* ... *)` comment are each skipped as a single token. A site is still excluded when its own text contains a `{` character. That check is deliberately left character-blind: relaxing it would make an enclosing `pystr_cat "... ensures { ..."` call the outermost site, and the finer probes of the calls nested inside it would be dropped. The edit is inline (rule 9: no helper extracted). `_run_vacuity_gate` / `_probe_one` are `\trusted` in the mirror (`src/self-annotate/src/pycsl.py`, the `#@ \trusted` block at line 1013). The mirror file is untouched, so no section 10.4 re-port is owed.

## Census (type-only, no proof)

`scratchpad/u56/census.py` builds every call-site probe body with a given tree's rewriter and runs `why3 prove --type-only` on it. It covers the 8 mirror files that have rejections (`scratchpad/u56/emit/*.mlw`, emitted with `--no-proof --no-typecheck --keep-mlw` from the head tree, whose emission is identical to base):

| Rewriter | Functions with sites | Rejected by why3 | Total sites |
|---|---|---|---|
| base `57d71f9d3` | 182 | **21** (exactly the 21 of the landed logs) | 1391 |
| head | 182 | **0** | 1578 |

No function has fewer sites at head. 21 functions gained sites, the ones whose scan had been corrupted. Every site that differs between base and head is either a base mis-parse or the same site in its corrected form. Logs: `scratchpad/u56/census8c.log`, `census8-{base,head}.tsv`.

## Probe verdicts

(see below)
