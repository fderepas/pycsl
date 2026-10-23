# wall-plan Phase 1 — Track-R-only (R3 / R1' / R2) execution + measured verdict

**Executes Phase 1 of `generic-dict-str-and-plan.md` §6, re-grounded on the Phase-0 verdict
(`wall-plan-phase0.md`): Track M HALTED (fmap NO-GO, independently confirmed), Track-R-only proceeds
through the EXISTING certified IR-node ADT (`preamble.py::_emit_exprir_theory`,
`expressions.py::_KIND_DISCRIMINANT`, `functions.py` size/variant). No new value model built; `pyval`/
`fmap` untouched.** Branch `ghost-assign-bc6`, HEAD `a657569c`, `\trusted` = **1240**. Provers system
Alt-Ergo 2.6.2 + Z3 4.13.3 under Why3, `.venv` active (libcst present, LIVE bodies asserted).

## OVERALL PHASE-1 VERDICT — **STOP-LOSS at 1240; 0 conversions; R3 blocked.**

The Track-R Phase-1 surface is blocked by a **pre-existing RED baseline** on the only two
ADT-capable mirror files, compounded by the census-confirmed B1 ceiling on the clean-baseline files.
Trajectory **1240 → 1240**. Measured clean rate **0 / 1** direct attempt (plus the Phase-0 tier-5
census's **0 / 98** on the same surface). Stop-loss (plan §6 Phase 4) triggers on the first batch.
Ledger held at 3 axioms; `proof_axiom_allowlist` untouched; no `src/pycsl`/mirror edit landed.

| item | outcome | why |
|---|---|---|
| **R3** tuple-unpack per-slot typing | **BLOCKED (not landed)** | targets live in RED files + is a value-model feature, not a small typing tweak (below) |
| **R1'** typed accessor facade | **NOT BUILT** | its only consumers are R2 walkers, which are blocked → building it alone is gold-plating (task's explicit prohibition) |
| **R2** non-recursive incidental walkers | **0 converted / 1 attempted** | ADT reflection needs a @mutable_state class; the @mutable_state files are RED; the clean files are plain classes → B1 string/int |

---

## 1. The decisive finding — the mirror baseline is RED at HEAD (pre-existing, not introduced here)

The task's premise "tree clean, gates green" does **not** hold at HEAD. The self-annotation suite
(`bin/run-self-annotation-suite.sh`) has three FAILING files at HEAD, with **zero** edits to
`src/pycsl` or the mirror from this session (`git status --short src/pycsl src/self-annotate` empty):

| mirror file | suite | whole-file typecheck | failing (verified) method | error |
|---|---|---|---|---|
| `module6_whyml/expressions.py` | **FAIL** | `.mlw:669` | `_handle_field_get_expr` | `int_to_string (… Map.get self._class_constants …)` — `_class_constants` declared value-type `option int`, read as **string** → `type int, but expected string` |
| `module6_whyml/statements.py` | **FAIL** | `.mlw:508` | `_handle_array_set_stmt` | `type int, but expected type string` |
| `pycsl.py` | **FAIL** | — | (driver) | — |
| types.py, functions.py, ir_scanner.py, identifiers.py, scc.py, abstract_ops.py, auto_trust.py, Module6_WhyMLTranspiler.py, stmt_control_flow.py (typecheck ✓) | PASS | ✓ | — | — |

