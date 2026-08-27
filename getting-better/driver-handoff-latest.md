# HANDOFF — read this FIRST on relaunch (rewritten 2026-08-27, RELAUNCH #4 worker)

## State, verified from the surface

- **Count: `grep` 611 · MARKERS 586.** Quote BOTH. The two differ by a CONSTANT 25 and the
  campaign has been over-reporting by that much since it started — see the metric correction
  below. Window delta: grep **619 -> 611**, markers **594 -> 586** — EIGHT conversions plus two
  count-neutral interface repairs.
- Ledger **3**, untouched. No new axiom. Rocq `Phase2l_PyAstExpr.v` 35/35 `Closed under the
  global context`; Lean `PyAstExpr.lean` 34/34 (28 axiom-free, 6 `propext`, no `sorryAx`).
- Tree clean apart from the pre-existing user/build dirt (`session.txt`,
  `src/formal-semantics/rocq/.lia.cache`, untracked `scratchpad/`, `prompt.txt`). None of it is
  mine; leave it alone. `getting-better/.driver-deadline` intact.
- Field parity OK; `check-untrusted-emitted` **724/707/0/0**; vacuity GREEN; fidelity at the
  baseline **2 DIVERGED / 3 drifted**; corpus byte-diff **0 over 813/813**; the emitted mirror set
  is byte-IDENTICAL to the set that was proved.

## THE METRIC IS WRONG BY 25 — fix your expectations before you read any old record

`grep -rcF '#@ \trusted'` counts LINES CONTAINING THE SUBSTRING. **25 of the hits are one line of
boilerplate MODULE DOCSTRING**, repeated verbatim in 25 mirror files. The true directive count is
**588**, not 613. Every DELTA ever reported is correct (the offset is constant while the mirror
file set is) but every absolute "the floor is N" inherits the error — including
"COMPREHENSIVE AUTONOMOUS FLOOR at 687". Run **`bin/count-trusted-directives.py`**: it prints
markers / grep / the itemised offset side by side, fails on an UNATTACHED marker, and (with
`--emit-dir`) on a STALE one.

## Instrument facts (unchanged, still true, still silently corrupting)

1. **`why3` is NOT on the default PATH** (`/home/fabrice/.opam/framac-coq8/bin`). Without it
   `pycsl.py` errors AND EXITS 0. `export PATH=...` on every gate.
2. **`--import-path src/pycsl`** is the canonical mirror path (`run-self-annotation-suite.sh:27`).
3. **The Alt-Ergo pin at `pycsl.py:1318` is stale.** Pass
   `--provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,'` EXPLICITLY. Do NOT edit the pin.
4. `check-emitted-vacuity.py` is a false green without `--emit`.
5. **`.gitignore` has `*.mlw`** — `git add -A` SILENTLY SKIPS evidence files and reports success.
   Two of my commits cited artifacts that were not in the tree until I force-added them. If a
   commit message cites a file, `git ls-files` it.

## What this window did

**THE L2 CLUSTER IS CLOSED.** `_py_expr_to_ir` (619->618) and `_csl_to_ir` (618->617) CONVERTED
via a new type-keyed **dispatch expansion** over an input-side node ADT, co-landed with an
axiom-free Rocq+Lean certificate. `_py_stmts_to_ir` is a **CERTIFIED-BOUNDARY [COST/SCALE]**,
refuted by a measured erasure probe (evidence banked). A tree-wide census confirms there are
exactly THREE handler tables, so the vein is exhausted.

**THE LADDER WAS LOOKING IN THE WRONG FILE.** The first per-file marker census of this campaign:
`frontend/pure_ast.py` holds **186 of 588 markers = 31% of the entire TCB**, more than the next
FIVE files combined, with **96 in the single class `_Parser`**. The backlog had it filed behind a
"solver-context-saturation PROOF-SCALE wall"; measured fresh, the file proves **235 Valid in
minutes** — one of the CHEAPEST in the suite to gate. SIX conversions landed there (617->611) and
the file now proves **299 Valid, SUCCESS**.

**TWO CAPABILITIES LANDED THERE, both with consumers:**
 - the **CLASS-BY-NAME FACTORY** — `_N("<Class>")(<kwargs>)` resolved to a direct construction
   over the SAME-FILE-harvested `_NODE_SPEC` record, with a synthesized constructor, an
   `option`-field import gate, declaration-beats-inference for union locals, and an OPTION-TARGET
   union projection so an absent value is a true `None` and not `""`;
 - the **`_Parser` CURSOR CHAIN** — `cur` identity, `at_op` token-kind, the **EOF-SENTINEL class
   invariant**, `advance`'s increment, `accept_op`'s strict progress, and (the one the
   measurement forced) `_name_str`'s NON-REGRESSION. **A cursor-measure loop needs monotonicity
   from EVERY call in its body, not just from the guard.** Every `while self.accept_op(...)` loop
   in the class is now reachable.

