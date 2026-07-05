# finding-wrong-lowering.md — systematically discover wrong / opaque / unsound lowerings

**This is a DISCOVERY / AUDIT plan, not a feature.** Its EXECUTION produces the deliverable
**`wrong-lowering-to-fix.md`** — a deduplicated, prioritized, evidence-backed backlog of concrete places
where PyCSL lowers a Python construct WRONGLY: a type collapsed to `int`/`array int` when a faithful type
exists (e.g. the old `a[i][j][k]` nested collapse), a semantically-WRONG WhyML representation (e.g. the
mutable-nested rejection), an OPAQUE abstract `val` whose result is unmodelled, or — worst — an UNSOUND
lowering that admits a false claim or a vacuous green. Every finding must be backed by an EXECUTABLE
driver that exhibits the defect; no speculative entries.

Aligns with the no-more-int doctrine ([[feedback_no_more_int]]) and extends the existing hand-kept catalog
`we-are-getting-better.md` (40 items) with a REPRODUCIBLE, TOOL-DRIVEN sweep.

---

## 1. What counts as "wrong lowering" — the taxonomy (severity order)

1. **UNSOUND** — the lowering lets PyCSL PROVE a claim that is FALSE of real Python semantics (e.g. a
   collision-admitting key hash proving a distinct-key property it shouldn't; a `-1` return where Python
   raises; `τ(float)=int` proving a false integer identity). Top priority: it can certify wrong code.
2. **FALSE-GREEN / VACUOUS** — the lowering yields a logically-inconsistent context so a false `ensures`
   discharges (the nonlinear-div class). Detect with the default non-vacuity gate.
3. **COLLAPSED (with a real consumer)** — a type is flattened to `int`/`array int`, losing structure that
   a genuine driver needs faithfully (the `a[i][j][k]` collapse; a dict value/element type dropped). The
   driver's true content property is UNPROVABLE though it should hold.
4. **WRONG REPRESENTATION** — the WhyML type is semantically off (mutable modelled as immutable or vice
   versa; a set modelled as an array; a signed int modelled as unsigned) — provability may be fine but
   the model doesn't match Python semantics.
5. **OPAQUE (no current consumer)** — an abstract `val` with only a length/type law, content unmodelled
   (most string transforms, comprehension content). Lowest priority unless a consumer appears.

**NOT wrong (the acceptable baseline — must NOT be flagged):** the ~80% DELIBERATE tractability collapses
documented in the **τ-table** (`docs/pycsl-static-semantics-reference.md §1.4`, translational §T.2.2):
`bool=1/0`, bare `tuple`→`array int`, etc. A finding is only valid if it is NOT a τ-table-blessed
collapse. The audit's hardest job is avoiding false positives against this baseline.

---

## 2. Detectors (complementary; each emits candidate findings)

**D0 — Calibration (do FIRST, like an SMT spike for a feature).** Before the full sweep, verify each
detector on KNOWN cases: it MUST flag a genuine wrong-lowering (reproduce one — e.g. revert
`nested-list` on a throwaway worktree, or a synthetic `τ(float)=int` snippet) and MUST NOT flag a
τ-table-blessed collapse (`bool`, bare tuple) or an already-faithful lowering (`map string` dict). Record
the precision/recall on the calibration set; a detector that false-positives on the baseline is not ready.

**D1 — Abstract-op census.** Enumerate every `val`/`val function` emitted across the pycsl-reference +
python-reference corpora (the ~147 distinct ops) via a `.mlw` scan, cross-referenced to the
`_add_abstract_op` sites and `preamble.py::_AXIOM_REGISTRY`. Classify each: FAITHFUL (native or full
content laws) / OPAQUE (partial/length-only law) / UNSOUND-RISK (result could admit a false claim, e.g.
an un-axiomatised hash). OPAQUE + UNSOUND-RISK → candidate findings, tagged with the op name and the
Python construct that emits it.

**D2 — Type-lowering matrix probe.** Auto-generate a small typed Python snippet for each cell of
`{Python type} × {position}`: position ∈ {param, local, return, record field, list element, dict key,
dict value, set element, tuple slot, nested@depth 1..4}; type ∈ {int, bool, float, str, bytes,
List[·], Dict[·,·], Set[·], Tuple[·], record}. Emit WhyML, extract the actual WhyML type, and diff
against a hand-authored EXPECTED-τ table (the faithful target). A cell whose emitted type is
int-collapsed where a faithful type exists — AND is not a τ-table-blessed deliberate collapse — is a
COLLAPSED/WRONG-REPRESENTATION finding. This is the primary catcher of `a[i][j][k]`- and
`mutable-nested`-style defects.

**D3 — CPython differential oracle (strongest).** Generate typed snippets with a CONCRETE computable
result; run the snippet under CPython (ground truth). Emit two drivers per snippet: (a) `#@ ensures
\result == <cpython-value>` and (b) `#@ ensures \result == <cpython-value + 1>` (a deliberately-false
twin). Failure modes → findings: **(a) proves the FALSE twin ⇒ UNSOUND (top severity);** (b) can't prove
the TRUE claim ⇒ COLLAPSED/OPAQUE; (c) the true claim is ill-typed ⇒ WRONG-REPRESENTATION. (Mirrors the
CPython-differential idea in [[os_returncode_not_exception]].)

