# FINDING — THE `reason:` TAXONOMY TOKEN DOES NOT MOVE EMISSION BY A BYTE. IT REFUSES THE WHOLE FILE.
# (found 2026-09-13 by the convergence-metric Phase-3 PILOT, at HEAD `ef6da553`)

**STATUS: the Phase-3 pilot gate FIRED. Phase 3 is `BLOCKED:emission-moved`. The other 458
markers were NOT tagged. The pilot edit is fully reverted; the tree is clean and markers are
still 459.**

## THE CLAIM THAT WAS REFUTED

`ideas-for-convergence-metric.md` §3.8 proposes adding a second token to the `\trusted`
directive (`#@ \trusted reviewer: … reason: cost-scale:string-setops`) and says:

> "Check … that adding a token to the directive is byte-inert for emission (**it should be:
> the marker is a comment to Module 2**)"

**The marker is not a comment to Module 2. It is a PARSED DIRECTIVE WITH A CLOSED GRAMMAR,
and the grammar has no slot for a second token.** The premise is false, and with it the
"no prover time if byte-inert" cost estimate.

This is why `convergence-metric-implement.md` §0 challenge (3) demanded a pilot before the
459-line edit, and it is the **#96 pattern exactly**: a construct believed inert that was
not. *"Should be"* is precisely the claim this campaign punishes.

## THE MEASUREMENT

Pilot file `src/self-annotate/src/frontend/exec_splice.py` — chosen as the mirror file with
exactly ONE real marker (line 35, governing `_ExecSplicer.visit_Expr`) that ALSO has a
passing whole-file proof on record (`w49_exec_splice`, rc=0), so a baseline exists.

**BASELINE, established BEFORE the edit and COVERAGE-CHECKED (not merely A/B-compared):**

```
$ python3 src/pycsl/pycsl.py src/self-annotate/src/frontend/exec_splice.py \
      --import-path src/pycsl --no-proof --no-typecheck --keep-mlw
[+] Verification SUCCESS (--no-proof --no-typecheck: WhyML generated)
  11570 bytes · 304 lines · 40 `let`/`val` declarations
  sha256 62eeafd68dc9d3dc34e7215a0e170e10c16bfb74435e49831b75de7adaa44f8f
  line 285:  val _execsplicer__visit_Expr (self: _execsplicer) (node: int) : unit
```

That last line is the coverage evidence: the emission demonstrably **contains the marked
function, as the bodyless `val` the marker exists to produce**. A byte-diff over a baseline
that did not contain the marked function would have been vacuous.

**AFTER appending ` reason: unclassified` to line 35 — and to line 35 ONLY:**

```
[!] PIPELINE ERROR:
[parse]: PyCSL Syntax Error around line 39:
\trusted reviewer: pycsl-self-annotate reason: unclassified
unexpected trailing input (got NAME 'reason')
```

**MINIMAL PAIR — it is not `reason:` that is rejected, it is ANY trailing token:**

| line 35 content | verdict |
|---|---|
| `#@ \trusted reviewer: pycsl-self-annotate` | ACCEPTED |
| `#@ \trusted reviewer: pycsl-self-annotate reason: unclassified` | REFUSED (parse error) |
| `#@ \trusted reviewer: pycsl-self-annotate reason:unclassified` | REFUSED (parse error) |
| `#@ \trusted reviewer: pycsl-self-annotate x` | REFUSED (parse error) |

**REPRODUCED ON A SECOND FILE** so the scale claim is measured, not inferred:
`src/self-annotate/src/exception_model.py` line 77 — same `unexpected trailing input`.

## THE MECHANISM, NAMED

`src/pycsl/frontend/Module2_Parser.py`:

```
1411  def _parse_trusted(self):
1412      self.expect_bs("\trusted")
1413      reviewer = ""
1414      if self.at_name("reviewer"):
1415          self.advance(); self.expect_op(":")
1416          reviewer = self._grab_reviewer_id()
1417      return Trusted(reviewer=reviewer)
```

The production is `\trusted [reviewer: REVIEWER_ID]` and then it **returns**. The caller
requires the directive line to be fully consumed and raises at
`Module2_Parser.py:1321  self._err("unexpected trailing input")`.