**A WHOLE-MIRROR FRONTIER SWEEP**, the first that does not over-report: 574 candidates, 513
L3TC-FAIL, 28 ERASURE, 2 CLEAN (one of which was STILL wrong on inspection).

**TWO NEW GATES + ONE NEW TOOL**, all probed non-vacuous:
`bin/count-trusted-directives.py`, `bin/check-mirror-field-parity.py`,
`bin/probe-conversion-candidates.py`.

**91 CLASS FIELDS had drifted** between live and mirror with no gate comparing them; 84 retyped
(proof-neutral, corpus-inert), 7 remain and are itemized by name.

## Pick up here — in this order

1. **`accept_kw`'s monotonicity chain — a FIVE-MINUTE repeat of a landed pattern.** `at_kw` gets
   a token-kind postcondition exactly like `at_op`'s and `accept_kw` gets the strict-progress
   clause; both discharge against the EOF-sentinel invariant already in the class. It unblocks
   every `accept_kw`-using body. MEASURED as the blocker: giving `_import_as_name` the
   non-regression clause its caller needs makes its OWN postcondition time out, because its body
   calls `accept_kw`.
2. **Then `_import_as_names`** — its body already lowers PERFECTLY (cursor loop discharges, real
   `break`, accumulator snocs the CONVERTED `_import_as_name`). Its second blocker is the return
   annotation: `List[<harvested record>]`. **DO NOT "just add the typing import"** — see
   wall-lessons (ss); `List`/`Set`/`Dict`/`Tuple` are ASDL node names in `pure_ast`'s own globals
   and importing them from `typing` REPLACES the node classes and breaks the parser. Use a quoted
   annotation or a non-colliding alias.
3. **Budget `_fin` before funding the rest of the vein.** Almost every OTHER `_N` construction is
   wrapped in `self._fin(_N(…)(…), t)`, which SETS FOUR LOCATION ATTRIBUTES on a node whose type
   varies per call site. **`_fin`, not `_N`, is the gate for the remaining ~71 stubs** — a
   distinct and harder capability. `_N` is necessary, not sufficient.
4. **`for`-over-array has NO termination variant and the SOURCE CANNOT SUPPLY ONE** (the counter
   is emitter-internal). Do NOT send a window to write invariants for it. The capability is to
   emit the arithmetic index invariant/variant when the bound is already a pure LOGIC length
   term; the obstacle is the BYTE-DIFF (corpus drivers are not `@mutable_state` and get none
   today), so it needs an opt-in `#@` surface plus the doc-coherency/language-audit obligation.
5. Stage B of the `pyast_expr` build (recursive ADT, structural variant) — the honest
   strengthening of this window's two dispatch conversions. Phase-0b already proved the shape
   (16/16). It retires the four abstract vals the conversions introduced.
6. `_py_stmts_to_ir`'s six named features, if the window is long. Two of them add constructors to
   the CERTIFIED `stmt_ir` ADT, so the certificate must be extended under the co-landing rule.

## Method notes this window paid for (full text in wall-lessons.md, (jj)-(rr))

- **Re-measure an inherited PROOF-SCALE wall before you inherit it** — the most perishable kind
  of record in this campaign; one proof-hardening increment retires one silently.
- **Run a per-file census of the count at least once per campaign.**
- **A RAISE that models as a FALL-THROUGH is a facade** and only the emitted body shows it. Read
  the branch; require `absurd`.
- **The probe's CLEAN verdict was wrong 4 times out of 5.** Read the emitted body of every CLEAN.
- **A capability's SECOND instance is where its hidden assumptions surface** — budget for four,
  not zero.
- **A field retype does NOT cascade the way a return-type retype does** — check which you have
  before assuming the `Set[str]` disaster repeats.
- Count the LEVELS in an encoded-pair variant; a list mapper is a third level.
- A SYNTHESIZED call needs a synthesized ORDERING EDGE or Why3 rejects the file.
- **An edit to ANY live function whose mirror is UN-TRUSTED carries the §10.4 re-port
  obligation**, and the gate that catches it is the FIDELITY one — I skipped it once this window
  because the emission diff looked confined, and shipped a divergence.
- **In a module that installs generated classes into its own globals, an import is NOT
  namespace-neutral** (lesson (ss)) — and when an UNEXPECTED PIPELINE ERROR prints a message with
  no traceback, GET THE TRACEBACK before theorising. I filed a live-source bug of my own making
  as an emitter limitation.