**D4 — Non-vacuity sweep.** Run the default fail-closed non-vacuity gate (now on by default) across the
whole corpus + the D3 fuzzed drivers. Any non-exempt function that proves `ensures false` = a FALSE-GREEN
lowering (an inconsistent assumed context) → finding.

**D5 — Consequence / round-trip probes.** For each op the census marks FAITHFUL, author a
setup→operate→observe consequence test ([[feedback_formal_test_consequence]]): write→read-back,
pack→unpack, sort→is-sorted, replace→content. A FAITHFUL-tagged op whose true consequence is UNPROVABLE
is mis-tagged — a hidden OPAQUE/COLLAPSED finding.

---

## 3. Triage → the deliverable `wrong-lowering-to-fix.md`

Merge the candidate findings from D1–D5, then:
- **Dedup** against: `we-are-getting-better.md` (the 40 existing items), the documented boundaries in
  `choices.md` + the `cleared-*`/`nested-list` plans, and each other (same construct×position = one item).
- **Reject false positives**: drop anything that is a τ-table-blessed deliberate collapse or an
  already-documented sound boundary (with a note that it was considered and excluded).
- **Attach evidence**: every surviving finding gets a MINIMAL reproducing driver committed under a
  scratch dir (e.g. `getting-better/wrong-lowering/`) with its verdict (proves-false / can't-prove /
  vacuous / ill-typed).
- **Prioritise** by severity (UNSOUND > FALSE-GREEN > COLLAPSED-with-consumer > WRONG-REPR >
  COLLAPSED-no-consumer > OPAQUE), then by fix effort.

`wrong-lowering-to-fix.md` schema — one row per finding:
```
### WL-NN — <one-line>
- Construct / position: <e.g. `List[List[List[int]]]` element read at depth 3 / param>
- Current lowering: <the actual WhyML type/op emitted>
- Faithful target: <what it should be>
- Class / severity: <UNSOUND | FALSE-GREEN | COLLAPSED | WRONG-REPR | OPAQUE> / <1..5>
- Evidence: <driver path> → <verdict> (which detector: D1..D5)
- Deliberate-collapse check: NO (not a τ-table entry) — <why it's a real leak>
- Fix direction / effort: <sketch> / <S|M|L>
- Dedup: <we-are-getting-better #NN | choices.md ref | none>
```

---

## 4. Critical files / harness
- Detector harness (new, e.g. `bin/find-wrong-lowering.py` or a documented command set) driving
  `src/pycsl/pycsl.py` over generated snippets; scans `.mlw` output + the `--diagnostics-json`.
- Type-inference under audit: `frontend/Module5_IREmitter.py` (`_m5_annotation_to_whyml_type`,
  `_param_type_str` plumbing), `module6_whyml/types.py`, `module6_whyml/functions.py` — the int-default
  sites.
- Abstract-op surface: `module6_whyml/abstract_ops.py` + the `_add_abstract_op` calls +
  `preamble.py::_AXIOM_REGISTRY`.
- Baselines: the τ-table (static-semantics §1.4 / translational §T.2.2) and `we-are-getting-better.md`.
- The non-vacuity gate: `pycsl.py::_run_vacuity_gate` (D4).

## 5. Out-of-scope / soundness of the AUDIT itself
- **No false positives**: a finding must be a genuine leak, never a τ-table-blessed collapse or an
  already-documented sound boundary. Each is verified by an executable driver, not asserted.
- **No fixes here** — this plan only DISCOVERS and RECORDS. Fixing is the follow-on (each `WL-NN` becomes
  a scoped task, à la the `cleared-*` plans). Ordering: UNSOUND findings must be fixed with priority.
- The audit changes NO emitter code and adds NO axiom; it only runs probes and writes markdown +
  scratch drivers. It must be re-runnable to catch REGRESSIONS (a lowering that silently gets worse).

## 6. Gates (for the discovery run)
1. **Calibration passed** (D0): each detector flags the known-bad and spares the known-good/τ-table set.
2. **Every finding in `wrong-lowering-to-fix.md` has a committed, re-runnable repro driver + recorded
   verdict** — no speculative entries.
3. **Deduped**: no finding duplicates a `we-are-getting-better.md` item or a documented boundary (or it's
   explicitly cross-referenced).
4. **Prioritised + classified** per the schema; UNSOUND/FALSE-GREEN findings called out at the top.
5. The harness + generated drivers are committed so the sweep is reproducible.

## 7. Reference corpus
The generated repro drivers (esp. the D3 false-twin UNSOUND catchers and any D4 vacuity reproducers) are
committed under `getting-better/wrong-lowering/`; the genuinely-useful ones graduate into
`test-suite/corpus/pycsl-reference/` as `# pycsl-expected: FAIL` regression locks when their `WL-NN` is
later fixed.

**Expected outcome:** a reproducible harness + `wrong-lowering-to-fix.md` — a ranked, evidence-backed
backlog of real wrong lowerings (UNSOUND first), deduped against the existing catalog and the τ-table
baseline, each with a minimal reproducing driver — ready to be worked one `WL-NN` at a time exactly as the
`cleared-*` / `nested-list` campaign was.