## THE CONSEQUENCE IS WORSE THAN "EMISSION MOVED", AND THIS IS THE TRANSFERABLE PART

A refusal is not a changed emission. **A REFUSED FILE EMITS NO `.mlw` AT ALL.** Measured:

```
$ python3 src/pycsl/pycsl.py … --keep-mlw ; echo $?      # with the reason: token
1
  *** NO .mlw EMITTED — the baseline's 11570 bytes / 304 lines / 40 declarations are GONE ***
```

So a byte-diff sweep **that compares the files present in both trees would have reported
ZERO CHANGES** — a FALSE GREEN on an edit that silently stops **45 marker-bearing mirror
files (459 markers)** from emitting anything at all.

**This is route #42/#50's post-mortem happening again, live.** The handoff already records
it verbatim: *"A REFUSED file emits no `.mlw` at all, so it has NO BASELINE COUNTERPART, and
a diff-the-common-files sweep reports zero changes while a REFUSAL HAS BECOME AN EMISSION."*
The repo fixed that as a plane — `bin/byte-diff-compare.py` reports **MOVED / GONE /
APPEARED** and `byte-diff-sweep.sh` writes a `SOURCES.txt` manifest. **This finding is a live
demonstration that the fix earns its keep**: without the `GONE` arm, the taxonomy edit would
have passed the byte-diff and been landed.

Note also which gate caught it: the **type/parse gate**, not the byte-diff. Had the pilot
been run byte-diff-first on a diff-the-common-files sweep, it would have gone green.

## WHAT THIS COSTS PHASE 3

The taxonomy is **not** a bookkeeping pass over 459 comment lines. Two options, neither free:

1. **Extend the grammar** with an optional trailing `reason: <id>`. That is a PyCSL LANGUAGE
   CHANGE, and `config/skills/pycsl-audit-pycsl-language` binds it: wired through
   grammar → Module 4 validate → IR → Module 6 WhyML, documented on all five normative
   surfaces (`test-suite/annotations.md`, `README.md`, and the three `docs/` references),
   covered by the reference corpus, `bin/doc-coherency.py --check` green, plus the
   emission-identical byte-diff over BOTH corpora with the MOVED/GONE/**APPEARED** arms.
   This is a capability build, not the "~3 h, no prover time" the report priced.
2. **Carry the taxonomy OUT OF BAND** — a side file keyed by `(mirror file, function
   qualname)` rather than a token in the directive, read by
   `bin/count-trusted-directives.py --metrics` to print the histogram.
   **This needs no language change, no grammar risk and no re-proof**, and it delivers the
   same decomposition of the 459. Its weakness is drift: a side file can go stale against
   the markers, so it needs its own attachment check (every entry names a live marker; every
   marker has an entry) — which is cheap and is exactly the shape
   `count-trusted-directives.py` already enforces for `unattached`.

**Recommendation: option 2**, and price option 1 separately as a named capability if the
in-band spelling is ever actually wanted. The value the report is after is the HISTOGRAM,
and the histogram does not care where the reason is stored.

## REOPENING / RE-PROBE CONDITION

If the `\trusted` production is ever extended to accept trailing tokens, re-run this pilot
before believing any taxonomy edit is inert — and run it with a **long** reason value as
well as a short one, since nothing here has measured a length-sensitive path.

## STATE LEFT BEHIND

Tree clean, edit reverted, re-emission sha **byte-identical to the baseline**
(`62eeafd6…`), `bin/count-trusted-directives.py` rc=0 with markers **459** / grep 484 /
offset 25 / unattached 0. `bin/check-self-annotate-sync.sh` rc=0 (887 functions verbatim).
`bin/self-annotate-mirror-check.sh` is rc=1 at HEAD on
`expr_ghost_collections.py` / `statements.py` / `stmt_control_flow.py` — **PRE-EXISTING, not
caused by this pilot**: `git diff HEAD --stat` is empty, and none of those files was touched
here. Same family as `finding-L1-fidelity-plane-red-at-head.md`.