**Root cause (git-traced).** The `_class_constants`/`_all_record_fields`/array-set int↔string leaks
sit in verified methods that were **resync-ported to their live WL-era bodies** (`4ef18975`
"resync mirror `_handle_array_set_stmt` to live (WL-04f drift)"; the WL-05b/WL-06 series). The
ledger entry for `e73ec7c6` already recorded these two files as carrying a "**pre-existing int↔string
leak … in an unconverted method**"; the later WL commits degraded it from a localized leak into a
**whole-file typecheck failure**. This is the SKILL §10.4 failure mode ("a feature that edits a
verified emitter method MUST re-port + re-prove that mirror method in the same commit; if it can't
prove, do NOT re-trust and do NOT merge a red verified method") — landed anyway across the WL series.

**Consequence.** A whole-file typecheck failure blocks `--fun` proof of **every** method in the file
(Why3 type-checks the whole module before proving any goal). Verified with
`pycsl.py statements.py --import-path src/pycsl --fun statementemissionmixin___handle_tuple_unpack_stmt`
→ same `.mlw:508` type error, no goal reached. So **no conversion and no re-port can pass its
type-safety gate in expressions.py or statements.py** until the baseline is restored to green.

## 2. R3 — tuple-unpack per-slot typing — BLOCKED, and larger than "a small typing fix"

R3's two motivating constructs both route through methods that are **verified (non-`\trusted`)** in
RED files, so editing them triggers §10.4 re-port+re-prove — which cannot even typecheck:

- **`ret, _, _, _ = f()`** (Call-unpack) → `statements.py::_handle_tuple_unpack_stmt` (RED file).
  Per-slot typing already exists there, gated on `_current_self_type ∈ _mutable_state_classes` via
  `_resolve_dotted_signature`; generalizing it edits a verified method that can't be re-proved now.
- **`for nm, v in (("tag_int",0), …)`** (`_emit_metatype_tags`, expressions.py, RED file) → the
  for-loop tuple-target path (`stmt_control_flow.py::_classify_iterable` + `_handle_for_stmt`). A
  tuple-of-pairs **literal** iterable lowers to the **opaque `iter_length`/`iter_get` (int)** path;
  making `nm` a string and `v` an int requires **modeling the heterogeneous tuple-of-pairs literal as
  a real typed sequence of pairs** — a value-model FEATURE (the emission-defect spike,
  `emission-defect-spike-findings.md`, already classified this exact case as an `int vs string`
  value-model gap, not a declaration tweak), not the "small typing-precision" item the plan hoped
  for. It also touches verified `_handle_for_stmt`. **Out of scope for a Track-R Phase-1 increment.**

Byte-diff was therefore never the binding constraint on R3; the type-safety gate is unreachable.

## 3. R2 — non-recursive incidental walkers — measured 0/1; the surface is structurally blocked

The Phase-0 census′ (`wall-plan-phase0.md` §4) measured an 0.90 *rewritability* fraction but with the
explicit caveat that the yield is **staged**: the ADT reflection that makes a tag-dispatch/accessor
rewrite lower faithfully (`.get("type")`→`kind_of`, `.get("name")`→`name_of`, string dispatch instead
of an int collapse) is **gated on the reader's class being `@mutable_state @dataclass`** (SKILL leaf-
conversion-recognizers §7: `ExpressionEmissionMixin` IS @mutable_state; `TypeInferenceMixin` is a
PLAIN class). The two axes do not intersect at HEAD:

- **@mutable_state files** (expressions.py, statements.py) — ADT reflection available — are **RED**
  (§1). Nothing converts there.
- **Clean-baseline files** (types.py, ir_scanner.py, functions.py) — **plain classes** — so
  `node.get("type")` lowers to the opaque `get_N : … → int` and any `vt in ("Compare","BoolOp")`
  string dispatch is an `int↔string` clash (B1).

**Direct measurement (1 attempt / 0 conversions).** `types.py::_val_is_bool` — the *smallest*
non-recursive incidental clean-file trusted stub (a `@staticmethod` reading `.get("type")`/`.get("op")`
and string-dispatching): drop `\trusted` → `sync-mirror-bodies.py module6_whyml/types.py` (live body
ported, `val_ir: Dict[str,Any]`) → `--fun typeinferencemixin___val_is_bool` →
**`type string, but expected int` → FAILED**. Reverted; count 1240; `git diff` empty. This reproduces
the tier-5 census's **0/98** on this exact surface (`tier5-value-model-census.md`, `whole-body-census.md`).

Converting any clean-file incidental walker would require **retrofitting its whole mixin class to
`@mutable_state @dataclass`** (a per-FILE prerequisite with real corpus byte-diff risk — the gating
changes emitter behavior), and even then the census predicts B1 behind the tag reads (heterogeneous
value reads beyond the type/op tag). That is a value-model build, not a Track-R rewrite, and it fails
the §10.7 "value not count" calculus on measured yield.

## 4. R1' — accessor facade — NOT built (would be gold-plating)

`ir_kind`/`ir_get_str`/`ir_get_list`/`ir_children` are thin wrappers over the existing ADT
projections (`kind_of`, `name_of`/`value_of`, `args_of`, …). They are worth landing ONLY when an
incidental conversion consumes them (task: "Only build the accessors the actual incidental conversions
need — do not gold-plate"). With every R2 consumer blocked (§3), an unused facade is dead emitter code
and an unnecessary corpus-byte-diff risk. Deferred to a session where the baseline is green and at
least one consumer converts in the same commit.

## 5. Stop-loss (plan §6 Phase 4) — TRIGGERED

First batch: 1 clean attempt, 0 conversions (0% < 50%). Combined with the Phase-0 tier-5 census
(0/98 on the identical surface) the honest clean-conversion yield of the Track-R Phase-1 surface **as
currently gated is 0**. Per the campaign discipline, the residual stays `TRUSTED` — leaving stubs
trusted is sound and honest. No `TRUSTED(stop-loss, …)` reclassification of individual stubs is
recorded because **no stub changed classification** (all remain `\trusted` exactly as at HEAD; count
1240 unchanged).

## 6. The one actionable output — restore the mirror baseline BEFORE reopening Track-R Phase-1

The binding blocker is not the wall the plan targeted; it is the **RED baseline** (§1) on the two
ADT-capable files. Until `bin/run-self-annotation-suite.sh` is green again on `expressions.py` and
`statements.py`, **no** conversion in them (and no §10.4 re-port of a WL-touched method) can pass its
type-safety gate — this blocks R3, ADT-routed R2, and R1' alike. Restoring it means fixing the
`_class_constants` (value-type `option int`→`option string`) and `_handle_array_set_stmt` int↔string
leaks in the verified bodies — which is the **same B1 value-model gap** that defines the frontier, now
sitting *inside the meta-verifier's own gate*. That is a value-model repair (or a WL-series
re-examination under §10.4), not a Track-R rewrite. Recommended next move: **audit the WL-04f/05/06
mirror resyncs against §10.4** (were verified methods re-trusted or merged red?), restore the two
files to green, and only then re-attempt R3/R2 on a measured, census-confirmed candidate.

## 7. Ledger assertions (re-verifiable)

```
$ find src/self-annotate/src -name '*.py' -exec grep -h '\trusted' {} \; | wc -l
1240                                   # unchanged
$ git status --short src/pycsl src/self-annotate
(empty)                                # no emitter/mirror edit landed this session
$ bash bin/check-self-annotate-sync.sh
OK: all 90 un-trusted … verbatim copies  # fidelity green
```

- `\trusted` = **1240**, unchanged. 3-axiom ledger untouched; `proof_axiom_allowlist` (both copies)
  unchanged (no conversion, no feature).
- Deliverables this session are **docs only** (this file + the §8 ledger entry + the committed input
  plan `generic-dict-str-and-plan.md`). E-0 corpus byte-diff baseline (756 `.mlw`) built for the gate
  but not needed — no emitter change to diff.

## 8. Pointers
- Phase-0 verdict + census′: `getting-better/tier3/wall-plan-phase0.md`
- Tier-5 census (0/98): `getting-better/tier3/tier5-value-model-census.md`, `…/whole-body-census.md`
- Emission-defect / heterogeneous-tuple gap: `getting-better/tier3/emission-defect-spike-findings.md`
- ADT foundation: `preamble.py::_emit_exprir_theory`, `expressions.py::_KIND_DISCRIMINANT`
- Discipline: `config/skills/self-tcb-reduction/SKILL.md` §10 (esp. §10.4 re-port rule), §11;
  `…/leaf-conversion-recognizers.md` §7 (@mutable_state per-file prerequisite)
- Plan: `generic-dict-str-and-plan.md`
